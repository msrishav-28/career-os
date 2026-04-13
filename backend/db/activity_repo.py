"""
Repository for the ``activity_log`` table.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime, timezone
import json

from db.base_repo import BaseRepository


class ActivityRepository(BaseRepository):
    table_name = "activity_log"

    async def log(
        self,
        session: AsyncSession,
        user_id: UUID,
        action_type: str,
        platform: Optional[str] = None,
        success: bool = True,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Log a user or system activity."""
        data: Dict[str, Any] = {
            "user_id": str(user_id),
            "action_type": action_type,
            "success": success,
        }
        if platform:
            data["platform"] = platform
        if metadata:
            data["metadata"] = json.dumps(metadata)

        columns = ", ".join(data.keys())
        placeholders = ", ".join(f":{k}" for k in data.keys())

        query = text(
            f"INSERT INTO activity_log ({columns}) VALUES ({placeholders}) RETURNING *"
        )
        result = await session.execute(query, data)
        row = result.mappings().first()
        return dict(row) if row else data

    async def list(
        self,
        session: AsyncSession,
        user_id: UUID,
        action_type: Optional[str] = None,
        days: int = 30,
        limit: int = 100,
        offset: int = 0,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """List activity logs with optional action_type filter."""
        clauses = [
            "user_id = :user_id",
            "created_at >= NOW() - INTERVAL ':days days'",
        ]
        params: Dict[str, Any] = {
            "user_id": str(user_id),
            "days": days,
            "limit": limit,
            "offset": offset,
        }

        if action_type:
            clauses.append("action_type = :action_type")
            params["action_type"] = action_type

        where = " AND ".join(clauses)
        query = text(
            f"SELECT * FROM activity_log WHERE {where} "
            f"ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        )
        result = await session.execute(query, params)
        return [dict(row) for row in result.mappings().all()]

    async def count_actions(
        self,
        session: AsyncSession,
        user_id: UUID,
        action_type: str,
        days: int = 1,
    ) -> int:
        """Count actions of a specific type within a time window."""
        query = text(
            "SELECT COUNT(*) as count FROM activity_log "
            "WHERE user_id = :user_id AND action_type = :action_type "
            "AND created_at >= NOW() - make_interval(days => :days)"
        )
        result = await session.execute(
            query,
            {"user_id": str(user_id), "action_type": action_type, "days": days},
        )
        row = result.mappings().first()
        return row["count"] if row else 0


activity_repo = ActivityRepository()
