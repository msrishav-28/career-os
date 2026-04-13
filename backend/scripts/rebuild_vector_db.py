"""
Rebuild Vector DB from PostgreSQL.

Per OPERATIONAL_RUNBOOK.md §Backup & Recovery:
  python scripts/rebuild_vector_db.py

Re-generates all embeddings from PostgreSQL data.
Takes ~10 minutes for 1000 contacts.
"""
import asyncio
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def rebuild_vector_db():
    """Rebuild Vector DB from PostgreSQL data."""
    from db.session import get_sessionmaker
    from db import contacts_repo
    from services.vector_service import vector_service
    from services.sync_service import SyncService
    from sqlalchemy import text

    sync = SyncService()
    sessionmaker = get_sessionmaker()

    async with sessionmaker() as session:
        # Get all users
        result = await session.execute(text("SELECT id FROM users"))
        users = [row["id"] for row in result.mappings().all()]

        logger.info(f"Rebuilding Vector DB for {len(users)} users...")

        total_contacts = 0

        for user_id in users:
            contacts = await contacts_repo.list(session, user_id, limit=10000)
            logger.info(f"User {user_id}: {len(contacts)} contacts to rebuild")

            for i, contact in enumerate(contacts):
                try:
                    contact_text = sync._build_contact_text(contact)
                    vector_service.store_network_insight(
                        str(user_id),
                        contact_text,
                        {
                            "type": "contact",
                            "contact_id": str(contact["id"]),
                            "name": contact.get("name", ""),
                            "company": contact.get("company", ""),
                            "source": "rebuild",
                        },
                    )
                    total_contacts += 1

                    if (i + 1) % 100 == 0:
                        logger.info(f"  Progress: {i + 1}/{len(contacts)}")
                except Exception as e:
                    logger.warning(f"  Failed to rebuild contact {contact.get('id')}: {e}")

        logger.info(f"Rebuild complete! {total_contacts} contacts embedded.")


if __name__ == "__main__":
    asyncio.run(rebuild_vector_db())
