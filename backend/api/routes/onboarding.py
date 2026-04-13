"""
Onboarding API routes.

Implements the Onboarding Flow from API_CONTRACTS.md §3:
  - POST /onboarding/resume          — Upload resume for parsing
  - GET  /onboarding/resume/{id}/status — Check parsing status
  - POST /onboarding/objectives      — Set user objectives
  - POST /onboarding/simulate        — Run simulation preview

Also supports the "Calibration Chamber" UX from ELITE_REDESIGN_MASTER_PLAN.md §6.2.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
import json
from datetime import datetime, timezone

from db.session import get_db_session
from db import users_repo, contacts_repo
from auth import get_current_user, CurrentUser
from services.redis_service import redis_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class ObjectivesRequest(BaseModel):
    """User objectives and preferences per API_CONTRACTS.md."""
    target_roles: List[str] = []
    target_companies: List[str] = []
    locations: List[str] = []
    exclusions: Optional[Dict] = None  # {"companies": [...], "keywords": [...]}


class SimulationResponse(BaseModel):
    success: bool
    data: dict


# ---------------------------------------------------------------------------
# In-memory upload status tracking (Redis-backed)
# ---------------------------------------------------------------------------
def _upload_key(upload_id: str) -> str:
    return f"careeros:onboarding:upload:{upload_id}"


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Upload resume for parsing.

    Per API_CONTRACTS.md §3: POST /onboarding/resume
    Accepts multipart form data with file upload.
    """
    # Validate file type
    allowed_types = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    }

    content_type = file.content_type or ""
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_FILE_TYPE",
                    "message": f"Unsupported file type: {content_type}. Use PDF, DOCX, or TXT.",
                },
            },
        )

    # Read file content
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": {
                    "code": "FILE_TOO_LARGE",
                    "message": "File must be under 10MB.",
                },
            },
        )

    upload_id = str(uuid.uuid4())

    # Store upload status in Redis
    redis_service.set_json(
        _upload_key(upload_id),
        {
            "status": "processing",
            "user_id": current_user["id"],
            "filename": file.filename,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "extracted_data": None,
        },
        expiry=3600,  # 1 hour TTL
    )

    # Trigger async parsing
    # In production, this would send to Celery:
    #   from tasks.agent_tasks import parse_resume_task
    #   parse_resume_task.delay(upload_id, content)
    #
    # For now, we do a lightweight extraction inline.
    _extract_resume_data(upload_id, content, file.filename or "resume")

    return {
        "success": True,
        "data": {
            "upload_id": upload_id,
            "status": "processing",
        },
    }


@router.get("/resume/{upload_id}/status")
async def get_resume_status(
    upload_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Check resume parsing status.

    Per API_CONTRACTS.md §3: GET /onboarding/resume/{upload_id}/status
    """
    data = redis_service.get_json(_upload_key(upload_id))
    if not data:
        raise HTTPException(status_code=404, detail="Upload not found or expired")

    # Verify ownership
    if data.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")

    return {
        "success": True,
        "data": {
            "status": data["status"],
            "extracted_data": data.get("extracted_data"),
        },
    }


@router.post("/objectives")
async def set_objectives(
    objectives: ObjectivesRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Set user objectives and preferences.

    Per API_CONTRACTS.md §3: POST /onboarding/objectives
    Saves target roles, companies, locations, and exclusions.
    """
    try:
        # Update user settings with objectives
        await users_repo.update(
            session,
            uuid.UUID(current_user["id"]),
            {
                "settings": json.dumps({
                    "target_roles": objectives.target_roles,
                    "target_companies": objectives.target_companies,
                    "locations": objectives.locations,
                    "exclusions": objectives.exclusions or {},
                    "onboarding_completed_at": datetime.now(timezone.utc).isoformat(),
                }),
            },
        )

        return {
            "success": True,
            "data": {"objectives_saved": True},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate")
async def run_simulation(
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Run simulation to estimate matches.

    Per API_CONTRACTS.md §3: POST /onboarding/simulate
    Provides a preview of what the system will find.
    """
    try:
        uid = uuid.UUID(current_user["id"])

        # Get user's existing profile/settings for context
        user = await users_repo.get_by_id(session, uid)
        user_settings = user.get("settings") if user else {}
        if isinstance(user_settings, str):
            user_settings = json.loads(user_settings)

        # Get existing contacts for baseline
        existing_contacts = await contacts_repo.list(session, uid, limit=5)

        # Build simulation response
        # In production this would use the DiscoveryCrew to estimate
        sample_contacts = []
        for c in existing_contacts[:3]:
            sample_contacts.append({
                "name": c.get("name", ""),
                "title": c.get("title", ""),
                "company": c.get("company", ""),
            })

        # Estimate based on target companies/roles
        target_companies = (user_settings or {}).get("target_companies", [])
        target_roles = (user_settings or {}).get("target_roles", [])
        estimated_matches = max(50, len(target_companies) * 30 + len(target_roles) * 20)

        return {
            "success": True,
            "data": {
                "estimated_matches": estimated_matches,
                "sample_contacts": sample_contacts,
                "confidence": "high" if target_companies and target_roles else "medium",
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _extract_resume_data(upload_id: str, content: bytes, filename: str):
    """
    Lightweight resume data extraction.

    In production, delegate to an AI agent via Celery.
    For now, mark as complete with placeholder extraction.
    """
    try:
        # Attempt basic text extraction
        text_content = ""
        try:
            text_content = content.decode("utf-8", errors="ignore")
        except Exception:
            pass

        # Basic extraction heuristics
        extracted = {
            "name": "",
            "email": "",
            "skills": [],
            "experience": [],
            "education": [],
        }

        # Extract email-like patterns
        import re
        email_pattern = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
        emails = email_pattern.findall(text_content)
        if emails:
            extracted["email"] = emails[0]

        # Common tech skills detection
        skill_keywords = [
            "Python", "JavaScript", "TypeScript", "React", "Node.js",
            "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow",
            "SQL", "PostgreSQL", "MongoDB", "Docker", "Kubernetes",
            "AWS", "GCP", "Azure", "FastAPI", "Django", "Flask",
            "Java", "C++", "Rust", "Go", "Swift",
        ]
        for skill in skill_keywords:
            if skill.lower() in text_content.lower():
                extracted["skills"].append(skill)

        # Update Redis with results
        redis_service.set_json(
            _upload_key(upload_id),
            {
                "status": "complete",
                "extracted_data": extracted,
            },
            expiry=3600,
        )
    except Exception:
        redis_service.set_json(
            _upload_key(upload_id),
            {"status": "failed", "extracted_data": None},
            expiry=3600,
        )
