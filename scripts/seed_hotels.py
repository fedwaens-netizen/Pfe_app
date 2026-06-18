"""
Script to seed hotels and rooms into the database from morocco_data.json.
Generates multiple realistic room types per hotel.
"""
import json
import random
from db.database import Base, engine, SessionLocal, Hotel, Room, Booking

# Room type configurations per star rating
ROOM_TEMPLATES = {
    1: [
        {"type": "Chambre Standard", "price_factor": 1.0, "availability": 20},
    ],
    2: [
        {"type": "Chambre Standard", "price_factor": 1.0, "availability": 15},
        {"type": "Chambre Double", "price_factor": 1.4, "availability": 8},
    ],
    3: [
        {"type": "Chambre Standard", "price_factor": 1.0, "availability": 15},
        {"type": "Chambre Double", "price_factor": 1.4, "availability": 10},
        {"type": "Chambre Supérieure", "price_factor": 1.8, "availability": 6},
    ],
    4: [
        {"type": "Chambre Standard", "price_factor": 1.0, "availability": 12},
        {"type": "Chambre Deluxe", "price_factor": 1.5, "availability": 8},
        {"type": "Junior Suite", "price_factor": 2.2, "availability": 5},
        {"type": "Suite Executive", "price_factor": 3.0, "availability": 3},
    ],
    5: [
        {"type": "Chambre Deluxe", "price_factor": 1.0, "availability": 10},
        {"type": "Suite Junior", "price_factor": 1.8, "availability": 6},
        {"type": "Suite Prestige", "price_factor": 2.8, "availability": 4},
        {"type": "Suite Royale", "price_factor": 4.5, "availability": 2},
    ],
}

def seed_hotels():
    print("Starting hotel seeding...")
    
    with open('morocco_data.json', 'r', encoding='utf-8') as f:
        morocco_data = json.load(f)
    
    db = SessionLocal()
    
    try:
        # Clear existing hotels and rooms
        existing = db.query(Hotel).count()
        if existing > 0:
            print(f"Found {existing} existing hotels. Clearing...")
            # Must delete bookings first (FK constraint)
            bookings_deleted = db.query(Booking).delete()
            print(f"   Deleted {bookings_deleted} existing bookings (FK constraint).")
            db.query(Room).delete()
            db.query(Hotel).delete()
            db.commit()
        
        hotel_count = 0
        room_count = 0
        
        for city in morocco_data:
            city_name = city['name']
            hotels_data = city.get('hotels', [])
            
            if not hotels_data:
                continue
            
            for h in hotels_data:
                hotel_name = h.get('name', 'Hôtel Inconnu')
                rating = h.get('rating', 3)
                
                # Clamp rating to 1-5
                rating = max(1, min(5, rating))
                
                hotel = Hotel(
                    name=hotel_name,
                    destination=city_name,
                    rating=rating
                )
                db.add(hotel)
                db.flush()  # Get hotel.id
                
                # Get base price from JSON data (first room)
                json_rooms = h.get('rooms', [])
                if json_rooms:
                    base_price = json_rooms[0].get('price', 100.0)
                else:
                    # Default base price by star rating
                    default_prices = {1: 30, 2: 60, 3: 100, 4: 180, 5: 350}
                    base_price = default_prices.get(rating, 100)
                
                # Add original room from JSON first (if has unique type)
                if json_rooms and json_rooms[0].get('type'):
                    orig_type = json_rooms[0]['type']
                    orig_price = json_rooms[0]['price']
                    orig_avail = json_rooms[0].get('availability', 10)
                    
                    room = Room(
                        hotel_id=hotel.id,
                        room_type=orig_type,
                        price=round(orig_price, 2),
                        availability=orig_avail
                    )
                    db.add(room)
                    room_count += 1
                
                # Add additional room types from templates
                templates = ROOM_TEMPLATES.get(rating, ROOM_TEMPLATES[3])
                for tmpl in templates:
                    # Skip if same as already added room
                    if json_rooms and tmpl['type'] == json_rooms[0].get('type'):
                        continue
                    
                    # Add slight randomness to price (+/- 10%)
                    price = base_price * tmpl['price_factor']
                    price *= random.uniform(0.9, 1.1)
                    price = round(price, 2)
                    avail = tmpl['availability'] + random.randint(-3, 5)
                    avail = max(1, avail)
                    
                    room = Room(
                        hotel_id=hotel.id,
                        room_type=tmpl['type'],
                        price=price,
                        availability=avail
                    )
                    db.add(room)
                    room_count += 1
                
                hotel_count += 1
        
        db.commit()
        print(f"\n[DONE] Seeding complete!")
        print(f"   Hotels added: {hotel_count}")
        print(f"   Rooms added:  {room_count}")
        
        # Quick stats
        sample = db.query(Hotel).limit(3).all()
        print("\nSample hotels:")
        for h in sample:
            print(f"  {h.name} ({h.destination}) - {h.rating} stars - {len(h.rooms)} rooms")
    
    finally:
        db.close()

if __name__ == "__main__":
    seed_hotels()
