"""
Repository for the ``contacts`` table.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Any, Dict, List, Optional
from uuid import UUID
import json

from db.base_repo import BaseRepository


class ContactsRepository(BaseRepository):
    table_name = "contacts"

    def _array_columns(self) -> set:
        return {"tags", "requirements", "research_areas"}

    async def list(
        self,
        session: AsyncSession,
        user_id: UUID,
        status: Optional[str] = None,
        contact_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """List contacts with optional status and type filters."""
        clauses = ["user_id = :user_id"]
        params: Dict[str, Any] = {
            "user_id": str(user_id),
            "limit": limit,
            "offset": offset,
        }

        if status:
            clauses.append("status = :status")
            params["status"] = status
        if contact_type:
            clauses.append("contact_type = :contact_type")
            params["contact_type"] = contact_type

        where = " AND ".join(clauses)
        query = text(
            f"SELECT * FROM contacts WHERE {where} "
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
        """Create a new contact."""
        data["user_id"] = str(user_id)

        # Serialize JSONB columns
        for col in ("metadata", "publications"):
            if col in data and isinstance(data[col], (dict, list)):
                data[col] = json.dumps(data[col])

        # Handle list-to-ARRAY conversion for text[] columns
        for col in ("tags", "research_areas"):
            if col in data and isinstance(data[col], list):
                # asyncpg handles Python lists as PostgreSQL arrays natively
                pass

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        columns = ", ".join(data.keys())
        placeholders = ", ".join(f":{k}" for k in data.keys())

        query = text(
            f"INSERT INTO contacts ({columns}) VALUES ({placeholders}) RETURNING *"
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
        """Update a contact."""
        for col in ("metadata", "publications"):
            if col in data and isinstance(data[col], (dict, list)):
                data[col] = json.dumps(data[col])
        return await super().update(session, record_id, data)

    async def search_by_tag(
        self,
        session: AsyncSession,
        user_id: UUID,
        tag: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search contacts that have a specific tag."""
        query = text(
            "SELECT * FROM contacts "
            "WHERE user_id = :user_id AND :tag = ANY(tags) "
            "ORDER BY created_at DESC LIMIT :limit"
        )
        result = await session.execute(
            query, {"user_id": str(user_id), "tag": tag, "limit": limit}
        )
        return [dict(row) for row in result.mappings().all()]

    async def count_by_status(
        self,
        session: AsyncSession,
        user_id: UUID,
    ) -> Dict[str, int]:
        """Get count of contacts grouped by status."""
        query = text(
            "SELECT status, COUNT(*) as count FROM contacts "
            "WHERE user_id = :user_id GROUP BY status"
        )
        result = await session.execute(query, {"user_id": str(user_id)})
        return {row["status"]: row["count"] for row in result.mappings().all()}


contacts_repo = ContactsRepository()
