"""
Repository for the ``campaigns`` table.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Any, Dict, List, Optional
from uuid import UUID
import json

from db.base_repo import BaseRepository


class CampaignsRepository(BaseRepository):
    table_name = "campaigns"

    async def list(
        self,
        session: AsyncSession,
        user_id: UUID,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """List campaigns with optional status filter."""
        clauses = ["user_id = :user_id"]
        params: Dict[str, Any] = {
            "user_id": str(user_id),
            "limit": limit,
            "offset": offset,
        }

        if status:
            clauses.append("status = :status")
            params["status"] = status

        where = " AND ".join(clauses)
        query = text(
            f"SELECT * FROM campaigns WHERE {where} "
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
        """Create a new campaign."""
        data["user_id"] = str(user_id)

        if "metadata" in data and isinstance(data["metadata"], dict):
            data["metadata"] = json.dumps(data["metadata"])

        data = {k: v for k, v in data.items() if v is not None}

        columns = ", ".join(data.keys())
        placeholders = ", ".join(f":{k}" for k in data.keys())

        query = text(
            f"INSERT INTO campaigns ({columns}) VALUES ({placeholders}) RETURNING *"
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
        """Update a campaign."""
        if "metadata" in data and isinstance(data["metadata"], dict):
            data["metadata"] = json.dumps(data["metadata"])
        return await super().update(session, record_id, data)


campaigns_repo = CampaignsRepository()
