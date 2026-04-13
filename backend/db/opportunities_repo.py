"""
Repository for the ``opportunities`` table.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Any, Dict, List, Optional
from uuid import UUID
import json

from db.base_repo import BaseRepository


class OpportunitiesRepository(BaseRepository):
    table_name = "opportunities"

    def _array_columns(self) -> set:
        return {"requirements"}

    async def list(
        self,
        session: AsyncSession,
        user_id: UUID,
        status: Optional[str] = None,
        opportunity_type: Optional[str] = None,
        min_match_score: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """List opportunities with optional filters."""
        clauses = ["user_id = :user_id"]
        params: Dict[str, Any] = {
            "user_id": str(user_id),
            "limit": limit,
            "offset": offset,
        }

        if status:
            clauses.append("status = :status")
            params["status"] = status
        if opportunity_type:
            clauses.append("opportunity_type = :opportunity_type")
            params["opportunity_type"] = opportunity_type
        if min_match_score is not None:
            clauses.append("match_score >= :min_match_score")
            params["min_match_score"] = min_match_score

        where = " AND ".join(clauses)
        query = text(
            f"SELECT * FROM opportunities WHERE {where} "
            f"ORDER BY match_score DESC, discovered_at DESC "
            f"LIMIT :limit OFFSET :offset"
        )
        result = await session.execute(query, params)
        return [dict(row) for row in result.mappings().all()]

    async def create(
        self,
        session: AsyncSession,
        user_id: UUID,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new opportunity."""
        data["user_id"] = str(user_id)

        if "metadata" in data and isinstance(data["metadata"], dict):
            data["metadata"] = json.dumps(data["metadata"])

        data = {k: v for k, v in data.items() if v is not None}

        columns = ", ".join(data.keys())
        placeholders = ", ".join(f":{k}" for k in data.keys())

        query = text(
            f"INSERT INTO opportunities ({columns}) VALUES ({placeholders}) RETURNING *"
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
        """Update an opportunity."""
        if "metadata" in data and isinstance(data["metadata"], dict):
            data["metadata"] = json.dumps(data["metadata"])
        return await super().update(session, record_id, data)


opportunities_repo = OpportunitiesRepository()
