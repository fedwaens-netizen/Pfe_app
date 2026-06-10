import pandas as pd
import numpy as np
import random
import json

# Define the number of samples per destination for better class representation
SAMPLES_PER_DESTINATION = 130 # Target ~140k-150k rows total

# Mapping for 12 regions to 7 Super-Zones
REGION_TO_ZONE = {
    'Tanger-Tétouan-Al Hoceïma': 'Z1_Nord',
    'Oriental': 'Z1_Nord',
    'Fès-Meknès': 'Z2_Centre_Imperial',
    'Rabat-Salé-Kénitra': 'Z2_Centre_Imperial',
    'Casablanca-Settat': 'Z3_Atlantique_Eco',
    'Marrakech-Safi': 'Z4_Safi_Marrakech',
    'Béni Mellal-Khénifra': 'Z4_Safi_Marrakech',
    'Souss-Massa': 'Z5_Souss_Massa',
    'Drâa-Tafilalet': 'Z6_Desert_Est',
    'Guelmim-Oued Noun': 'Z7_Sahara',
    'Laâyoune-Sakia El Hamra': 'Z7_Sahara',
    'Dakhla-Oued Ed-Dahab': 'Z7_Sahara'
}

# Create a City-To-Zone map from the base data
with open('morocco_data.json', 'r', encoding='utf-8') as f:
    morocco_data_base = json.load(f)
CITY_ZONE_MAP = {city['name']: REGION_TO_ZONE.get(city.get('region', ''), 'Z_Unknown') for city in morocco_data_base}

# Define Tiers for popularity
TIER_1_CITIES = {
    'Marrakech', 'Casablanca', 'Rabat', 'Fès', 'Tanger', 'Agadir', 
    'Meknès', 'Essaouira', 'Chefchaouen', 'Ouarzazate', 'Dakhla', 'Merzouga'
}

TIER_2_CITIES = {
    'Oujda', 'Tétouan', 'El Jadida', 'Safi', 'Kenitra', 'Nador', 
    'Al Hoceima', 'Laâyoune', 'Ifrane', 'Taroudant', 'Zagora', 'Tiznit',
    'Asilah', 'Tafraout', 'Taliouine', 'Midelt', 'Azrou', 'Béni Mellal',
    'Oualidia', 'Taghazout', 'Mirleft', 'Moulay Idriss Zerhoun', 'Erfoud'
}

def get_samples_for_city(city_name):
    if city_name in TIER_1_CITIES:
        return 550   # Major cities
    elif city_name in TIER_2_CITIES:
        return 300   # Tier 2 cities
    else:
        return SAMPLES_PER_DESTINATION 

# Consolidated Categories
interests_map = {
    'Culture & Patrimoine': ['Historique', 'Culture', 'Architecture', 'Histoire', 'Patrimoine', 'Art'],
    'Nature & Paysages': ['Nature', 'Montagne', 'Oasis', 'Vallée', 'Forêt'],
    'Plage & Détente': ['Plage', 'Détente', 'Mer'],
    'Aventure & Désert': ['Désert', 'Aventure', 'Randonnée', 'Exploration', 'Caravane'],
    'Gastronomie & Shopping': ['Shopping', 'Gastronomie', 'Médina'],
    'Sports & Loisirs': ['Sport', 'Surf', 'Ski', 'Golf', 'Plongée', 'Kitesurf']
}

all_activities = [
    'Shopping', 'Histoire', 'Photographie', 'Surf', 'Randonnée', 'Architecture', 
    'Gastronomie', 'Ski', 'Kitesurf', 'Arquéologie', 'Détente', 'Plage', 'Art', 
    'Plongée', 'Golf', 'Exploration', 'Caravane', 'Patrimoine', 'Cinéma'
]

all_interests = list(interests_map.keys())
climates = ['Tempéré', 'Chaud', 'Froid', 'Désertique']
travel_types = ['Solo', 'Couple', 'Famille', 'Amis']
seasons = ['Printemps', 'Été', 'Automne', 'Hiver']

def determine_best_interest(dest_profile):
    """Fallback if we want to reverse-engineer interest from dest type"""
    dtype = dest_profile.get('type', 'Ville')
    if dtype == 'Plage': return 'Plage & Détente'
    if dtype == 'Désert': return 'Aventure & Désert'
    if dtype == 'Montagne': return random.choice(['Nature & Paysages', 'Sports & Loisirs'])
    return random.choice(['Culture & Patrimoine', 'Gastronomie & Shopping'])

data = []

