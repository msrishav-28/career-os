"""
Authentication tests.

Per TESTING_STRATEGY.md — Critical Path (100% Coverage Required):
  - User authentication
  - Session expires after timeout
  - Token refresh works correctly
  - Cannot access protected routes without auth
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta, timezone


class TestJWT:
    """Test JWT token creation and verification."""

    def test_create_access_token(self):
        """Create a valid access token."""
        from auth.jwt import create_access_token

        token = create_access_token({"sub": "test-user-123", "email": "test@test.com"})
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20

    def test_verify_valid_token(self):
        """Verify a freshly created token."""
        from auth.jwt import create_access_token, verify_token

        token = create_access_token({"sub": "test-user-123", "email": "test@test.com"})
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test-user-123"
        assert payload["email"] == "test@test.com"

    def test_verify_expired_token(self):
        """Expired tokens should return None."""
        from auth.jwt import create_access_token, verify_token

        token = create_access_token(
            {"sub": "test-user-123"},
            expires_delta=timedelta(seconds=-1),
        )
        payload = verify_token(token)
        assert payload is None

    def test_verify_invalid_token(self):
        """Invalid tokens should return None."""
        from auth.jwt import verify_token

        payload = verify_token("not.a.valid.token")
        assert payload is None

    def test_verify_tampered_token(self):
        """Tampered tokens should return None."""
        from auth.jwt import create_access_token, verify_token

        token = create_access_token({"sub": "test-user-123"})
        tampered = token[:-5] + "XXXXX"
        payload = verify_token(tampered)
        assert payload is None


class TestPasswordHashing:
    """Test bcrypt password hashing."""

    def test_hash_and_verify(self):
        """Hash a password and verify it."""
        from auth.jwt import hash_password, verify_password

        hashed = hash_password("my-secure-password")
        assert hashed != "my-secure-password"
        assert verify_password("my-secure-password", hashed)

    def test_wrong_password(self):
        """Wrong password should not verify."""
        from auth.jwt import hash_password, verify_password

        hashed = hash_password("correct-password")
        assert not verify_password("wrong-password", hashed)

    def test_hash_is_unique(self):
        """Two hashes of the same password should differ (salt)."""
        from auth.jwt import hash_password

        h1 = hash_password("same-password")
        h2 = hash_password("same-password")
        assert h1 != h2  # bcrypt uses random salt


class TestAuthRoutes:
    """Test auth API endpoints (without database)."""

    def test_login_missing_fields(self):
        """Login with missing fields should return 422."""
        from fastapi.testclient import TestClient
        from api.main import app

        client = TestClient(app)
        response = client.post("/auth/login", json={})
        assert response.status_code == 422

    def test_register_missing_fields(self):
        """Register with missing fields should return 422."""
        from fastapi.testclient import TestClient
        from api.main import app

        client = TestClient(app)
        response = client.post("/auth/register", json={})
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
