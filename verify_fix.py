
import sys
import os
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import schemas
from main import get_prediction, calculate_relevance_score

# Mock request object matching schemas.RecommendationRequest
class MockRequest:
    def __init__(self, Age, Budget, Duree, Interet, Climat, Region, Type_Destination):
        self.Age = Age
        self.Budget = Budget
        self.Duree = Duree
        self.Interet = Interet
        self.Climat = Climat
        self.Region = Region
        self.Type_Destination = Type_Destination

def verify_fix():
    db = SessionLocal()
    try:
        with open("verification_results.txt", "w", encoding="utf-8") as f:
            f.write("=== HYBRID RECOMMENDATION VERIFICATION ===\n\n")
            
            # Test 1: Budget Sensitivity (5 runs each)
            f.write("--- TEST 1: Budget Sensitivity ---\n")
            req_high = MockRequest(Age=25, Budget=5000, Duree=5, Interet="Culture", Climat="Tempéré", Region="Centre-Sud", Type_Destination="")
            req_low = MockRequest(Age=25, Budget=200, Duree=5, Interet="Culture", Climat="Tempéré", Region="Centre-Sud", Type_Destination="")
            
            high_results = [get_prediction(req_high, db) for _ in range(5)]
            low_results = [get_prediction(req_low, db) for _ in range(5)]
            
            f.write(f"High Budget (5000): {high_results}\n")
            f.write(f"Low Budget (200):   {low_results}\n")
            f.write(f"Different? {set(high_results) != set(low_results)}\n\n")
            
            # Test 2: Climate Sensitivity
            f.write("--- TEST 2: Climate Sensitivity ---\n")
            req_hot = MockRequest(Age=30, Budget=2000, Duree=7, Interet="Nature", Climat="Chaud", Region="Nord", Type_Destination="")
            req_cold = MockRequest(Age=30, Budget=2000, Duree=7, Interet="Nature", Climat="Froid", Region="Nord", Type_Destination="")
            
            hot_results = [get_prediction(req_hot, db) for _ in range(5)]
            cold_results = [get_prediction(req_cold, db) for _ in range(5)]
            
            f.write(f"Hot Climate (Chaud):  {hot_results}\n")
            f.write(f"Cold Climate (Froid): {cold_results}\n")
            f.write(f"Different? {set(hot_results) != set(cold_results)}\n\n")
            
            # Test 3: Interest Sensitivity
            f.write("--- TEST 3: Interest Sensitivity ---\n")
            req_culture = MockRequest(Age=28, Budget=1500, Duree=5, Interet="Culture", Climat="Tempéré", Region="Nord-Est", Type_Destination="")
            req_plage = MockRequest(Age=28, Budget=1500, Duree=5, Interet="Plage", Climat="Tempéré", Region="Nord-Est", Type_Destination="")
            
            culture_results = [get_prediction(req_culture, db) for _ in range(5)]
            plage_results = [get_prediction(req_plage, db) for _ in range(5)]
            
            f.write(f"Culture Interest: {culture_results}\n")
            f.write(f"Plage Interest:   {plage_results}\n")
            f.write(f"Different? {set(culture_results) != set(plage_results)}\n\n")
            
            # Test 4: Type Destination Sensitivity
            f.write("--- TEST 4: Destination Type Sensitivity ---\n")
            req_historique = MockRequest(Age=35, Budget=3000, Duree=7, Interet="Culture", Climat="Tempéré", Region="Centre-Sud", Type_Destination="Historique")
            req_plage_type = MockRequest(Age=35, Budget=3000, Duree=7, Interet="Culture", Climat="Tempéré", Region="Centre-Sud", Type_Destination="Plage")
            
            historique_results = [get_prediction(req_historique, db) for _ in range(5)]
            plage_type_results = [get_prediction(req_plage_type, db) for _ in range(5)]
            
            f.write(f"Type=Historique: {historique_results}\n")
            f.write(f"Type=Plage:      {plage_type_results}\n")
            f.write(f"Different? {set(historique_results) != set(plage_type_results)}\n\n")
            
            # Test 5: Stochastic Diversity (same input, multiple runs)
            f.write("--- TEST 5: Stochastic Diversity ---\n")
            req_same = MockRequest(Age=25, Budget=2000, Duree=7, Interet="Nature", Climat="Chaud", Region="Sud-Est", Type_Destination="")
            same_results = [get_prediction(req_same, db) for _ in range(10)]
            
            f.write(f"Same input, 10 runs: {same_results}\n")
            f.write(f"Unique results: {set(same_results)}\n")
            f.write(f"Shows diversity? {len(set(same_results)) > 1}\n")
            
            f.write("\n=== VERIFICATION COMPLETE ===\n")
            
    finally:
        db.close()

if __name__ == "__main__":
    verify_fix()
    print("Verification complete. See verification_results.txt for results.")
