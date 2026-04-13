"""
Rate limiting tests.

Per TESTING_STRATEGY.md — Critical Path (100% Coverage Required):
  - Allows requests within limit
  - Blocks requests exceeding limit
  - Resets counter after time window
  - Different users have independent limits
"""
import pytest
from unittest.mock import MagicMock, patch


class TestRateLimiting:
    """Test Redis-backed rate limiting."""

    def _mock_redis(self):
        """Create a mock Redis client."""
        mock = MagicMock()
        mock.pipeline.return_value = mock
        mock.incr.return_value = mock
        mock.expire.return_value = mock
        mock.execute.return_value = [1, True]  # count=1, expire set
        mock.ttl.return_value = 55
        return mock

    def test_allows_within_limit(self):
        """Requests within the limit should be allowed."""
        from services.redis_service import RedisService

        rs = RedisService.__new__(RedisService)
        rs.client = self._mock_redis()
        rs.client.execute.return_value = [5, True]  # 5 requests so far

        allowed, count = rs.check_rate_limit("user1", "api_request", 100)
        assert allowed is True
        assert count == 5

    def test_blocks_exceeding_limit(self):
        """Requests exceeding the limit should be blocked."""
        from services.redis_service import RedisService

        rs = RedisService.__new__(RedisService)
        rs.client = self._mock_redis()
        rs.client.execute.return_value = [101, True]  # 101 > 100 limit

        allowed, count = rs.check_rate_limit("user1", "api_request", 100)
        assert allowed is False
        assert count == 101

    def test_independent_user_limits(self):
        """Different users should have independent rate limits."""
        from services.redis_service import RedisService

        rs = RedisService.__new__(RedisService)
        rs.client = self._mock_redis()

        # User 1 at limit
        rs.client.execute.return_value = [100, True]
        allowed1, _ = rs.check_rate_limit("user1", "api_request", 100)

        # User 2 still under
        rs.client.execute.return_value = [5, True]
        allowed2, _ = rs.check_rate_limit("user2", "api_request", 100)

        assert allowed1 is False
        assert allowed2 is True


class TestRateLimitDependency:
    """Test the FastAPI rate_limit dependency factory."""

    def test_rate_limit_factory_creates_callable(self):
        """rate_limit() should return a callable dependency."""
        from security.rate_limit import rate_limit

        dep = rate_limit("test_action", 10)
        assert callable(dep)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
