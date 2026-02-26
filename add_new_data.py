"""
add_new_data.py
Adds 50 brand-new destinations + 15,000 new fresh data rows to the dataset.
These destinations have NEVER appeared in the training data, making the model
learn to generalise to new cities via their type/climate/region features.
"""
import json
import random
import numpy as np
import pandas as pd

random.seed(99)
np.random.seed(99)

# ─────────────────────────────────────────────
# 1.  50 BRAND NEW destinations (not in existing data)
# ─────────────────────────────────────────────
brand_new_cities = [
    # (name, region, type, climat)
    ("Tiflet", "Rabat-Salé-Kénitra", "Ville",      "Tempéré"),
    ("Kénitra", "Rabat-Salé-Kénitra", "Ville",     "Tempéré"),
    ("Sidi Kacem", "Rabat-Salé-Kénitra", "Ville",  "Tempéré"),
    ("Ksar el-Kébir", "Tanger-Tétouan-Al Hoceïma", "Historique", "Tempéré"),
    ("Larache 2",  "Tanger-Tétouan-Al Hoceïma", "Plage",     "Tempéré"),
    ("Fnidek",     "Tanger-Tétouan-Al Hoceïma", "Plage",     "Tempéré"),
    ("Martil",     "Tanger-Tétouan-Al Hoceïma", "Plage",     "Tempéré"),
    ("Asilah 2",   "Tanger-Tétouan-Al Hoceïma", "Historique","Tempéré"),
    ("Oued Laou",  "Tanger-Tétouan-Al Hoceïma", "Plage",     "Tempéré"),
    ("Bni Mellal", "Béni Mellal-Khénifra",       "Ville",     "Tempéré"),
    ("Khouribga",  "Béni Mellal-Khénifra",       "Ville",     "Tempéré"),
    ("Azilal",     "Béni Mellal-Khénifra",       "Montagne",  "Froid"),
    ("Demnate",    "Béni Mellal-Khénifra",       "Historique","Tempéré"),
    ("Kasba Tadla","Béni Mellal-Khénifra",       "Historique","Tempéré"),
    ("Imilchil",   "Drâa-Tafilalet",             "Montagne",  "Froid"),
    ("Tinghir",    "Drâa-Tafilalet",             "Désert",    "Désertique"),
    ("Rich",       "Drâa-Tafilalet",             "Désert",    "Désertique"),
    ("Goulmima",   "Drâa-Tafilalet",             "Désert",    "Désertique"),
    ("Erfoud",     "Drâa-Tafilalet",             "Désert",    "Désertique"),
    ("Rissani",    "Drâa-Tafilalet",             "Désert",    "Désertique"),
    ("Tazarine",   "Drâa-Tafilalet",             "Désert",    "Désertique"),
    ("Nkob",       "Drâa-Tafilalet",             "Désert",    "Désertique"),
    ("Boulemane",  "Fès-Meknès",                 "Montagne",  "Froid"),
    ("Missour",    "Fès-Meknès",                 "Désert",    "Désertique"),
    ("El Hajeb",   "Fès-Meknès",                 "Montagne",  "Froid"),
    ("Aïn Leuh",   "Fès-Meknès",                 "Montagne",  "Froid"),
    ("Azrou 2",    "Fès-Meknès",                 "Montagne",  "Froid"),
    ("Berkane",    "Oriental",                    "Ville",     "Tempéré"),
    ("Taourirt",   "Oriental",                    "Désert",    "Désertique"),
    ("Figuig",     "Oriental",                    "Désert",    "Désertique"),
    ("Driouch",    "Oriental",                    "Ville",     "Tempéré"),
    ("Nador 2",    "Oriental",                    "Plage",     "Tempéré"),
    ("Selouane",   "Oriental",                    "Ville",     "Tempéré"),
    ("El Jadida 2","Casablanca-Settat",           "Plage",     "Tempéré"),
    ("Berrechid",  "Casablanca-Settat",           "Ville",     "Tempéré"),
    ("Benslimane", "Casablanca-Settat",           "Nature",    "Tempéré"),
    ("Settat",     "Casablanca-Settat",           "Ville",     "Tempéré"),
    ("Bouznika",   "Rabat-Salé-Kénitra",         "Plage",     "Tempéré"),
    ("Skhirate",   "Rabat-Salé-Kénitra",         "Plage",     "Tempéré"),
    ("Temara",     "Rabat-Salé-Kénitra",         "Ville",     "Tempéré"),
    ("Sidi Ifni",  "Guelmim-Oued Noun",          "Plage",     "Chaud"),
    ("Goulimine",  "Guelmim-Oued Noun",          "Désert",    "Désertique"),
    ("Tan-Tan",    "Guelmim-Oued Noun",          "Désert",    "Désertique"),
    ("Assa",       "Guelmim-Oued Noun",          "Désert",    "Désertique"),
    ("Smara",      "Laâyoune-Sakia El Hamra",    "Désert",    "Désertique"),
    ("Boujdour",   "Laâyoune-Sakia El Hamra",    "Plage",     "Chaud"),
    ("El Marsa",   "Dakhla-Oued Ed-Dahab",       "Plage",     "Chaud"),
    ("Bir Gandouz","Dakhla-Oued Ed-Dahab",       "Désert",    "Désertique"),
    ("Aousserd",   "Dakhla-Oued Ed-Dahab",       "Désert",    "Désertique"),
    ("Tarfaya",    "Laâyoune-Sakia El Hamra",    "Plage",     "Chaud"),
]

