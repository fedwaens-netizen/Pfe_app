from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:Kxsd2882@localhost:5432/touristes_db')

with engine.begin() as conn:
    # 1. Fix regions
    conn.execute(text("UPDATE destination SET continent = 'Fès-Meknès' WHERE name = 'Azrou'"))
    conn.execute(text("UPDATE destination SET continent = 'Béni Mellal-Khénifra' WHERE name = 'Beni Mellal'"))
    
    # 2. Clear bad images
    conn.execute(text("DELETE FROM image_cache WHERE query LIKE '%Sidi Bennour%' OR query LIKE '%Bir Tam Tam%' OR url LIKE '%wikipedia%'"))
    conn.execute(text("DELETE FROM destination_images WHERE destination_id IN (SELECT id FROM destination WHERE name IN ('Sidi Bennour', 'Bir Tam Tam')) OR url LIKE '%wikipedia%'"))
    
print('Done updating database.')
