"""
Token migration script.

Per MIGRATION_ROLLOUT_PLAN.md §Data Migration — Step 3: Token Migration:
  Encrypt existing LinkedIn tokens and remove plaintext versions.

Usage:
  python scripts/migrate_tokens.py
"""
import asyncio
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def migrate_tokens():
    """Encrypt all plaintext tokens in the database."""
    from db.session import get_sessionmaker
    from security.encryption import encrypt_token
    from sqlalchemy import text

    sessionmaker = get_sessionmaker()

    async with sessionmaker() as session:
        # Check for users with plaintext tokens in settings
        result = await session.execute(
            text(
                "SELECT id, settings FROM users "
                "WHERE settings IS NOT NULL "
                "AND settings::text LIKE '%linkedin_token%'"
            )
        )
        users = result.mappings().all()

        logger.info(f"Found {len(users)} users with potential plaintext tokens")

        migrated = 0
        for user in users:
            try:
                import json
                user_settings = json.loads(user["settings"]) if isinstance(user["settings"], str) else user["settings"]

                # Check for plaintext LinkedIn token
                linkedin_token = user_settings.get("linkedin_token", "")
                if linkedin_token and not linkedin_token.startswith("gAAAAA"):
                    # Not already encrypted (Fernet tokens start with gAAAAA)
                    encrypted = encrypt_token(linkedin_token)
                    user_settings["linkedin_token"] = encrypted
                    user_settings["token_encrypted"] = True

                    await session.execute(
                        text("UPDATE users SET settings = :settings WHERE id = :id"),
                        {"settings": json.dumps(user_settings), "id": str(user["id"])},
                    )
                    migrated += 1
                    logger.info(f"  Encrypted token for user {user['id']}")

            except Exception as e:
                logger.warning(f"  Failed to migrate token for user {user['id']}: {e}")

        await session.commit()
        logger.info(f"Migration complete! {migrated} tokens encrypted.")


if __name__ == "__main__":
    asyncio.run(migrate_tokens())
