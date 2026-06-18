"""
generate_clean_dataset.py
=========================
Génère un dataset 100% cohérent avec les valeurs du frontend ForYou.jsx.
Règles :
- Interet  = exactement les 6 valeurs du frontend
- Activite = dérivé de l'intérêt (pas aléatoire)
- Climat   = cohérent avec le type de destination
- Saison   = cohérente avec le climat
- Region   = uniquement les 12 régions officielles + "Toutes"
- Type_Destination = Ville | Plage | Montagne | Désert (pas Villages/Commune)
"""
import pandas as pd
import numpy as np
import random
import json

random.seed(42)
np.random.seed(42)

# ─── EXACT VALUES MATCHING THE FRONTEND ────────────────────────────────────────
VALID_INTERETS      = ['Culture & Patrimoine', 'Nature & Paysages', 'Plage & Détente',
                       'Aventure & Désert', 'Gastronomie & Shopping', 'Sports & Loisirs']
VALID_DEST_TYPES    = ['Ville', 'Plage', 'Montagne', 'Désert']
VALID_CLIMATES      = ['Chaud', 'Tempéré', 'Froid', 'Désertique']
VALID_SAISONS       = ['Printemps', 'Été', 'Automne', 'Hiver']
VALID_TRAVEL_TYPES  = ['Solo', 'Couple', 'Famille', 'Amis']
VALID_REGIONS       = [
    'Toutes', 'Tanger-Tétouan-Al Hoceïma', "Région de l'Oriental",
    'Fès-Meknès', 'Rabat-Salé-Kénitra', 'Béni Mellal-Khénifra',
    'Casablanca-Settat', 'Marrakech-Safi', 'Drâa-Tafilalet',
    'Souss-Massa', 'Guelmim-Oued Noun', 'Laâyoune-Sakia El Hamra',
    'Dakhla-Oued Ed-Dahab'
]

# ─── ACTIVITIES mapped to each interest (coherent) ──────────────────────────────
INTERET_TO_ACTIVITES = {
    'Culture & Patrimoine':   ['Histoire', 'Architecture', 'Patrimoine', 'Art', 'Archéologie', 'Photographie'],
    'Nature & Paysages':      ['Randonnée', 'Photographie', 'Exploration', 'Nature'],
    'Plage & Détente':        ['Plage', 'Détente', 'Surf', 'Plongée', 'Kitesurf'],
    'Aventure & Désert':      ['Caravane', 'Exploration', 'Randonnée', 'Aventure'],
    'Gastronomie & Shopping': ['Gastronomie', 'Shopping', 'Médina', 'Marché'],
    'Sports & Loisirs':       ['Surf', 'Randonnée', 'Ski', 'Golf', 'Kitesurf', 'Plongée'],
}

# ─── DESTINATION PROFILE: which INTERET fits best ────────────────────────────────
DEST_TYPE_TO_INTERET = {
    'Ville':    ['Culture & Patrimoine', 'Gastronomie & Shopping', 'Culture & Patrimoine'],
    'Plage':    ['Plage & Détente', 'Sports & Loisirs', 'Plage & Détente'],
    'Montagne': ['Nature & Paysages', 'Sports & Loisirs', 'Aventure & Désert'],
    'Désert':   ['Aventure & Désert', 'Nature & Paysages', 'Aventure & Désert'],
}

# ─── CLIMATE per dest type ────────────────────────────────────────────────────────
DEST_TYPE_TO_CLIMAT = {
    'Ville':    ['Tempéré', 'Chaud', 'Froid'],
    'Plage':    ['Chaud', 'Tempéré'],
    'Montagne': ['Froid', 'Tempéré'],
    'Désert':   ['Désertique', 'Chaud'],
}

# ─── SEASON per climate ────────────────────────────────────────────────────────────
CLIMAT_TO_SAISON = {
    'Chaud':      ['Printemps', 'Été'],
    'Tempéré':    ['Printemps', 'Automne'],
    'Froid':      ['Automne', 'Hiver'],
    'Désertique': ['Automne', 'Hiver', 'Printemps'],
}

# ─── ZONES mapping ────────────────────────────────────────────────────────────────
REGION_TO_ZONE = {
    'Tanger-Tétouan-Al Hoceïma':   'Z1_Nord',
    "Région de l'Oriental":        'Z1_Nord',
    'Fès-Meknès':                  'Z2_Centre_Imperial',
    'Rabat-Salé-Kénitra':          'Z2_Centre_Imperial',
    'Casablanca-Settat':           'Z3_Atlantique_Eco',
    'Marrakech-Safi':              'Z4_Safi_Marrakech',
    'Béni Mellal-Khénifra':        'Z4_Safi_Marrakech',
    'Souss-Massa':                 'Z5_Souss_Massa',
    'Drâa-Tafilalet':              'Z6_Desert_Est',
    'Guelmim-Oued Noun':           'Z7_Sahara',
    'Laâyoune-Sakia El Hamra':     'Z7_Sahara',
    'Dakhla-Oued Ed-Dahab':        'Z7_Sahara',
}

# ─── Load destinations from DB-like JSON ─────────────────────────────────────────
with open('morocco_data.json', 'r', encoding='utf-8') as f:
    morocco_raw = json.load(f)

# Normalize destination types
TYPE_MAP = {
    'Village': 'Ville', 'Villages/Commune': 'Ville', 'Commune': 'Ville',
    'Historique': 'Ville', 'Nature': 'Montagne', 'Oasis': 'Désert',
}

