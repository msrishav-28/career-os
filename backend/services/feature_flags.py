"""
Feature flag service — Redis-backed.

Implements the feature flag system from MIGRATION_ROLLOUT_PLAN.md §Feature Flags.
Supports:
  - Boolean on/off flags
  - Percentage-based rollout
  - Per-user overrides
"""
from typing import Dict, Optional
from services.redis_service import redis_service
import hashlib
import json


class FeatureFlags:
    """
    Redis-backed feature flag service.

    Flags are stored in Redis with the key pattern:
      careeros:feature:{flag_name}

    Each flag is a JSON dict:
      {"enabled": bool, "rollout_percentage": int, "overrides": {"user_id": bool}}
    """

    # Default flag definitions per MIGRATION_ROLLOUT_PLAN.md
    DEFAULT_FLAGS: Dict[str, Dict] = {
        "new_approval_ui": {"enabled": False, "rollout_percentage": 0},
        "new_onboarding": {"enabled": False, "rollout_percentage": 0},
        "new_landing": {"enabled": False, "rollout_percentage": 0},
        "quantum_ui": {"enabled": False, "rollout_percentage": 0},
        "proxy_scraping": {"enabled": True, "rollout_percentage": 10},
        "use_proxies": {"enabled": False, "rollout_percentage": 0},
        "use_cached_messages": {"enabled": False, "rollout_percentage": 0},
    }

    def _key(self, flag_name: str) -> str:
        return f"careeros:feature:{flag_name}"

    def _get_flag(self, flag_name: str) -> Dict:
        """Get flag config from Redis, falling back to defaults."""
        try:
            data = redis_service.get_json(self._key(flag_name))
            if data:
                return data
        except Exception:
            pass
        return self.DEFAULT_FLAGS.get(flag_name, {"enabled": False, "rollout_percentage": 0})

    def _set_flag(self, flag_name: str, config: Dict):
        """Persist flag config to Redis."""
        redis_service.set_json(self._key(flag_name), config)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def is_enabled(self, flag_name: str, user_id: Optional[str] = None) -> bool:
        """
        Check if a feature flag is enabled for a given user.

        Resolution:
        1. Check per-user override
        2. Check global enabled state
        3. Check rollout percentage (deterministic hash)
        """
        config = self._get_flag(flag_name)

        # Per-user override
        overrides = config.get("overrides", {})
        if user_id and user_id in overrides:
            return overrides[user_id]

        # Global toggle
        if not config.get("enabled", False):
            return False

        # Percentage rollout
        percentage = config.get("rollout_percentage", 100)
        if percentage >= 100:
            return True
        if percentage <= 0:
            return False

        # Deterministic hash to ensure consistent behavior per user
        if user_id:
            hash_input = f"{flag_name}:{user_id}"
            hash_val = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
            return (hash_val % 100) < percentage

        return False

    def enable(self, flag_name: str, percentage: int = 100):
        """Enable a flag at a given rollout percentage."""
        config = self._get_flag(flag_name)
        config["enabled"] = True
        config["rollout_percentage"] = min(100, max(0, percentage))
        self._set_flag(flag_name, config)

    def disable(self, flag_name: str):
        """Disable a flag immediately."""
        config = self._get_flag(flag_name)
        config["enabled"] = False
        config["rollout_percentage"] = 0
        self._set_flag(flag_name, config)

    def set_override(self, flag_name: str, user_id: str, enabled: bool):
        """Set a per-user override for a flag."""
        config = self._get_flag(flag_name)
        overrides = config.get("overrides", {})
        overrides[user_id] = enabled
        config["overrides"] = overrides
        self._set_flag(flag_name, config)

    def remove_override(self, flag_name: str, user_id: str):
        """Remove a per-user override."""
        config = self._get_flag(flag_name)
        overrides = config.get("overrides", {})
        overrides.pop(user_id, None)
        config["overrides"] = overrides
        self._set_flag(flag_name, config)

    def get_all_flags(self) -> Dict[str, Dict]:
        """Get all flag configurations."""
        result = {}
        for flag_name in self.DEFAULT_FLAGS:
            result[flag_name] = self._get_flag(flag_name)
        return result


# Singleton instance
feature_flags = FeatureFlags()
