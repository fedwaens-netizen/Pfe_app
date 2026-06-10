import pandas as pd
import numpy as np
import random
import json

# Load real Moroccan destinations from JSON
with open('morocco_data.json', 'r', encoding='utf-8') as f:
    cities_data = json.load(f)

# ── Règles logiques ────────────────────────────────────────────────────────────
INTERET_TYPE_COMPAT = {
    'Culture':     ['Ville'],
    'Nature':      ['Montagne'],
    'Détente':     ['Plage'],
    'Aventure':    ['Désert', 'Montagne'],
    'Sport':       ['Montagne', 'Plage'],
    'Shopping':    ['Ville'],
    'Gastronomie': ['Ville'],
    'Histoire':    ['Ville', 'Désert'],
}

CLIMAT_TYPE_COMPAT = {
    'Chaud':       ['Plage'],
    'Tempéré':     ['Ville', 'Montagne'],
    'Froid':       ['Montagne'],
    'Désertique':  ['Désert'],
}

CLIMAT_SAISON = {
    'Chaud':       ['Printemps', 'Été'],
    'Tempéré':     ['Printemps', 'Automne'],
    'Froid':       ['Automne', 'Hiver'],
    'Désertique':  ['Automne', 'Hiver', 'Printemps'],
}

ACTIVITE_BY_TYPE = {
    'Ville':    ['Culture', 'Shopping', 'Gastronomie', 'Histoire'],
    'Plage':    ['Surf', 'Natation', 'Détente', 'Sport'],
    'Montagne': ['Randonnée', 'Ski', 'Nature', 'Sport'],
    'Désert':   ['Randonnée', 'Aventure', 'Photographie'],
}

voyage_types  = ['Solo', 'Couple', 'Famille', 'Amis']
nationalities = ['Marocain', 'Étranger']

# Grouper les villes par type
destinations_by_type = {'Ville': [], 'Plage': [], 'Montagne': [], 'Désert': []}
for c in cities_data:
    t = c.get('type', 'Ville')
    if t in destinations_by_type:
        p = c.get('profile', {})
        destinations_by_type[t].append({
            'name':       c['name'],
            'type':       t,
            'min_budget': p.get('Budget', 1000) * 0.5,
            'max_budget': p.get('Budget', 1000) * 2.5,
        })

print("Destinations par type :")
for t, lst in destinations_by_type.items():
    print(f"  {t}: {len(lst)}")

# ── Correspondances logiques strictes ─────────────────────────────────────────
# (Intérêt, Climat) → Type de destination
PAIRS = [
    ('Culture',     'Tempéré',    'Ville'),
    ('Culture',     'Chaud',      'Ville'),
    ('Culture',     'Froid',      'Ville'),
    ('Nature',      'Tempéré',    'Montagne'),
    ('Nature',      'Froid',      'Montagne'),
    ('Détente',     'Chaud',      'Plage'),
    ('Détente',     'Tempéré',    'Plage'),
    ('Aventure',    'Désertique', 'Désert'),
    ('Aventure',    'Froid',      'Montagne'),
    ('Aventure',    'Tempéré',    'Montagne'),
    ('Sport',       'Froid',      'Montagne'),
    ('Sport',       'Chaud',      'Plage'),
    ('Sport',       'Tempéré',    'Montagne'),
    ('Shopping',    'Tempéré',    'Ville'),
    ('Shopping',    'Chaud',      'Ville'),
    ('Gastronomie', 'Tempéré',    'Ville'),
    ('Gastronomie', 'Chaud',      'Ville'),
    ('Histoire',    'Tempéré',    'Ville'),
    ('Histoire',    'Désertique', 'Désert'),
    ('Histoire',    'Chaud',      'Ville'),
]

def generate_balanced_data(samples_per_type=30000):
    """
    Génère exactement samples_per_type lignes pour chaque type (Ville, Plage, Montagne, Désert).
    Chaque ligne est 100% cohérente Intérêt+Climat+Saison+Type.
    Total = samples_per_type * 4 lignes.
    """
    # Filtrer les paires valides (on a des villes disponibles pour ce type)
    valid_pairs_by_type = {}
    for interet, climat, dest_type in PAIRS:
        if dest_type not in valid_pairs_by_type:
            valid_pairs_by_type[dest_type] = []
        if destinations_by_type.get(dest_type):
            valid_pairs_by_type[dest_type].append((interet, climat))

    all_data = []

    for dest_type, n in [('Ville', samples_per_type), ('Plage', samples_per_type),
                         ('Montagne', samples_per_type), ('Désert', samples_per_type)]:
        cities = destinations_by_type.get(dest_type, [])
        pairs  = valid_pairs_by_type.get(dest_type, [])
        if not cities or not pairs:
            print(f"WARNING: aucune ville ou paire pour {dest_type}")
            continue

        for _ in range(n):
            city             = random.choice(cities)
            interet, climat  = random.choice(pairs)
            saison           = random.choice(CLIMAT_SAISON.get(climat, ['Printemps']))
            budget           = random.randint(int(city['min_budget']), int(city['max_budget']))
            activite         = random.choice(ACTIVITE_BY_TYPE.get(dest_type, ['Culture']))

            all_data.append({
                'Age':              random.randint(18, 70),
                'Budget':           budget,
                'Interet':          interet,
                'Duree':            random.randint(3, 15),
                'Climat':           climat,
                'Type_Voyage':      random.choice(voyage_types),
                'Saison':           saison,
                'Nationalite':      random.choice(nationalities),
                'Activite':         activite,
                'Destination':      city['name'],
                'Type_Destination': dest_type,
            })

    random.shuffle(all_data)
    return pd.DataFrame(all_data)

# ── Générer ───────────────────────────────────────────────────────────────────
SAMPLES_PER_TYPE = 30000
print(f"\nGénération : {SAMPLES_PER_TYPE} lignes * 4 types = {SAMPLES_PER_TYPE*4} total")
df = generate_balanced_data(SAMPLES_PER_TYPE)

print("\nDistribution finale :")
print(df['Type_Destination'].value_counts().to_string())

print("\nIntérêt distribution :")
print(df['Interet'].value_counts().to_string())

df.to_csv('tourisme_dataset.csv', index=False)
print(f"\nDataset sauvegardé : tourisme_dataset.csv ({len(df)} lignes)")