for city in morocco_data_base:
    dest_name = city['name']
    dest_type = city.get('type', 'Ville')
    dest_region = city.get('region', 'Maroc')
    profile = city.get('profile', {}) 
    
    dest_climate = profile.get('Climat', random.choice(climates))
    dest_interest = profile.get('Interet', determine_best_interest({"type": dest_type}))
    dest_activity = profile.get('Activite', random.choice(all_activities))
    
    # Map raw interest to consolidated ones
    for cons_interest, keywords in interests_map.items():
        if dest_interest in keywords or any(k in dest_interest for k in keywords):
            dest_interest = cons_interest
            break
    
    col_index = city.get('cost_of_living', 2.0)
    samples = get_samples_for_city(dest_name)
    
    for _ in range(samples):
        # 1. Duration
        if dest_region in ['Dakhla-Oued Ed-Dahab', 'Laâyoune-Sakia El Hamra'] or dest_type == 'Désert':
            user_duree = np.random.randint(5, 17)
        elif dest_type == 'Ville':
            user_duree = np.random.randint(2, 9)
        elif dest_type == 'Plage':
            user_duree = np.random.randint(4, 18)
        else:
            user_duree = np.random.randint(3, 14)
        
        # 2. Budget: linked to COL_INDEX
        base_daily = (col_index ** 2.2) * 480 
        noise = int(np.random.exponential(1.2) * 600 * col_index) 
        white_noise = int(np.random.normal(0, 500)) 
        user_budget = max(400, int(base_daily * user_duree + noise + white_noise))
        
        # 3. Interest: 85% logic favor (increased for clearer separation)
        if random.random() < 0.90:
            user_interest = dest_interest
        else:
            user_interest = random.choice(all_interests)
            
        # 4. Activity: 80% logic favor
        if random.random() < 0.85:
            user_activity = dest_activity
        else:
            user_activity = random.choice(all_activities)

        # 5. Age: Tied to destination and activity
        if dest_type in ['Désert', 'Montagne'] or user_activity in ['Surf', 'Kitesurf', 'Randonnée']:
            user_age = max(18, min(80, int(np.random.normal(30, 10)))) 
        elif user_interest == 'Culture & Patrimoine' or user_activity in ['Histoire', 'Patrimoine', 'Arquéologie']:
            user_age = max(18, min(85, int(np.random.normal(55, 12)))) 
        else:
            user_age = np.random.randint(18, 85)
            
        # 6. Climate: 85% favor
        user_climate = dest_climate if random.random() < 0.90 else random.choice(climates)
            
        # 7. Region: 65% favor
        user_region = dest_region if random.random() < 0.65 else "Toutes"
        
        # 8. Season
        if dest_climate == 'Chaud':
            user_season = random.choice(['Printemps', 'Automne']) if random.random() < 0.75 else random.choice(seasons)
        elif dest_climate == 'Désertique':
            user_season = random.choice(['Automne', 'Hiver']) if random.random() < 0.75 else random.choice(seasons)
        elif dest_climate == 'Froid':
            user_season = random.choice(['Hiver', 'Printemps']) if random.random() < 0.75 else random.choice(seasons)
        else:
            user_season = random.choice(seasons)
            
        # 9. Travel Type
        if dest_type == 'Plage':
            user_type_voyage = random.choices(['Famille', 'Couple', 'Amis', 'Solo'], weights=[0.5, 0.3, 0.1, 0.1])[0]
        elif dest_type in ['Montagne', 'Désert']:
            user_type_voyage = random.choices(['Amis', 'Couple', 'Solo', 'Famille'], weights=[0.4, 0.3, 0.2, 0.1])[0]
        else:
            user_type_voyage = random.choices(['Couple', 'Solo', 'Famille', 'Amis'], weights=[0.4, 0.3, 0.15, 0.15])[0]
            
        # 10. Budget Level
        daily_budget = user_budget / (user_duree + 1e-6)
        if daily_budget < 600: budget_lvl = 'Petit'
        elif daily_budget < 1300: budget_lvl = 'Moyen'
        elif daily_budget < 2800: budget_lvl = 'Luxe'
        else: budget_lvl = 'Ultra-Luxe'

        # 11. Age Group
        if user_age < 26: age_grp = 'Jeune'
        elif user_age < 46: age_grp = 'Adulte'
        elif user_age < 66: age_grp = 'Senior'
        else: age_grp = 'Retraité'

        user = {
            'Age': user_age,
            'Age_Group': age_grp,
            'Budget': user_budget,
            'Budget_Level': budget_lvl,
            'Interet': user_interest,
            'Activite': user_activity,
            'Duree': user_duree,
            'Climat': user_climate,
            'Type_Voyage': user_type_voyage,
            'Saison': user_season,
            'Region': user_region,
            'Zone': CITY_ZONE_MAP.get(dest_name, 'Z_Unknown'),  # Geographical cluster
            'Destination': dest_name,
            'Type_Destination': dest_type
        }
        data.append(user)

# Create DataFrame and save
df = pd.DataFrame(data)
df = df.sample(frac=1).reset_index(drop=True)
df.to_csv('tourisme_dataset.csv', index=False)

print(f"Generated {len(df)} profiles for {len(morocco_data_base)} destinations.")
print("Dataset 'tourisme_dataset.csv' created successfully.")
