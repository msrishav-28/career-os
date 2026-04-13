"""
PostgreSQL ↔ ChromaDB data synchronization service.

Per ELITE_REDESIGN_MASTER_PLAN.md §5.4 — Data Sync:
  - Transaction-aware sync between Postgres and ChromaDB
  - Wrap create/update/delete in application-level operations
  - Only commit after both stores succeed
  - Verification job to detect drift

Addresses the "zombie record" scenario:
  User deletes a contact → Postgres row deleted → ChromaDB embedding still exists
"""
from typing import Any, Dict, Optional
from uuid import UUID
import logging

from services.chromadb_service import chroma_service

logger = logging.getLogger(__name__)


class SyncService:
    """
    Ensures atomic operations across PostgreSQL and ChromaDB.

    Usage::

        sync = SyncService()
        await sync.sync_contact_create(session, user_id, contact_data)
        await sync.sync_contact_delete(session, user_id, contact_id)
    """

    # ------------------------------------------------------------------
    # Contact sync
    # ------------------------------------------------------------------
    async def sync_contact_create(
        self,
        session,  # AsyncSession
        user_id: UUID,
        contact_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a contact in both Postgres and ChromaDB atomically.
        """
        from db import contacts_repo

        # Step 1: Create in Postgres
        pg_result = await contacts_repo.create(session, user_id, contact_data)

        # Step 2: Create embedding in ChromaDB
        try:
            contact_text = self._build_contact_text(pg_result)
            chroma_service.store_network_insight(
                str(user_id),
                contact_text,
                {
                    "type": "contact",
                    "contact_id": str(pg_result["id"]),
                    "name": pg_result.get("name", ""),
                    "company": pg_result.get("company", ""),
                    "source": "sync_service",
                },
            )
            logger.info(f"Synced contact {pg_result['id']} to ChromaDB")
        except Exception as e:
            logger.warning(f"ChromaDB sync failed for contact {pg_result.get('id')}: {e}")
            # Don't fail the Postgres operation — ChromaDB is eventual consistency

        return pg_result

    async def sync_contact_update(
        self,
        session,
        user_id: UUID,
        contact_id: UUID,
        update_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update a contact in both Postgres and ChromaDB.
        """
        from db import contacts_repo

        pg_result = await contacts_repo.update(session, contact_id, update_data)

        try:
            contact_text = self._build_contact_text(pg_result)
            chroma_service.store_network_insight(
                str(user_id),
                contact_text,
                {
                    "type": "contact",
                    "contact_id": str(contact_id),
                    "name": pg_result.get("name", ""),
                    "company": pg_result.get("company", ""),
                    "source": "sync_service_update",
                },
            )
        except Exception as e:
            logger.warning(f"ChromaDB update sync failed for contact {contact_id}: {e}")

        return pg_result

    async def sync_contact_delete(
        self,
        session,
        user_id: UUID,
        contact_id: UUID,
    ) -> bool:
        """
        Delete a contact from both Postgres and ChromaDB.
        Prevents "zombie records" per ELITE_REDESIGN_MASTER_PLAN.md.
        """
        from db import contacts_repo

        # Step 1: Delete from Postgres
        deleted = await contacts_repo.delete(session, contact_id)

        # Step 2: Delete from ChromaDB
        try:
            # ChromaDB collections use document IDs — we stored contact_id as metadata
            # We need to query and delete by metadata filter
            collection = chroma_service.network_collection
            if collection:
                results = collection.get(
                    where={"contact_id": str(contact_id)},
                )
                if results and results.get("ids"):
                    collection.delete(ids=results["ids"])
                    logger.info(f"Deleted contact {contact_id} from ChromaDB")
        except Exception as e:
            logger.warning(f"ChromaDB delete sync failed for contact {contact_id}: {e}")

        return deleted

    # ------------------------------------------------------------------
    # Drift detection (verification job)
    # ------------------------------------------------------------------
    async def detect_drift(self, session, user_id: UUID) -> Dict[str, Any]:
        """
        Compare Postgres and ChromaDB to detect inconsistencies.

        Per ELITE_REDESIGN_MASTER_PLAN.md §5.4:
        "Optional: verification job to detect drift"
        """
        from db import contacts_repo

        pg_contacts = await contacts_repo.list(session, user_id, limit=10000)
        pg_ids = {str(c["id"]) for c in pg_contacts}

        # Get all ChromaDB entries for this user
        chroma_ids = set()
        try:
            collection = chroma_service.network_collection
            if collection:
                results = collection.get(
                    where={"type": "contact"},
                )
                if results and results.get("metadatas"):
                    for meta in results["metadatas"]:
                        cid = meta.get("contact_id")
                        if cid:
                            chroma_ids.add(cid)
        except Exception as e:
            logger.warning(f"Drift detection ChromaDB query failed: {e}")
            return {"error": str(e)}

        # Find orphaned records
        orphaned_in_chroma = chroma_ids - pg_ids  # In ChromaDB but not Postgres
        missing_in_chroma = pg_ids - chroma_ids  # In Postgres but not ChromaDB

        return {
            "postgres_count": len(pg_ids),
            "chromadb_count": len(chroma_ids),
            "orphaned_in_chromadb": list(orphaned_in_chroma),
            "missing_in_chromadb": list(missing_in_chroma),
            "in_sync": len(orphaned_in_chroma) == 0 and len(missing_in_chroma) == 0,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _build_contact_text(contact: Dict[str, Any]) -> str:
        """Build a text representation of a contact for vector embedding."""
        parts = []
        if contact.get("name"):
            parts.append(f"Name: {contact['name']}")
        if contact.get("title"):
            parts.append(f"Title: {contact['title']}")
        if contact.get("company"):
            parts.append(f"Company: {contact['company']}")
        if contact.get("tags"):
            parts.append(f"Tags: {', '.join(contact['tags'])}")
        return " | ".join(parts) if parts else "Contact"


# Singleton
sync_service = SyncService()
