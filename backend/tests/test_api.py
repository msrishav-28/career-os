import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct response"""
        response = client.get("/")
        assert response.status_code == 200
        assert "CareerOS API" in response.json()["message"]
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_api_docs_available(self):
        """Test API documentation is available"""
        response = client.get("/docs")
        assert response.status_code == 200


class TestProfileAPI:
    """Test profile endpoints"""
    
    def test_store_profile(self):
        """Test profile storage"""
        profile_data = {
            "skills": ["Python", "FastAPI"],
            "projects": [],
            "experiences": [],
            "education": [],
            "goals": [],
            "interests": ["AI"],
            "achievements": []
        }
        
        response = client.post(
            "/api/profile/store?user_id=test-user",
            json=profile_data
        )
        assert response.status_code == 200


class TestContactsAPI:
    """Test contacts endpoints"""
    
    def test_get_contacts(self):
        """Test getting contacts list"""
        response = client.get("/api/contacts/?user_id=test-user")
        assert response.status_code == 200
        assert "contacts" in response.json()


class TestAnalyticsAPI:
    """Test analytics endpoints"""
    
    def test_dashboard_summary(self):
        """Test dashboard summary endpoint"""
        response = client.get("/api/analytics/dashboard?user_id=test-user&days=7")
        assert response.status_code == 200
        data = response.json()
        assert "outreach" in data
        assert "pipeline" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
