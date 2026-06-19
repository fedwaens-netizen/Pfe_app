import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

TOP_CITIES = {
    "Marrakech": "https://images.unsplash.com/photo-1597211684565-dca64d728560?w=800&q=80", # Koutoubia
    "Fes": "https://images.unsplash.com/photo-1554228968-3e4b77f98e72?w=800&q=80", # Fes medina
    "Chefchaouen": "https://images.unsplash.com/photo-1552084113-fbc10d297ff6?w=800&q=80", # Blue city
    "Ifrane": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Ifrane_Lion.jpg/800px-Ifrane_Lion.jpg", # Lion d'Ifrane
    "Casablanca": "https://images.unsplash.com/photo-1577180491035-71578e9bda53?w=800&q=80", # Hassan II Mosque
    "Rabat": "https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=800&q=80", # Hassan Tower
    "Tanger": "https://images.unsplash.com/photo-1583084323267-33e5c9429074?w=800&q=80", # Tangier
    "Agadir": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Agadir_Beach.jpg/800px-Agadir_Beach.jpg", # Agadir beach
    "Essaouira": "https://images.unsplash.com/photo-1551043047-1d2adf00f3fd?w=800&q=80", # Essaouira
    "Dakhla": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Dakhla_Bay.jpg/800px-Dakhla_Bay.jpg", # Dakhla
    "Merzouga": "https://images.unsplash.com/photo-1521503373516-701d51de56b4?w=800&q=80", # Sahara
    "Ouarzazate": "https://images.unsplash.com/photo-1580979601614-23ee36916fb2?w=800&q=80", # Ait Benhaddou
    "Meknes": "https://images.unsplash.com/photo-1662483842602-54070a969e77?w=800&q=80", # Meknes
    "Tetouan": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Tetouan_Medina.jpg/800px-Tetouan_Medina.jpg"
}

with engine.connect() as conn:
    # 1. Update top cities
    for city, url in TOP_CITIES.items():
        conn.execute(text(f"""
            UPDATE destination_images 
            SET url = '{url}' 
            WHERE destination_id IN (SELECT id FROM destination WHERE name = '{city}')
        """))
        print(f"Updated {city}")
        conn.commit()

    # 2. Fix the remaining duplicated images to use a variety of Moroccan landscapes based on ID
    GENERIC = [
        "https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=800&q=80",
        "https://images.unsplash.com/photo-1489749798305-4fea3ae63d43?w=800&q=80",
        "https://images.unsplash.com/photo-1512100356356-de1b84283e18?w=800&q=80",
        "https://images.unsplash.com/photo-1549487532-a5e2f7596b61?w=800&q=80",
        "https://images.unsplash.com/photo-1535086181678-5a5c4d23aa7d?w=800&q=80",
        "https://images.unsplash.com/photo-1548680324-4903ebc2ec0f?w=800&q=80",
        "https://images.unsplash.com/photo-1553531087-b25a0b9a68ab?w=800&q=80"
    ]
    
    city_names_str = ",".join([f"'{c}'" for c in TOP_CITIES.keys()])
    res = conn.execute(text(f"SELECT id FROM destination WHERE name NOT IN ({city_names_str})"))
    ids = [r[0] for r in res.fetchall()]
    
    for dest_id in ids:
        idx = dest_id % len(GENERIC)
        url = GENERIC[idx]
        conn.execute(text(f"UPDATE destination_images SET url = '{url}' WHERE destination_id = {dest_id}"))
    
    conn.commit()
    print(f"Updated {len(ids)} generic destinations with variety.")

print("Done!")
