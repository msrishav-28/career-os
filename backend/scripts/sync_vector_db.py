"""
Sync Vector DB from PostgreSQL.

Per OPERATIONAL_RUNBOOK.md §5 — Vector DB Out of Sync:
  python scripts/sync_vector_db.py

Ensures all contacts in PostgreSQL have corresponding
embeddings in Vector DB. Removes orphaned Vector DB entries.
"""
import asyncio
import sys
import os
import logging

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def sync_vector_db():
    """Run full sync between PostgreSQL and Vector DB."""
    from db.session import get_sessionmaker
    from db import contacts_repo, users_repo
    from services.sync_service import sync_service
    from sqlalchemy import text

    sessionmaker = get_sessionmaker()

    async with sessionmaker() as session:
        # Get all users
        result = await session.execute(text("SELECT id FROM users"))
        users = [row["id"] for row in result.mappings().all()]

        logger.info(f"Found {len(users)} users to sync")

        for user_id in users:
            logger.info(f"Syncing user {user_id}...")

            # Detect drift
            drift = await sync_service.detect_drift(session, user_id)
            logger.info(f"  Postgres contacts: {drift.get('postgres_count', 0)}")
            logger.info(f"  Vector DB contacts: {drift.get('vector_db_count', 0)}")

            if drift.get("orphaned_in_vector_db"):
                logger.warning(
                    f"  Orphaned in Vector DB: {len(drift['orphaned_in_vector_db'])}"
                )
                # Clean up orphaned entries
                from services.vector_service import vector_service
                collection = chroma_service.network_collection
                if collection:
                    for cid in drift["orphaned_in_chromadb"]:
                        try:
                            results = collection.get(where={"contact_id": cid})
                            if results and results.get("ids"):
                                vector_service.delete_documents(f"network_knowledge_{user_id}", [cid]) # Fallback delete
                                logger.info(f"  Cleaned orphan: {cid}")
                        except Exception as e:
                            logger.warning(f"  Failed to clean orphan {cid}: {e}")

            if drift.get("missing_in_vector_db"):
                logger.warning(
                    f"  Missing in Vector DB: {len(drift['missing_in_vector_db'])}"
                )
                # Re-sync missing contacts
                for cid in drift["missing_in_vector_db"]:
                    try:
                        from uuid import UUID
                        contact = await contacts_repo.get(session, UUID(cid))
                        if contact:
                            await sync_service.sync_contact_create(
                                session, user_id, contact
                            )
                            logger.info(f"  Re-synced contact: {cid}")
                    except Exception as e:
                        logger.warning(f"  Failed to re-sync {cid}: {e}")

            if drift.get("in_sync"):
                logger.info(f"  ✓ User {user_id} is in sync")

    logger.info("Sync complete!")


if __name__ == "__main__":
    asyncio.run(sync_vector_db())