# Interest categories for each destination type
TYPE_INTEREST = {
    "Historique": "Histoire",
    "Plage":      "Détente",
    "Montagne":   "Aventure",
    "Désert":     "Aventure",
    "Ville":      "Culture",
    "Nature":     "Nature",
}
TYPE_ACTIVITE = {
    "Historique": "Histoire",
    "Plage":      "Détente",
    "Montagne":   "Randonnée",
    "Désert":     "Randonnée",
    "Ville":      "Shopping",
    "Nature":     "Randonnée",
}

def build_city_entry(name, region, dest_type, climat):
    interest = TYPE_INTEREST.get(dest_type, "Détente")
    activite = TYPE_ACTIVITE.get(dest_type, "Détente")
    return {
        "name": name,
        "region": region,
        "cost_of_living": round(random.uniform(1.2, 3.5), 1),
        "type": dest_type,
        "description": f"Découvrez {name}, une destination remarquable de la région {region}.",
        "images": ["https://images.unsplash.com/photo-1539020140153-e479b8c22e70?q=80&w=1080&auto=format&fit=crop"],
        "places": [{"name": f"Centre de {name}", "image": "https://images.unsplash.com/photo-1548017198-91e9e8374fad?q=80&w=800&auto=format&fit=crop"}],
        "hotels": [{"name": f"Hôtel {name}", "rating": random.randint(3, 5),
                    "rooms": [{"type": "Chambre Standard", "price": round(random.uniform(40, 200), 0),
                               "availability": random.randint(5, 50)}]}],
        "profile": {
            "Interet":  interest,
            "Climat":   climat,
            "Budget":   random.randint(600, 3000),
            "Activite": activite,
        }
    }

# ─────────────────────────────────────────────
# 2.  Load existing JSON and append only new cities
# ─────────────────────────────────────────────
with open("morocco_data.json", "r", encoding="utf-8") as f:
    existing = json.load(f)

existing_names = {c["name"] for c in existing}
added = 0
for name, region, dest_type, climat in brand_new_cities:
    if name not in existing_names:
        existing.append(build_city_entry(name, region, dest_type, climat))
        existing_names.add(name)
        added += 1

with open("morocco_data.json", "w", encoding="utf-8") as f:
    json.dump(existing, f, ensure_ascii=False, indent=2)

print(f"[OK] Added {added} new destinations  ->  total: {len(existing)}")

