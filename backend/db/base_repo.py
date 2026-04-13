"""
Generic async repository base class.

Uses raw SQL via SQLAlchemy `text()` so we don't need ORM mapper classes —
the existing Pydantic models + raw SQL schema in setup_db.sql are sufficient.
All methods return plain dicts for easy JSON serialization.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime, timezone


class BaseRepository:
    """
    Generic CRUD repository for a single PostgreSQL table.

    Subclasses set ``table_name`` and optionally override methods
    for custom filtering or joins.
    """

    table_name: str = ""

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    async def get(self, session: AsyncSession, record_id: UUID) -> Optional[Dict[str, Any]]:
        """Fetch a single record by primary key."""
        query = text(f"SELECT * FROM {self.table_name} WHERE id = :id")
        result = await session.execute(query, {"id": str(record_id)})
        row = result.mappings().first()
        return dict(row) if row else None

    async def list(
        self,
        session: AsyncSession,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
        **filters: Any,
    ) -> List[Dict[str, Any]]:
        """
        List records for a given user with optional filters.
        Subclasses should override for custom filter logic.
        """
        clauses = ["user_id = :user_id"]
        params: Dict[str, Any] = {"user_id": str(user_id), "limit": limit, "offset": offset}

        for key, value in filters.items():
            if value is not None:
                clauses.append(f"{key} = :{key}")
                params[key] = value if not isinstance(value, UUID) else str(value)

        where = " AND ".join(clauses)
        query = text(
            f"SELECT * FROM {self.table_name} "
            f"WHERE {where} "
            f"ORDER BY created_at DESC "
            f"LIMIT :limit OFFSET :offset"
        )
        result = await session.execute(query, params)
        return [dict(row) for row in result.mappings().all()]

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------
    async def create(
        self,
        session: AsyncSession,
        user_id: UUID,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Insert a new record and return it."""
        data = {k: v for k, v in data.items() if v is not None}
        data["user_id"] = str(user_id)

        # Serialize complex types for JSONB / array columns
        for key, value in data.items():
            if isinstance(value, UUID):
                data[key] = str(value)
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, list) and key not in self._array_columns():
                # Assume JSONB — leave as is (asyncpg handles dicts/lists)
                pass

        columns = ", ".join(data.keys())
        placeholders = ", ".join(f":{k}" for k in data.keys())

        query = text(
            f"INSERT INTO {self.table_name} ({columns}) "
            f"VALUES ({placeholders}) "
            f"RETURNING *"
        )
        result = await session.execute(query, data)
        row = result.mappings().first()
        return dict(row) if row else data

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    async def update(
        self,
        session: AsyncSession,
        record_id: UUID,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a record by ID and return the updated row."""
        data = {k: v for k, v in data.items() if v is not None}
        if not data:
            existing = await self.get(session, record_id)
            return existing or {}

        # Serialize
        for key, value in list(data.items()):
            if isinstance(value, UUID):
                data[key] = str(value)
            elif isinstance(value, datetime):
                data[key] = value.isoformat()

        set_clause = ", ".join(f"{k} = :{k}" for k in data.keys())
        data["id"] = str(record_id)

        query = text(
            f"UPDATE {self.table_name} SET {set_clause} WHERE id = :id RETURNING *"
        )
        result = await session.execute(query, data)
        row = result.mappings().first()
        return dict(row) if row else {}

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    async def delete(self, session: AsyncSession, record_id: UUID) -> bool:
        """Delete a record by ID. Returns True if deleted."""
        query = text(f"DELETE FROM {self.table_name} WHERE id = :id")
        result = await session.execute(query, {"id": str(record_id)})
        return result.rowcount > 0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _array_columns(self) -> set:
        """
        Override in subclasses to list columns that are PostgreSQL ARRAY type
        (vs JSONB). This affects serialization.
        """
        return set()
