"""
Hotel Service — Business logic for hotel search and booking.
Keeps endpoints thin; all domain logic lives here.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
import db.crud as crud
import db.schemas as schemas
import db.database as database


def search_hotels(db: Session, destination: str) -> List[database.Hotel]:
    """
    Search hotels by destination (case-insensitive partial match).
    Returns an empty list if destination is blank.
    """
    if not destination or not destination.strip():
        return []
    return crud.get_hotels_by_destination(db, destination=destination.strip())


def book_room(
    db: Session,
    user_id: int,
    booking: schemas.BookingCreate,
) -> tuple:
    """
    Validate and create a hotel room booking.
    Returns (booking_obj, error_message).
    error_message is None on success.
    """
    from datetime import date

    if booking.end_date <= booking.start_date:
        return None, "La date de départ doit être après la date d'arrivée."

    if booking.start_date < date.today():
        return None, "La date d'arrivée ne peut pas être dans le passé."

    db_booking, error = crud.create_booking(db=db, user_id=user_id, booking=booking)
    return db_booking, error


def get_hotel_by_id(db: Session, hotel_id: int) -> Optional[database.Hotel]:
    """Return a single hotel by its primary key."""
    return db.query(database.Hotel).filter(database.Hotel.id == hotel_id).first()
