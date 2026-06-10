from sqlalchemy.orm import Session
from datetime import date as date_type
import unicodedata
import db.schemas as schemas
import db.database as database
from core.security import get_password_hash

# ─── User CRUD ────────────────────────────────────────────────────
def get_user(db: Session, user_id: int):
    return db.query(database.User).filter(database.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(database.User).filter(database.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(database.User).filter(database.User.email == email).first()

def get_user_by_phone(db: Session, phone: str):
    return db.query(database.User).filter(database.User.phone == phone).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = database.User(username=user.username, email=user.email, phone=user.phone, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, username: str, new_password: str):
    user = get_user_by_username(db, username)
    if user:
        hashed_password = get_password_hash(new_password)
        user.password_hash = hashed_password
        db.commit()
        db.refresh(user)
        return user
    return None

def update_user_password_by_phone(db: Session, phone: str, new_password: str):
    user = get_user_by_phone(db, phone)
    if user:
        hashed_password = get_password_hash(new_password)
        user.password_hash = hashed_password
        db.commit()
        db.refresh(user)
        return user
    return None

# ─── Hotel CRUD ───────────────────────────────────────────────────
def get_hotels_by_destination(db: Session, destination: str):
    return db.query(database.Hotel).filter(database.Hotel.destination.ilike(f"%{destination}%")).all()

def create_hotel(db: Session, hotel: schemas.HotelCreate):
    db_hotel = database.Hotel(**hotel.dict())
    db.add(db_hotel)
    db.commit()
    db.refresh(db_hotel)
    return db_hotel

def get_room(db: Session, room_id: int):
    # Lock the row for update to prevent race conditions
    return db.query(database.Room).filter(database.Room.id == room_id).with_for_update().first()

def create_booking(db: Session, user_id: int, booking: schemas.BookingCreate):
    db_room = get_room(db, room_id=booking.room_id)

    if not db_room:
        db.rollback()
        return None, "Room not found."

    if db_room.availability <= 0:
        db.rollback()
        return None, "No rooms available."

    # Calculate total price based on number of nights
    num_nights = (booking.end_date - booking.start_date).days
    if num_nights <= 0:
        db.rollback()
        return None, "La date de départ doit être après la date d'arrivée."
    total_price = round(db_room.price * num_nights, 2)

    db_room.availability -= 1

    db_booking = database.Booking(
        user_id=user_id,
        room_id=booking.room_id,
        start_date=booking.start_date,
        end_date=booking.end_date,
        total_price=total_price,
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)

    return db_booking, None

def get_user_bookings(db: Session, user_id: int):
    return db.query(database.Booking).filter(
        database.Booking.user_id == user_id
    ).order_by(database.Booking.start_date.desc()).all()

def cancel_booking(db: Session, booking_id: int, user_id: int):
    booking = db.query(database.Booking).filter(
        database.Booking.id == booking_id,
        database.Booking.user_id == user_id
    ).first()

    if not booking:
        return None, "Réservation introuvable."
    
    if booking.status == "Annulée":
        return None, "Cette réservation est déjà annulée."

    # Restore room availability
    room = db.query(database.Room).filter(database.Room.id == booking.room_id).first()
    if room:
        room.availability += 1
    
    booking.status = "Annulée"
    db.commit()
    db.refresh(booking)
    return booking, None

# ─── Taxi CRUD ────────────────────────────────────────────────────
def create_taxi_booking(db: Session, user_id: int, taxi: schemas.TaxiBookingCreate):
    """Persist a new taxi booking in the database."""
    db_taxi = database.TaxiBooking(
        user_id=user_id,
        pickup=taxi.pickup,
        destination=taxi.destination,
        vehicle_category=taxi.vehicle_category,
        driver_name=taxi.driver_name,
        vehicle_model=taxi.vehicle_model,
        vehicle_color=taxi.vehicle_color,
        vehicle_plate=taxi.vehicle_plate,
        estimated_km=taxi.estimated_km,
        estimated_duration_min=taxi.estimated_duration_min,
        fare=taxi.fare,
        passengers=taxi.passengers,
        confirmation_code=taxi.confirmation_code,
    )
    db.add(db_taxi)
    db.commit()
    db.refresh(db_taxi)
    return db_taxi

def get_user_taxi_bookings(db: Session, user_id: int):
    """Return all taxi bookings for a user, most recent first."""
    return db.query(database.TaxiBooking).filter(
        database.TaxiBooking.user_id == user_id
    ).order_by(database.TaxiBooking.created_at.desc()).all()

def cancel_taxi_booking(db: Session, booking_id: int, user_id: int):
    """Cancel a taxi booking if it belongs to the user."""
    booking = db.query(database.TaxiBooking).filter(
        database.TaxiBooking.id == booking_id,
        database.TaxiBooking.user_id == user_id
    ).first()

    if not booking:
        return None, "Réservation introuvable."
    if booking.status == "Annulée":
        return None, "Cette réservation est déjà annulée."

    booking.status = "Annulée"
    db.commit()
    db.refresh(booking)
    return booking, None

# ─── Recommendation CRUD ──────────────────────────────────────────
def create_recommendation_history(db: Session, recommendation: schemas.RecommendationLogCreate, user_id: int = None):
    db_rec = database.RecommendationHistory(
        user_id=user_id,
        age=recommendation.age,
        budget=recommendation.budget,
        interest=recommendation.interest,
        duration=recommendation.duration,
        climate=recommendation.climate,
        continent=recommendation.region,
        destination_type=recommendation.destination_type,
        season=recommendation.season,
        type_voyage=recommendation.type_voyage,
        predicted_destination=recommendation.predicted_destination
    )
    db.add(db_rec)
    db.commit()
    db.refresh(db_rec)
    return db_rec

# ─── Destination CRUD ─────────────────────────────────────────────
def get_all_destinations(db: Session):
    return db.query(database.Destination).all()

from services.image_service import get_best_destination_image

def get_destination_by_name(db: Session, name: str):
    # 1. Exact match
    destination = db.query(database.Destination).filter(database.Destination.name == name).first()
    
    # 2. Case-insensitive match
    if not destination:
        destination = db.query(database.Destination).filter(database.Destination.name.ilike(name)).first()
        
    # 3. Match without accents (e.g. if input is Fès but DB is Fes)
    if not destination:
        normalized_name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('utf-8')
        if normalized_name != name:
            destination = db.query(database.Destination).filter(database.Destination.name.ilike(normalized_name)).first()
    
    # Dynamically fetch and attach a high-quality image if it has none
    if destination and not destination.images:
        # Use destination.name from DB as it might be better formatted
        img_url = get_best_destination_image(destination.name)
        if img_url:
            new_image = database.DestinationImage(url=img_url, destination_id=destination.id)
            db.add(new_image)
            db.commit()
            db.refresh(destination)
            
    return destination

# ─── User Recommendation History ─────────────────────────────────
def get_user_recommendations(db: Session, user_id: int, limit: int = 20):
    return db.query(database.RecommendationHistory).filter(
        database.RecommendationHistory.user_id == user_id
    ).order_by(database.RecommendationHistory.timestamp.desc()).limit(limit).all()

