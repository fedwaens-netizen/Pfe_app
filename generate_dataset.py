import pandas as pd
import numpy as np
import random

# Define the number of samples to generate
import json

# Define the number of samples to generate
num_samples = 60000

# Load profiles from JSON
with open('morocco_data.json', 'r', encoding='utf-8') as f:
    morocco_data = json.load(f)

# Reformat structure for easy lookup
# 'Marrakech': {'Interet': 'Culture', 'Climat': 'Chaud', 'Budget': 1500, 'Activite': 'Shopping', 'Type': 'Historique'}
destination_profiles = {}
for city in morocco_data:
    destination_profiles[city['name']] = city['profile']
    # Add region and TYPE for logical scoring
    destination_profiles[city['name']]['Region'] = city.get('region', 'Maroc') # Fallback
    destination_profiles[city['name']]['Type'] = city.get('type', 'Ville')

# Define user feature distributions
interests = ['Culture', 'Détente', 'Aventure', 'Nature', 'Sport', 'Gastronomie', 'Shopping', 'Histoire']
# Climates aligned with Morocco regions
climates = ['Tempéré', 'Chaud', 'Froid', 'Désertique']
travel_types = ['Solo', 'Couple', 'Famille', 'Amis']
seasons = ['Printemps', 'Été', 'Automne', 'Hiver']
# Top tourists to Morocco often come from:
nationalities = ['Français', 'Espagnol', 'Marocain', 'Allemand', 'Américain', 'Belge', 'Anglais', 'Néerlandais']
activities = ['Musée', 'Gastronomie', 'Shopping', 'Surf', 'Histoire', 'Randonnée', 'Photographie', 'Détente']

def get_diverse_destination(user_profile, dest_profiles):
    """
    Calculates a compatibility score with explicit interest-to-type mapping.
    Ensures logical predictions: Shopping→Ville, Nature→Plage/Montagne, etc.
    """
    # CRITICAL: Interest to destination TYPE mapping (logical rules)
    interest_type_weights = {
        'Culture': {'Historique': 30, 'Ville': 15, 'Montagne': 2}, # Boosted weights for accuracy
        'Nature': {'Plage': 20, 'Montagne': 25, 'Nature': 25, 'Désert': 10},
        'Détente': {'Plage': 30, 'Montagne': 15, 'Nature': 10, 'Détente': 25},
        'Aventure': {'Désert': 30, 'Montagne': 25, 'Nature': 10, 'Aventure': 25},
        'Sport': {'Montagne': 25, 'Plage': 20, 'Désert': 10, 'Sport': 25},
        'Shopping': {'Ville': 30, 'Historique': 15, 'Shopping': 25},
        'Gastronomie': {'Ville': 25, 'Historique': 20, 'Plage': 10, 'Gastronomie': 25},
        'Histoire': {'Historique': 35, 'Ville': 15, 'Désert': 5},
    }
    
    # Season to climate mapping
    season_climate_weights = {
        'Été': {'Chaud': 10, 'Désertique': -10, 'Tempéré': 5, 'Plage': 15}, # Avoid desert in summer!
        'Hiver': {'Froid': 10, 'Désertique': 15, 'Chaud': -5}, # Desert is good in winter
        'Printemps': {'Tempéré': 10, 'Chaud': 5},
        'Automne': {'Tempéré': 10, 'Froid': 5},
    }
    
    scores = {}
    for dest, profile in dest_profiles.items():
        score = 0
        
        # 1. DESTINATION TYPE matching user interest (MOST IMPORTANT)
        user_interest = user_profile['Interet']
        dest_type = profile.get('Type', 'Ville')  # Get from morocco_data.json type
        type_weights = interest_type_weights.get(user_interest, {})
        
        # Check against Type AND check against explicit Interest in profile if available
        type_score = type_weights.get(dest_type, -10)
        score += type_score
        
        if profile.get('Interet') == user_interest:
             score += 15 # Strong bonus for explicit interest match
        
        # 2. Climate match (medium importance)
        if user_profile['Climat'] == profile.get('Climat', ''):
            score += 10
        
        # 3. Season-climate alignment
        user_season = user_profile.get('Saison', 'Printemps')
        dest_climate = profile.get('Climat', '')
        season_weights = season_climate_weights.get(user_season, {})
        score += season_weights.get(dest_climate, 0)
        
        # 4. Budget proximity (lower weight)
        budget_diff = abs(user_profile['Budget'] - profile.get('Budget', 2000))
        score += max(0, 5 - budget_diff / 400) # Increased sensitivity
        
        # 5. Activity match (bonus)
        if user_profile.get('Activite', '') == profile.get('Activite', ''):
            score += 8
        
        # REDUCED NOISE for "exactness"
        score += np.random.uniform(-0.5, 0.5) 
        
        scores[dest] = score

    # Sort and pick from top candidates
    sorted_dests = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    # Stricter selection: Mostly pick the top 1
    top_n = sorted_dests[:3]
    choices = [t[0] for t in top_n]
    
    if len(choices) == 1:
        return choices[0]
    elif len(choices) >= 2:
        # Heavily favor the best match
        weights = [0.85, 0.10, 0.05] if len(choices) >= 3 else [0.90, 0.10]
        return random.choices(choices, weights=weights[:len(choices)])[0]
    else:
        return choices[0]

# Generate user data
data = []
for i in range(num_samples):
    user = {
        'Age': np.random.randint(18, 70),
        'Budget': np.random.randint(500, 5000), # Adjusted for Morocco budget scale
        'Interet': np.random.choice(interests),
        'Duree': np.random.randint(3, 15),
        'Climat': np.random.choice(climates),
        'Type_Voyage': np.random.choice(travel_types),
        'Saison': np.random.choice(seasons),
        'Nationalite': np.random.choice(nationalities),
        'Activite': np.random.choice(activities)
    }

    # REMOVED TYPO INJECTION for cleaner data
    
    destination = get_diverse_destination(user, destination_profiles)
    user['Destination'] = destination
    data.append(user)

# Create DataFrame and save to CSV
df = pd.DataFrame(data)

# ENSURE NO PERFECT DUPLICATES - This satisfies the user's requirement
df.drop_duplicates(inplace=True)

df.to_csv('tourisme_dataset.csv', index=False)

print(f"Generated {len(df)} unique travel profiles for Morocco.")
print("Dataset 'tourisme_dataset.csv' created successfully.")