def normalize_type(t):
    if not t:
        return 'Ville'
    return TYPE_MAP.get(t, t if t in VALID_DEST_TYPES else 'Ville')

def normalize_region(r):
    """Map any region string to a valid region from the frontend list."""
    if not r or r not in VALID_REGIONS:
        return 'Toutes'
    return r

# ─── TIERS: number of samples per city ───────────────────────────────────────────
TIER_1 = {'Marrakech', 'Casablanca', 'Rabat', 'Fès', 'Tanger', 'Agadir',
           'Meknès', 'Essaouira', 'Chefchaouen', 'Ouarzazate', 'Dakhla', 'Merzouga'}
TIER_2 = {'Oujda', 'Tétouan', 'El Jadida', 'Safi', 'Kenitra', 'Nador',
           'Al Hoceima', 'Laâyoune', 'Ifrane', 'Taroudant', 'Zagora', 'Tiznit',
           'Asilah', 'Tafraout', 'Midelt', 'Azrou', 'Béni Mellal',
           'Oualidia', 'Taghazout', 'Mirleft', 'Erfoud'}

def n_samples(name):
    if name in TIER_1: return 500
    if name in TIER_2: return 250
    return 100

data = []

for city in morocco_raw:
    dest_name    = city['name']
    dest_type    = normalize_type(city.get('type', 'Ville'))
    dest_region  = normalize_region(city.get('region', 'Toutes'))
    dest_zone    = REGION_TO_ZONE.get(dest_region, 'Z2_Centre_Imperial')
    col_index    = city.get('cost_of_living', 2.0)

    # Best interest for this destination type
    best_interets = DEST_TYPE_TO_INTERET[dest_type]
    # Best climates for this destination type
    best_climates = DEST_TYPE_TO_CLIMAT[dest_type]

    n = n_samples(dest_name)

    for _ in range(n):
        # ── INTERET (90% coherent) ──────────────────────────────────────────────
        if random.random() < 0.90:
            interet = random.choice(best_interets)
        else:
            interet = random.choice(VALID_INTERETS)

        # ── ACTIVITE (always coherent with interet) ─────────────────────────────
        activite = random.choice(INTERET_TO_ACTIVITES[interet])

        # ── CLIMAT (85% coherent) ───────────────────────────────────────────────
        if random.random() < 0.85:
            climat = random.choice(best_climates)
        else:
            climat = random.choice(VALID_CLIMATES)

        # ── SAISON (80% coherent with climat) ───────────────────────────────────
        if random.random() < 0.80:
            saison = random.choice(CLIMAT_TO_SAISON[climat])
        else:
            saison = random.choice(VALID_SAISONS)

        # ── REGION (60% exact, 40% "Toutes") ────────────────────────────────────
        if dest_region != 'Toutes' and random.random() < 0.60:
            region = dest_region
        else:
            region = 'Toutes'

        # ── DURATION ─────────────────────────────────────────────────────────────
        if dest_type == 'Désert':
            duree = np.random.randint(5, 16)
        elif dest_type == 'Plage':
            duree = np.random.randint(4, 15)
        elif dest_type == 'Montagne':
            duree = np.random.randint(3, 12)
        else:  # Ville
            duree = np.random.randint(2, 8)

        # ── BUDGET (tied to cost_of_living) ──────────────────────────────────────
        base_daily = (col_index ** 2.0) * 400
        noise      = int(np.random.exponential(1.0) * 400 * col_index)
        budget     = max(500, int(base_daily * duree + noise))

        # ── AGE ───────────────────────────────────────────────────────────────────
        if interet in ['Aventure & Désert', 'Sports & Loisirs']:
            age = max(18, min(75, int(np.random.normal(28, 9))))
        elif interet == 'Culture & Patrimoine':
            age = max(18, min(85, int(np.random.normal(52, 13))))
        elif interet == 'Plage & Détente':
            age = max(18, min(80, int(np.random.normal(35, 12))))
        else:
            age = np.random.randint(18, 80)

        # ── TRAVEL TYPE ───────────────────────────────────────────────────────────
        if dest_type == 'Plage':
            type_voyage = random.choices(VALID_TRAVEL_TYPES, weights=[0.1, 0.3, 0.4, 0.2])[0]
        elif dest_type in ['Montagne', 'Désert']:
            type_voyage = random.choices(VALID_TRAVEL_TYPES, weights=[0.2, 0.3, 0.1, 0.4])[0]
        else:
            type_voyage = random.choices(VALID_TRAVEL_TYPES, weights=[0.3, 0.4, 0.15, 0.15])[0]

        data.append({
            'age':              age,
            'budget':           budget,
            'interet':          interet,
            'activite':         activite,
            'duree':            duree,
            'climat':           climat,
            'saison':           saison,
            'region':           region,
            'type_voyage':      type_voyage,
            'zone':             dest_zone,
            'destination':      dest_name,
            'type_destination': dest_type,
        })

df = pd.DataFrame(data)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
df.to_csv('tourisme_dataset_clean.csv', index=False)

print(f"Generated {len(df)} rows for {df['destination'].nunique()} destinations")
print(f"Interet values: {sorted(df['interet'].unique())}")
print(f"Climat values: {sorted(df['climat'].unique())}")
print(f"Type_destination values: {sorted(df['type_destination'].unique())}")
print(f"Region values (first 5): {sorted(df['region'].unique())[:5]}")
print(f"\nInteret -> Type_Destination distribution:")
print(pd.crosstab(df['interet'], df['type_destination']))
