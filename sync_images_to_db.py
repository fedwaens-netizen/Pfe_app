import json
from sqlalchemy.orm import Session
from db.database import SessionLocal, Destination, DestinationImage, Place, Base, engine

def sync_images():
    print("Syncing enriched images from morocco_data.json to SQLite database...")
    
    with open('morocco_data.json', 'r', encoding='utf-8') as f:
        morocco_data = json.load(f)
        
    db = SessionLocal()
    try:
        updated_cities = 0
        updated_places = 0
        
        for city_data in morocco_data:
            city_name = city_data['name']
            dest = db.query(Destination).filter(Destination.name == city_name).first()
            
            if not dest:
                # If for some reason the city isn't in DB, skip or we could create it
                continue
                
            # 1. Update City Images
            # For simplicity, we'll clear existing images for this city and add the new ones
            db.query(DestinationImage).filter(DestinationImage.destination_id == dest.id).delete()
            for img_url in city_data.get('images', []):
                db_img = DestinationImage(url=img_url, destination_id=dest.id)
                db.add(db_img)
            
            # 2. Update Places Images
            for place_data in city_data.get('places', []):
                place = db.query(Place).filter(
                    Place.name == place_data['name'], 
                    Place.destination_id == dest.id
                ).first()
                
                if place:
                    place.image_url = place_data.get('image', '')
                    updated_places += 1
                else:
                    # Create place if it doesn't exist? (Optional, init_db.py usually handles this)
                    new_place = Place(
                        name=place_data['name'],
                        image_url=place_data.get('image', ''),
                        destination_id=dest.id
                    )
                    db.add(new_place)
                    updated_places += 1
            
            updated_cities += 1
            if updated_cities % 50 == 0:
                print(f"Processed {updated_cities} cities...")
                db.commit()
        
        db.commit()
        print(f"Successfully synced {updated_cities} cities and {updated_places} places.")
        
    except Exception as e:
        db.rollback()
        print(f"Error during sync: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    sync_images()