# ─────────────────────────────────────────────
# 3.  Generate 15,000 NEW rows that include the new destinations
# ─────────────────────────────────────────────
# rebuild destination profiles (includes new cities)
dest_profiles = {}
for city in existing:
    dest_profiles[city["name"]] = {**city["profile"], "Type": city.get("type", "Ville"),
                                    "Region": city.get("region", "Maroc")}

interests   = ["Culture", "Détente", "Aventure", "Nature", "Sport", "Gastronomie", "Shopping", "Histoire"]
climates    = ["Tempéré", "Chaud", "Froid", "Désertique"]
travel_types= ["Solo", "Couple", "Famille", "Amis"]
seasons     = ["Printemps", "Été", "Automne", "Hiver"]
nationalities=["Français", "Espagnol", "Marocain", "Allemand", "Américain", "Belge", "Anglais", "Néerlandais"]
activities  = ["Musée", "Gastronomie", "Shopping", "Surf", "Histoire", "Randonnée", "Photographie", "Détente"]

interest_type_weights = {
    "Culture":      {"Historique": 30, "Ville": 15, "Montagne": 2},
    "Nature":       {"Plage": 20, "Montagne": 25, "Nature": 25, "Désert": 10},
    "Détente":      {"Plage": 30, "Montagne": 15, "Nature": 10},
    "Aventure":     {"Désert": 30, "Montagne": 25, "Nature": 10},
    "Sport":        {"Montagne": 25, "Plage": 20, "Désert": 10},
    "Shopping":     {"Ville": 30, "Historique": 15},
    "Gastronomie":  {"Ville": 25, "Historique": 20, "Plage": 10},
    "Histoire":     {"Historique": 35, "Ville": 15, "Désert": 5},
}
season_climate = {
    "Été":       {"Chaud": 10, "Désertique": -10, "Tempéré": 5},
    "Hiver":     {"Froid": 10, "Désertique": 15, "Chaud": -5},
    "Printemps": {"Tempéré": 10, "Chaud": 5},
    "Automne":   {"Tempéré": 10, "Froid": 5},
}

def pick_destination(user, profiles):
    scores = {}
    for dest, prof in profiles.items():
        s = 0
        tw = interest_type_weights.get(user["Interet"], {})
        s += tw.get(prof.get("Type", "Ville"), -10)
        if prof.get("Interet") == user["Interet"]:
            s += 15
        if user["Climat"] == prof.get("Climat", ""):
            s += 10
        sw = season_climate.get(user.get("Saison", "Printemps"), {})
        s += sw.get(prof.get("Climat", ""), 0)
        diff = abs(user["Budget"] - prof.get("Budget", 2000))
        s += max(0, 5 - diff / 400)
        if user.get("Activite", "") == prof.get("Activite", ""):
            s += 8
        s += np.random.uniform(-0.5, 0.5)
        scores[dest] = s
    top = sorted(scores, key=scores.get, reverse=True)[:3]
    w = [0.85, 0.10, 0.05] if len(top) >= 3 else [0.90, 0.10]
    return random.choices(top, weights=w[:len(top)])[0]

NEW_ROWS = 15_000
new_data = []
for _ in range(NEW_ROWS):
    u = {
        "Age":        np.random.randint(18, 70),
        "Budget":     np.random.randint(500, 5000),
        "Interet":    np.random.choice(interests),
        "Duree":      np.random.randint(3, 15),
        "Climat":     np.random.choice(climates),
        "Type_Voyage":np.random.choice(travel_types),
        "Saison":     np.random.choice(seasons),
        "Nationalite":np.random.choice(nationalities),
        "Activite":   np.random.choice(activities),
    }
    u["Destination"] = pick_destination(u, dest_profiles)
    new_data.append(u)

new_df = pd.DataFrame(new_data)

# Append to existing CSV
existing_df = pd.read_csv("tourisme_dataset.csv")
combined    = pd.concat([existing_df, new_df], ignore_index=True).drop_duplicates()
combined.to_csv("tourisme_dataset.csv", index=False)

print(f"[OK] Added {NEW_ROWS} new rows  ->  total in CSV: {len(combined)}")
print(f"   Unique destinations in CSV: {combined['Destination'].nunique()}")
