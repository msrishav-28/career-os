"""
Repository for the ``users`` table.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Any, Dict, Optional
from uuid import UUID
import json

from db.base_repo import BaseRepository


class UsersRepository(BaseRepository):
    table_name = "users"

    async def get_by_id(self, session: AsyncSession, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        return await self.get(session, user_id)

    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[Dict[str, Any]]:
        """Look up a user by email address."""
        query = text("SELECT * FROM users WHERE email = :email")
        result = await session.execute(query, {"email": email})
        row = result.mappings().first()
        return dict(row) if row else None

    async def create(
        self,
        session: AsyncSession,
        user_id: UUID = None,  # type: ignore[override]
        data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Create a new user.

        Accepts either:
          - create(session, data={"email": ..., "hashed_password": ...})
          - create(session, user_id, data)  (user_id ignored; auto-generated)
        """
        if data is None:
            data = {}
        # Serialize nested dicts for JSONB columns
        for col in ("profile_data", "settings"):
            if col in data and isinstance(data[col], dict):
                data[col] = json.dumps(data[col])

        columns = ", ".join(data.keys())
        placeholders = ", ".join(f":{k}" for k in data.keys())

        query = text(
            f"INSERT INTO users ({columns}) VALUES ({placeholders}) RETURNING *"
        )
        result = await session.execute(query, data)
        row = result.mappings().first()
        return dict(row) if row else data

    async def update(
        self,
        session: AsyncSession,
        user_id: UUID,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update user record."""
        # Serialize JSONB columns
        for col in ("profile_data", "settings"):
            if col in data and isinstance(data[col], dict):
                data[col] = json.dumps(data[col])
        return await super().update(session, user_id, data)


users_repo = UsersRepository()
