import pandas as pd
import joblib
from database import SessionLocal
import crud

model = joblib.load('recommendation_model.joblib')
preprocessor = joblib.load('preprocessor.joblib')
label_encoder = joblib.load('label_encoder.joblib')

db = SessionLocal()
destinations = crud.get_all_destinations(db)
dest_types = {d.name: d.destination_type for d in destinations}

tests = [
    {'name': 'Beach lover in summer', 'age': 25, 'budget': 2000, 'Duree': 7, 'Interet': 'Nature', 'Climat': 'Chaud', 'continent': 'Ouest', 'Saison': 'Été', 'Type_Destination': 'Mixte', 'Cout_de_la_Vie': 2.5, 'expected': 'Plage'},
    {'name': 'Culture seeker', 'age': 45, 'budget': 3000, 'Duree': 5, 'Interet': 'Culture', 'Climat': 'Tempéré', 'continent': 'Centre-Sud', 'Saison': 'Printemps', 'Type_Destination': 'Mixte', 'Cout_de_la_Vie': 2.5, 'expected': 'Historique'},
    {'name': 'Desert adventure', 'age': 30, 'budget': 1500, 'Duree': 4, 'Interet': 'Aventure', 'Climat': 'Désertique', 'continent': 'Sud-Est', 'Saison': 'Hiver', 'Type_Destination': 'Mixte', 'Cout_de_la_Vie': 2.5, 'expected': 'Désert'},
    {'name': 'Mountain hiker', 'age': 35, 'budget': 1800, 'Duree': 6, 'Interet': 'Sport', 'Climat': 'Froid', 'continent': 'Centre-Sud', 'Saison': 'Automne', 'Type_Destination': 'Mixte', 'Cout_de_la_Vie': 2.5, 'expected': 'Montagne'},
    {'name': 'City shopper', 'age': 28, 'budget': 4000, 'Duree': 3, 'Interet': 'Shopping', 'Climat': 'Tempéré', 'continent': 'Nord', 'Saison': 'Printemps', 'Type_Destination': 'Mixte', 'Cout_de_la_Vie': 2.5, 'expected': 'Ville'},
    {'name': 'Relaxation beach', 'age': 40, 'budget': 2500, 'Duree': 10, 'Interet': 'Détente', 'Climat': 'Chaud', 'continent': 'Ouest', 'Saison': 'Été', 'Type_Destination': 'Mixte', 'Cout_de_la_Vie': 2.5, 'expected': 'Plage'},
    {'name': 'History buff', 'age': 55, 'budget': 3500, 'Duree': 7, 'Interet': 'Histoire', 'Climat': 'Tempéré', 'continent': 'Centre-Sud', 'Saison': 'Automne', 'Type_Destination': 'Mixte', 'Cout_de_la_Vie': 2.5, 'expected': 'Historique'},
]

print('=== PREDICTION LOGIC VERIFICATION (AFTER FIX) ===\n')
correct = 0
total = len(tests)

for test in tests:
    name = test.pop('name')
    expected = test.pop('expected')
    
    input_df = pd.DataFrame([test])
    processed = preprocessor.transform(input_df)
    
    proba = model.predict_proba(processed)[0]
    top_indices = proba.argsort()[-3:][::-1]
    top_probs = proba[top_indices]
    top_names = label_encoder.inverse_transform(model.classes_[top_indices])
    
    predicted_type = dest_types.get(top_names[0], '?')
    is_match = predicted_type == expected
    if is_match:
        correct += 1
    status = "OK" if is_match else "MISMATCH"
    
    print(f'Test: {name}')
    print(f'  Expected: {expected} | Got: {predicted_type} [{status}]')
    print(f'  Top 3: {top_names[0]}({dest_types.get(top_names[0],"?")}), {top_names[1]}({dest_types.get(top_names[1],"?")}), {top_names[2]}({dest_types.get(top_names[2],"?")})')
    print()

print(f'=== RESULT: {correct}/{total} logical predictions ===')
db.close()
