import pandas as pd
import json
from database import Base, engine, SessionLocal
from database import Hotel, Room, Destination, TourismeData, DestinationImage, Place

def init_db():
    print("Dropping and recreating all tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # --- Populate Destinations from JSON ---
        try:
            print("Loading morocco_data.json...")
            with open('morocco_data.json', 'r', encoding='utf-8') as f:
                morocco_data = json.load(f)
            
            # Populate Destinations, Images, and Places
            dest_mapping = {}
            for city in morocco_data:
                # Create Destination
                dest = Destination(
                    name=city['name'],
                    continent=city['region'], # Mapping Region to Continent column
                    cost_of_living=city['cost_of_living'],
                    destination_type=city['type'],
                    description=city['description']
                )
                db.add(dest)
                db.flush() # Flush to get the ID
                dest_mapping[city['name']] = dest.id
                
                # Add Images
                for img_url in city['images']:
                    db_img = DestinationImage(
                        url=img_url,
                        destination_id=dest.id
                    )
                    db.add(db_img)
                
                # Add Places
                for place in city['places']:
                    db_place = Place(
                        name=place['name'],
                        image_url=place['image'],
                        destination_id=dest.id
                    )
                    db.add(db_place)
            
            db.commit()
            print(f"Destinations table populated with {len(morocco_data)} cities and their places/images.")

            print("Loading tourisme_dataset.csv (Generated)...")
            # Ensure the dataset exists, if not generate it first (user should run generate_dataset.py)
            try:
                tourisme_df = pd.read_csv('tourisme_dataset.csv')
            except FileNotFoundError:
                print("Dataset not found. Please run generate_dataset.py first.")
                return 

            tourisme_df['Destination'] = tourisme_df['Destination'].str.strip()
            
            success_count = 0
            miss_count = 0
            
            for _, row in tourisme_df.iterrows():
                dest_id = dest_mapping.get(row['Destination'])
                if dest_id:
                    data = TourismeData(
                        age=row['Age'],
                        budget=row['Budget'],
                        interest=row['Interet'],
                        duration=row['Duree'],
                        climate=row['Climat'],
                        season=row['Saison'],
                        destination_id=dest_id
                    )
                    db.add(data)
                    success_count += 1
                else:
                    miss_count += 1
            
            db.commit()
            print(f"TourismeData table populated with {success_count} rows.")
            if miss_count > 0:
                print(f"WARNING: {miss_count} rows skipped due to missmatch.")

        except Exception as e:
            print(f"Error during population: {e}")

        # --- Populate Hotels from JSON ---
        print("Populating hotels for all cities...")
        hotel_count = 0
        room_count = 0
        for city in morocco_data:
            city_name = city['name']
            hotels = city.get('hotels', [])
            for h in hotels:
                hotel = Hotel(name=h['name'], destination=city_name, rating=h['rating'])
                db.add(hotel)
                db.flush()  # Get hotel.id
                
                for r in h.get('rooms', []):
                    room = Room(
                        hotel_id=hotel.id,
                        room_type=r['type'],
                        price=r['price'],
                        availability=r['availability']
                    )
                    db.add(room)
                    room_count += 1
                hotel_count += 1
        
        db.commit()
        print(f"Hotels: {hotel_count} hotels, {room_count} rooms added.")

        print("Database initialized and populated successfully.")

    finally:
        db.close()

if __name__ == "__main__":
    init_db()

