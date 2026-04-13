"""
Repository for the ``agent_insights`` table.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Any, Dict, List, Optional
from uuid import UUID
import json

from db.base_repo import BaseRepository


class InsightsRepository(BaseRepository):
    table_name = "agent_insights"

    def _array_columns(self) -> set:
        return {"action_items"}

    async def list(
        self,
        session: AsyncSession,
        user_id: UUID,
        status: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """List insights ordered by priority and recency."""
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
            f"SELECT * FROM agent_insights WHERE {where} "
            f"ORDER BY "
            f"CASE priority "
            f"  WHEN 'critical' THEN 1 "
            f"  WHEN 'high' THEN 2 "
            f"  WHEN 'medium' THEN 3 "
            f"  WHEN 'low' THEN 4 "
            f"  ELSE 5 END, "
            f"created_at DESC "
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
        """Create a new insight."""
        data["user_id"] = str(user_id)

        if "metadata" in data and isinstance(data["metadata"], dict):
            data["metadata"] = json.dumps(data["metadata"])

        data = {k: v for k, v in data.items() if v is not None}

        columns = ", ".join(data.keys())
        placeholders = ", ".join(f":{k}" for k in data.keys())

        query = text(
            f"INSERT INTO agent_insights ({columns}) VALUES ({placeholders}) RETURNING *"
        )
        result = await session.execute(query, data)
        row = result.mappings().first()
        return dict(row) if row else data

    async def mark_read(
        self,
        session: AsyncSession,
        insight_id: UUID,
    ) -> Dict[str, Any]:
        """Mark an insight as read."""
        return await self.update(session, insight_id, {"status": "read"})


insights_repo = InsightsRepository()
