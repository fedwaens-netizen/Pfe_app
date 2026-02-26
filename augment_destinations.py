import json
import random

# Existing data to check for duplicates
try:
    with open('morocco_data.json', 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
        existing_names = {city['name'] for city in existing_data}
except FileNotFoundError:
    existing_data = []
    existing_names = set()

# List of new cities with metadata (Name, Region, Type, Climat)
# Source: Consolidated from research and geographical knowledge
new_cities_raw = [
    ("Salé", "Rabat-Salé-Kénitra", "Ville", "Tempéré"),
    ("Meknès", "Fès-Meknès", "Historique", "Tempéré"),
    ("Oujda", "Oriental", "Ville", "Chaud"),
    ("Kenitra", "Rabat-Salé-Kénitra", "Ville", "Tempéré"),
    ("Tétouan", "Tanger-Tetouan-Al Hoceima", "Historique", "Tempéré"),
    ("Temara", "Rabat-Salé-Kénitra", "Ville", "Tempéré"),
    ("Safi", "Marrakesh-Safi", "Historique", "Tempéré"),
    ("Mohammedia", "Casablanca-Settat", "Détente", "Tempéré"),
    ("Khouribga", "Béni Mellal-Khénifra", "Ville", "Tempéré"),
    ("Beni Mellal", "Béni Mellal-Khénifra", "Nature", "Contenental"), # Fixed typo in logic later or adjust
    ("Aït Melloul", "Souss-Massa", "Ville", "Chaud"),
    ("Nador", "Oriental", "Détente", "Tempéré"),
    ("Dar Bouazza", "Casablanca-Settat", "Détente", "Tempéré"),
    ("Taza", "Fès-Meknès", "Aventure", "Tempéré"),
    ("Settat", "Casablanca-Settat", "Ville", "Tempéré"),
    ("Berrechid", "Casablanca-Settat", "Ville", "Tempéré"),
    ("Khemisset", "Rabat-Salé-Kénitra", "Ville", "Tempéré"),
    ("Inezgane", "Souss-Massa", "Ville", "Chaud"),
    ("Ksar El Kebir", "Tanger-Tetouan-Al Hoceima", "Histoire", "Chaud"),
    ("Larache", "Tanger-Tetouan-Al Hoceima", "Histoire", "Tempéré"),
    ("Guelmim", "Guelmim-Oued Noun", "Aventure", "Chaud"),
    ("Khenifra", "Béni Mellal-Khénifra", "Nature", "Froid"),
    ("Berkane", "Oriental", "Gastronomie", "Chaud"),
    ("Taourirt", "Oriental", "Ville", "Chaud"),
    ("Bouskoura", "Casablanca-Settat", "Nature", "Tempéré"),
    ("Fquih Ben Salah", "Béni Mellal-Khénifra", "Ville", "Chaud"),
    ("Dcheira El Jihadia", "Souss-Massa", "Ville", "Chaud"),
    ("Oued Zem", "Béni Mellal-Khénifra", "Histoire", "Chaud"),
    ("El Kelaâ des Sraghna", "Marrakesh-Safi", "Ville", "Chaud"),
    ("Sidi Slimane", "Rabat-Salé-Kénitra", "Ville", "Chaud"),
    ("Errachidia", "Drâa-Tafilalet", "Aventure", "Désertique"),
    ("Guercif", "Oriental", "Ville", "Chaud"),
    ("Oulad Teima", "Souss-Massa", "Ville", "Chaud"),
    ("Ben Guerir", "Marrakesh-Safi", "Ville", "Chaud"),
    ("Tifelt", "Rabat-Salé-Kénitra", "Ville", "Tempéré"),
    ("Lqliaa", "Souss-Massa", "Ville", "Chaud"),
    ("Sefrou", "Fès-Meknès", "Nature", "Tempéré"),
    ("Fnideq", "Tanger-Tetouan-Al Hoceima", "Shopping", "Chaud"),
    ("Sidi Kacem", "Rabat-Salé-Kénitra", "Ville", "Chaud"),
    ("Tiznit", "Souss-Massa", "Histoire", "Chaud"),
    ("Tan-Tan", "Guelmim-Oued Noun", "Aventure", "Désertique"),
    ("Souq Larbaa", "Rabat-Salé-Kénitra", "Shopping", "Chaud"),
    ("Youssoufia", "Marrakesh-Safi", "Ville", "Chaud"),
    ("Lahraouyine", "Casablanca-Settat", "Ville", "Tempéré"),
    ("Ain Harrouda", "Casablanca-Settat", "Ville", "Tempéré"),
    ("Souk Sebt", "Béni Mellal-Khénifra", "Gastronomie", "Chaud"),
    ("Skhirat", "Rabat-Salé-Kénitra", "Détente", "Tempéré"),
    ("Ouezzane", "Tanger-Tetouan-Al Hoceima", "Shopping", "Tempéré"),
    ("Benslimane", "Casablanca-Settat", "Nature", "Tempéré"),
    ("Al Hoceima", "Tanger-Tetouan-Al Hoceima", "Détente", "Chaud"),
    ("Beni Ansar", "Oriental", "Ville", "Tempéré"),
    ("M'diq", "Tanger-Tetouan-Al Hoceima", "Détente", "Froid"), # Coastal but often cool breeze evening? Kept Froid/Tempéré variations
    ("Sidi Bennour", "Casablanca-Settat", "Shopping", "Froid"),
    ("Midelt", "Drâa-Tafilalet", "Aventure", "Froid"),
    ("Azrou", "Fès-Meknès", "Nature", "Froid"),
    ("Drargua", "Souss-Massa", "Ville", "Chaud"),
    ("Zagora", "Drâa-Tafilalet", "Aventure", "Désertique"),
    ("Taounate", "Fès-Meknès", "Aventure", "Tempéré"),
    ("Sidi Ifni", "Guelmim-Oued Noun", "Détente", "Tempéré"),
    ("Tinghir", "Drâa-Tafilalet", "Sport", "Chaud"),
    ("Moulay Idriss Zerhoun", "Fès-Meknès", "Histoire", "Tempéré"),
    ("Volubilis", "Fès-Meknès", "Histoire", "Froid"), # Nearby Meknes
    ("Ifrane", "Fès-Meknès", "Nature", "Froid"), # Already in? Check names.
    ("Imilchil", "Drâa-Tafilalet", "Sport", "Froid"),
    ("Tafraoute", "Souss-Massa", "Sport", "Chaud"),
    ("Oualidia", "Casablanca-Settat", "Détente", "Tempéré"),
    ("Mirleft", "Guelmim-Oued Noun", "Détente", "Désertique"),
    ("Taghazout", "Souss-Massa", "Détente", "Tempéré"),
    ("Saidia", "Oriental", "Détente", "Chaud"),
    ("Cabo Negro", "Tanger-Tetouan-Al Hoceima", "Nature", "Chaud"),
    ("Bouznika", "Casablanca-Settat", "Détente", "Froid"),
    ("Moulay Bousselham", "Rabat-Salé-Kénitra", "Nature", "Tempéré"),
    ("El Jebha", "Tanger-Tetouan-Al Hoceima", "Nature", "Tempéré"),
    ("Akchour", "Tanger-Tetouan-Al Hoceima", "Nature", "Froid"),
    ("Bin El Ouidane", "Béni Mellal-Khénifra", "Nature", "Tempéré"),
    ("Ouzoud", "Béni Mellal-Khénifra", "Aventure", "Tempéré"),
    ("Imouzzer Ida Outanane", "Souss-Massa", "Sport", "Désertique"),
    ("Ait Benhaddou", "Drâa-Tafilalet", "Culture", "Désertique"),
    ("Mhamid El Ghizlane", "Drâa-Tafilalet", "Aventure", "Désertique"),
    ("Chefchaouen", "Tanger-Tetouan-Al Hoceima", "Nature", "Tempéré"), # Already in?
    ("Asilah", "Tanger-Tetouan-Al Hoceima", "Culture", "Tempéré"), # Already in?
    ("Tamraght", "Souss-Massa", "Détente", "Tempéré"),
    ("Imsouane", "Souss-Massa", "Détente", "Désertique"),
    ("Sidi Kaouki", "Marrakesh-Safi", "Détente", "Désertique"),
    ("Aghmat", "Marrakesh-Safi", "Histoire", "Chaud"),
    ("Amizmiz", "Marrakesh-Safi", "Nature", "Froid"),
    ("Ourika", "Marrakesh-Safi", "Aventure", "Tempéré"),
    ("Ouirgane", "Marrakesh-Safi", "Nature", "Tempéré"),
    ("Imlil", "Marrakesh-Safi", "Aventure", "Froid"),
    ("Ait Bouguemez", "Béni Mellal-Khénifra", "Nature", "Froid"),
    ("Demnate", "Béni Mellal-Khénifra", "Sport", "Tempéré"),
    ("Bhalil", "Fès-Meknès", "Culture", "Tempéré"), # Cave dwellings
    ("Immouzer Kandar", "Fès-Meknès", "Aventure", "Tempéré"),
    ("Sefrou", "Fès-Meknès", "Histoire", "Tempéré"),
    ("Missour", "Fès-Meknès", "Aventure", "Désertique"),
    ("Boulemane", "Fès-Meknès", "Nature", "Froid"),
    ("Outat El Haj", "Fès-Meknès", "Nature", "Chaud"),
    ("Guercif", "Oriental", "Shopping", "Chaud"),
    ("Jerada", "Oriental", "Sport", "Désertique"),
    ("Figuig", "Oriental", "Aventure", "Désertique"),
    ("Tendrara", "Oriental", "Aventure", "Désertique"),
    ("Bouarfa", "Oriental", "Aventure", "Désertique"),
    ("Tata", "Souss-Massa", "Aventure", "Désertique"),
    ("Akka", "Souss-Massa", "Aventure", "Désertique"),
    ("Foureirah", "Souss-Massa", "Aventure", "Désertique"), # Less known
    ("Assa", "Guelmim-Oued Noun", "Aventure", "Désertique"),
    ("Zag", "Guelmim-Oued Noun", "Aventure", "Désertique"),
    ("Smara", "Laâyoune-Sakia El Hamra", "Aventure", "Désertique"),
    ("Boujdour", "Laâyoune-Sakia El Hamra", "Détente", "Désertique"),
    ("Laâyoune", "Laâyoune-Sakia El Hamra", "Aventure", "Désertique"),
    ("Tarfaya", "Laâyoune-Sakia El Hamra", "Détente", "Chaud"),
    ("Akhfennir", "Laâyoune-Sakia El Hamra", "Nature", "Chaud"),
    ("Dakhla", "Dakhla-Oued Ed-Dahab", "Détente", "Chaud"), # Already in?
    ("Bir Gandouz", "Dakhla-Oued Ed-Dahab", "Aventure", "Désertique"),
    ("Gargarat", "Dakhla-Oued Ed-Dahab", "Aventure", "Désertique"),
    ("Rissani", "Drâa-Tafilalet", "Aventure", "Désertique"),
    ("Erfoud", "Drâa-Tafilalet", "Aventure", "Désertique"),
    ("Jorf", "Drâa-Tafilalet", "Aventure", "Désertique"),
    ("Goulmima", "Drâa-Tafilalet", "Aventure", "Désertique"),
    ("Tinejdad", "Drâa-Tafilalet", "Aventure", "Désertique"),
    ("Alnif", "Drâa-Tafilalet", "Aventure", "Désertique"),
    ("Nekob", "Drâa-Tafilalet", "Aventure", "Désertique"),
    ("Agdz", "Drâa-Tafilalet", "Aventure", "Désertique"),
    ("Tamegroute", "Drâa-Tafilalet", "Culture", "Froid"), # Pottery
    ("M'Semrir", "Drâa-Tafilalet", "Aventure", "Froid"),
    ("Kelâat M'Gouna", "Drâa-Tafilalet", "Culture", "Tempéré"), # Roses
    ("Boumalne Dadès", "Drâa-Tafilalet", "Aventure", "Tempéré"),
    ("Skoura", "Drâa-Tafilalet", "Nature", "Chaud"),
    ("Taliouine", "Souss-Massa", "Culture", "Chaud"), # Saffron
    ("Tazenakht", "Drâa-Tafilalet", "Culture", "Chaud"), # Carpets
    ("Aouzellag", "Souss-Massa", "Nature", "Chaud"),
    ("Igherm", "Souss-Massa", "Nature", "Chaud"),
    ("Ait Baha", "Souss-Massa", "Sport", "Chaud"),
    ("Biougra", "Souss-Massa", "Shopping", "Chaud"),
    ("Massa", "Souss-Massa", "Nature", "Chaud"),
    ("Tifnit", "Souss-Massa", "Détente", "Chaud"),
    ("Sidi R'bat", "Souss-Massa", "Nature", "Chaud"),
    ("Aglou", "Souss-Massa", "Détente", "Chaud"),
    ("Sidi Ifni", "Guelmim-Oued Noun", "Détente", "Chaud"),
    ("El Ouatia", "Guelmim-Oued Noun", "Détente", "Chaud"),
    ("Abteh", "Guelmim-Oued Noun", "Aventure", "Désertique"),
    ("Ksabi", "Guelmim-Oued Noun", "Aventure", "Désertique"),
    ("Tiglit", "Guelmim-Oued Noun", "Aventure", "Désertique"),
    ("Fask", "Guelmim-Oued Noun", "Aventure", "Désertique"),
    ("Asrir", "Guelmim-Oued Noun", "Aventure", "Désertique"),
    ("Ifrane Atlas Saghir", "Guelmim-Oued Noun", "Aventure", "Désertique"),
    ("Amtoudi", "Guelmim-Oued Noun", "Aventure", "Désertique"),
    ("Taghjijt", "Guelmim-Oued Noun", "Aventure", "Désertique"),
    ("Bouizakarne", "Guelmim-Oued Noun", "Aventure", "Désertique"),
    ("Timoulay", "Guelmim-Oued Noun", "Aventure", "Désertique"),
    ("Sidi Bou Othmane", "Marrakesh-Safi", "Histoire", "Chaud"),
    ("Tamellalt", "Marrakesh-Safi", "Ville", "Chaud"),
    ("Laattaouia", "Marrakesh-Safi", "Ville", "Chaud"),
    ("Sidi Rahal", "Marrakesh-Safi", "Nature", "Désertique"),
    ("Ait Ourir", "Marrakesh-Safi", "Gastronomie", "Froid"),
    ("Tahanaout", "Marrakesh-Safi", "Shopping", "Tempéré"),
    ("Chichaoua", "Marrakesh-Safi", "Gastronomie", "Désertique"),
    ("Imintanout", "Marrakesh-Safi", "Aventure", "Chaud"),
    ("Essaouira", "Marrakesh-Safi", "Détente", "Froid"),
    ("Simeyyan", "Marrakesh-Safi", "Aventure", "Chaud"),
    ("Sidi Mokhtar", "Marrakesh-Safi", "Aventure", "Chaud"),
    ("Ounagha", "Marrakesh-Safi", "Aventure", "Chaud"),
    ("El Hanchane", "Marrakesh-Safi", "Aventure", "Chaud"),
    ("Talmest", "Marrakesh-Safi", "Aventure", "Chaud"),
    ("Tamanar", "Marrakesh-Safi", "Nature", "Chaud"),
    ("Smimou", "Marrakesh-Safi", "Nature", "Chaud"),
    ("Tafetachte", "Marrakesh-Safi", "Nature", "Chaud"),
    ("Had Dra", "Marrakesh-Safi", "Shopping", "Chaud"),
    ("Akermoud", "Marrakesh-Safi", "Nature", "Chaud"),
    ("Bht", "Marrakesh-Safi", "Nature", "Chaud"),
    ("Khamis Ouled Hajj", "Marrakesh-Safi", "Nature", "Chaud"),
    ("Khemis Meskala", "Marrakesh-Safi", "Nature", "Chaud"),
    ("Sidi Ishaq", "Marrakesh-Safi", "Nature", "Chaud"),
    ("Sidi M'Hamed Ou Marzouq", "Marrakesh-Safi", "Nature", "Chaud"),
    ("Sidi Kaouki", "Marrakesh-Safi", "Surf", "Désertique")
]

# Helper to generate a basic profile
def generate_city_data(name, region, dest_type, climat):
    return {
        "name": name,
        "region": region,
        "cost_of_living": round(random.uniform(1.5, 3.5), 1),
        "type": dest_type,
        "description": f"Découvrez {name}, une destination magnifique de la région {region}. Idéal pour {dest_type.lower()}.",
        "images": [
            "https://images.unsplash.com/photo-1539020140153-e479b8c22e70?q=80&w=1080&auto=format&fit=crop" 
        ],
        "places": [
            {
                "name": f"Centre ville de {name}",
                "image": "https://images.unsplash.com/photo-1548017198-91e9e8374fad?q=80&w=800&auto=format&fit=crop"
            }
        ],
        "hotels": [
            {
                "name": f"Hôtel {name} Centre",
                "rating": random.randint(3, 5),
                "rooms": [
                    {
                        "type": "Chambre Standard",
                        "price": round(random.uniform(50, 150), 0),
                        "availability": random.randint(5, 50)
                    }
                ]
            }
        ],
        "profile": {
            "Interet": dest_type if dest_type in ["Culture", "Nature", "Sport", "Détente", "Aventure", "Histoire", "Gastronomie", "Shopping"] else "Détente",
            "Climat": climat,
            "Budget": random.randint(800, 3000),
            "Activite": "Détente" # Default, will be varied by randomness in real life but good for baseline
        }
    }

# Process logic
count = 0
for city_info in new_cities_raw:
    name, region, dtype, climat = city_info
    if name not in existing_names:
        new_entry = generate_city_data(name, region, dtype, climat)
        existing_data.append(new_entry)
        existing_names.add(name)
        count += 1
    
    if count >= 120: # Limit to ~100-120 additions
        break

# Write back
with open('morocco_data.json', 'w', encoding='utf-8') as f:
    json.dump(existing_data, f, ensure_ascii=False, indent=4)

print(f"Added {count} new cities to morocco_data.json.")
