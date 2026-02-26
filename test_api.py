from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, RecommendationHistory

client = TestClient(app)

def test_recommendation_api():
    print("Testing /api/recommend endpoint (Morocco + Images)...")
    payload = {
        "Age": 25,
        "Budget": 1500,
        "Interet": "Culture",
        "Duree": 5,
        "Climat": "Chaud",
        "Continent": "Centre-Sud", # Adjusted region from morocco_data.json
        "Type_Destination": "Historique"
    }
    
    response = client.post("/api/recommend", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("Success! Response key layout:", data.keys())
        rec = data.get("recommendation", {})
        print(f"Prediction: {rec.get('name')}")
        
        # Verify rich data
        images = rec.get("images", [])
        places = rec.get("places", [])
        
        print(f"Images found: {len(images)}")
        print(f"Places found: {len(places)}")
        if places:
            print(f"Sample Place: {places[0]['name']} - {places[0]['image']}")
        
        assert "name" in rec
        assert len(images) > 0
        assert len(places) > 0
        assert "log_id" in data
            
    else:
        print(f"Failed. Status: {response.status_code}, Detail: {response.text}")

if __name__ == "__main__":
    test_recommendation_api()
