"""
Repository for the ``messages`` table.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Any, Dict, List, Optional
from uuid import UUID
import json

from db.base_repo import BaseRepository


class MessagesRepository(BaseRepository):
    table_name = "messages"

    async def list(
        self,
        session: AsyncSession,
        user_id: UUID,
        status: Optional[str] = None,
        contact_id: Optional[UUID] = None,
        campaign_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """List messages with optional filters."""
        clauses = ["user_id = :user_id"]
        params: Dict[str, Any] = {
            "user_id": str(user_id),
            "limit": limit,
            "offset": offset,
        }

        if status:
            clauses.append("status = :status")
            params["status"] = status
        if contact_id:
            clauses.append("contact_id = :contact_id")
            params["contact_id"] = str(contact_id)
        if campaign_id:
            clauses.append("campaign_id = :campaign_id")
            params["campaign_id"] = str(campaign_id)

        where = " AND ".join(clauses)
        query = text(
            f"SELECT * FROM messages WHERE {where} "
            f"ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        )
        result = await session.execute(query, params)
        return [dict(row) for row in result.mappings().all()]

    async def create(
        self,
        session: AsyncSession,
        user_id: UUID,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new message."""
        data["user_id"] = str(user_id)

        # Serialize JSONB and UUID columns
        if "metadata" in data and isinstance(data["metadata"], dict):
            data["metadata"] = json.dumps(data["metadata"])
        for col in ("contact_id", "campaign_id"):
            if col in data and isinstance(data[col], UUID):
                data[col] = str(data[col])

        data = {k: v for k, v in data.items() if v is not None}

        columns = ", ".join(data.keys())
        placeholders = ", ".join(f":{k}" for k in data.keys())

        query = text(
            f"INSERT INTO messages ({columns}) VALUES ({placeholders}) RETURNING *"
        )
        result = await session.execute(query, data)
        row = result.mappings().first()
        return dict(row) if row else data

    async def update(
        self,
        session: AsyncSession,
        record_id: UUID,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a message."""
        if "metadata" in data and isinstance(data["metadata"], dict):
            data["metadata"] = json.dumps(data["metadata"])
        return await super().update(session, record_id, data)

    async def get_pending_drafts(
        self,
        session: AsyncSession,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Get pending message drafts with contact info (for approval UI).
        Matches API_CONTRACTS.md GET /messages/pending.
        """
        query = text(
            "SELECT m.*, "
            "c.name as contact_name, c.title as contact_title, "
            "c.company as contact_company, c.linkedin_url as contact_linkedin, "
            "c.email as contact_email "
            "FROM messages m "
            "LEFT JOIN contacts c ON m.contact_id = c.id "
            "WHERE m.user_id = :user_id AND m.status = 'draft' "
            "ORDER BY m.created_at DESC "
            "LIMIT :limit OFFSET :offset"
        )
        result = await session.execute(
            query, {"user_id": str(user_id), "limit": limit, "offset": offset}
        )
        rows = result.mappings().all()

        # Shape into the API_CONTRACTS format
        drafts = []
        for row in rows:
            row_dict = dict(row)
            drafts.append({
                "id": row_dict["id"],
                "contact": {
                    "id": row_dict.get("contact_id"),
                    "name": row_dict.get("contact_name"),
                    "title": row_dict.get("contact_title"),
                    "company": row_dict.get("contact_company"),
                    "linkedin_url": row_dict.get("contact_linkedin"),
                    "email": row_dict.get("contact_email"),
                },
                "message": {
                    "subject": row_dict.get("subject"),
                    "body": row_dict.get("body"),
                    "preview": (row_dict.get("body") or "")[:120],
                },
                "quality_score": row_dict.get("personalization_score", 0),
                "personalization_score": row_dict.get("personalization_score", 0),
                "generated_at": row_dict.get("created_at"),
                "status": row_dict.get("status"),
            })
        return drafts

    async def bulk_update_status(
        self,
        session: AsyncSession,
        message_ids: List[str],
        new_status: str,
    ) -> int:
        """Bulk update status for multiple messages."""
        if not message_ids:
            return 0
        # Build parameterized IN clause
        id_params = {f"id_{i}": mid for i, mid in enumerate(message_ids)}
        in_clause = ", ".join(f":id_{i}" for i in range(len(message_ids)))
        query = text(
            f"UPDATE messages SET status = :status "
            f"WHERE id IN ({in_clause})"
        )
        params = {"status": new_status, **id_params}
        result = await session.execute(query, params)
        return result.rowcount

    async def count_by_status(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> Dict[str, int]:
        """Count messages grouped by status."""
        query = text(
            "SELECT status, COUNT(*) as count FROM messages "
            "WHERE user_id = :user_id GROUP BY status"
        )
        result = await session.execute(query, {"user_id": str(user_id)})
        return {row["status"]: row["count"] for row in result.mappings().all()}

    async def count_sent_today(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> int:
        """Count messages sent today (for rate limiting display)."""
        query = text(
            "SELECT COUNT(*) as count FROM messages "
            "WHERE user_id = :user_id AND status IN ('sent', 'opened', 'replied') "
            "AND sent_at >= CURRENT_DATE"
        )
        result = await session.execute(query, {"user_id": str(user_id)})
        row = result.mappings().first()
        return row["count"] if row else 0

    async def mark_sent_if_approved(
        self,
        session: AsyncSession,
        message_id: UUID,
        sent_at: Any = None,
    ) -> Dict[str, Any]:
        """
        Atomically mark a message as 'sent' only if its current status is 'approved'.
        Used by the send_approved_messages scheduled task.
        """
        from datetime import datetime, timezone

        if sent_at is None:
            sent_at = datetime.now(timezone.utc)

        query = text(
            "UPDATE messages SET status = 'sent', sent_at = :sent_at "
            "WHERE id = :id AND status = 'approved' "
            "RETURNING *"
        )
        result = await session.execute(
            query, {"id": str(message_id), "sent_at": sent_at.isoformat()}
        )
        row = result.mappings().first()
        return dict(row) if row else {}


messages_repo = MessagesRepository()

