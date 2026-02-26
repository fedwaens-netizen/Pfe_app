import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, Base, engine

# Create a test client
client = TestClient(app)

# Test fixtures
@pytest.fixture(scope="module")
def test_db():
    """Provide a clean database session for tests."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()

class TestDestinationsAPI:
    """Tests for the Destinations API endpoints."""
    
    def test_list_destinations(self):
        """GET /api/destinations should return a list of Moroccan cities."""
        response = client.get("/api/destinations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        # Check structure
        first = data[0]
        assert "id" in first
        assert "name" in first
        assert "continent" in first
        assert "destination_type" in first
    
    def test_get_destination_by_name(self):
        """GET /api/destinations/{name} should return full destination details."""
        response = client.get("/api/destinations/Marrakech")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Marrakech"
        assert "description" in data
        assert "images" in data
        assert "places" in data
        assert len(data["images"]) > 0
        assert len(data["places"]) > 0
    
    def test_get_destination_not_found(self):
        """GET /api/destinations/{name} should return 404 for unknown city."""
        response = client.get("/api/destinations/UnknownCity123")
        assert response.status_code == 404

class TestRecommendationAPI:
    """Tests for the Recommendation API endpoint."""
    
    def test_recommendation_success(self):
        """POST /api/recommend should return a prediction with images and places."""
        payload = {
            "Age": 30,
            "Budget": 1500,
            "Interet": "Culture",
            "Duree": 7,
            "Climat": "Chaud",
            "Region": "Centre-Sud",
            "Type_Destination": "Historique"
        }
        response = client.post("/api/recommend", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "log_id" in data
        assert "recommendation" in data
        rec = data["recommendation"]
        assert "name" in rec
        assert "images" in rec
        assert "places" in rec
    
    def test_recommendation_validation_error(self):
        """POST /api/recommend should reject invalid input (e.g., negative Age)."""
        payload = {
            "Age": -5,  # Invalid
            "Budget": 1500,
            "Interet": "Culture",
            "Duree": 7,
            "Climat": "Chaud",
            "Region": "Centre-Sud",
            "Type_Destination": "Historique"
        }
        response = client.post("/api/recommend", json=payload)
        assert response.status_code == 422  # Unprocessable Entity (validation error)

class TestHotelsAPI:
    """Tests for the Hotels API endpoints."""
    
    def test_search_hotels_by_destination(self):
        """GET /api/hotels/search should return hotels for a given destination."""
        response = client.get("/api/hotels/search?destination=Marrakech")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            hotel = data[0]
            assert "name" in hotel
            assert "rating" in hotel
            assert "rooms" in hotel

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
