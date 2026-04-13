"""
Authentication API routes.

Implements the authentication endpoints from API_CONTRACTS.md:
  - POST /auth/login
  - POST /auth/register
  - POST /auth/refresh
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timezone

from db.session import get_db_session
from db import users_repo
from auth.jwt import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class RefreshRequest(BaseModel):
    refresh_token: str


class AuthResponse(BaseModel):
    success: bool
    data: dict


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Authenticate user and receive access + refresh tokens.

    Per API_CONTRACTS.md §1: POST /auth/login
    """
    user = await users_repo.get_by_email(session, body.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password (stored in user record or separate auth table)
    stored_hash = user.get("hashed_password", "")
    if not stored_hash or not verify_password(body.password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create tokens
    token_data = {"sub": str(user["id"]), "email": user["email"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "success": True,
        "data": {
            "user": {
                "id": str(user["id"]),
                "email": user["email"],
                "name": (user.get("profile_data") or {}).get("name", ""),
            },
            "session": {
                "token": access_token,
                "refresh_token": refresh_token,
                "expires_at": (
                    datetime.now(timezone.utc).isoformat()
                ),
            },
        },
    }


@router.post("/register", response_model=AuthResponse)
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """
    Create a new user account.
    """
    # Check if email already exists
    existing = await users_repo.get_by_email(session, body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash password and create user
    hashed = hash_password(body.password)
    user = await users_repo.create(
        session,
        data={
            "email": body.email,
            "hashed_password": hashed,
        },
    )

    # Create tokens
    token_data = {"sub": str(user["id"]), "email": user["email"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "success": True,
        "data": {
            "user": {
                "id": str(user["id"]),
                "email": user["email"],
                "name": body.name or "",
            },
            "session": {
                "token": access_token,
                "refresh_token": refresh_token,
                "expires_at": datetime.now(timezone.utc).isoformat(),
            },
        },
    }


@router.post("/refresh", response_model=AuthResponse)
async def refresh(body: RefreshRequest):
    """
    Refresh access token using a valid refresh token.

    Per API_CONTRACTS.md §1: POST /auth/refresh
    """
    payload = verify_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    token_data = {"sub": payload["sub"], "email": payload.get("email", "")}
    new_access_token = create_access_token(token_data)

    return {
        "success": True,
        "data": {
            "token": new_access_token,
            "expires_at": datetime.now(timezone.utc).isoformat(),
        },
    }
