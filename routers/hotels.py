"""
Hotels Router — Clean API endpoints for hotel search and booking.
All business logic delegated to services/hotel_service.py.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

import db.crud as crud
import db.schemas as schemas
import db.database as database
from db.database import SessionLocal
from routers.auth import get_current_user
from services import hotel_service
from services import sms_service
from services.image_service import get_best_destination_image

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/hotels", tags=["Hotels"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/search", response_model=List[schemas.Hotel])
async def search_hotels(
    destination: str = Query(..., min_length=1, description="Destination city name"),
    db: Session = Depends(get_db),
):
    """
    Search hotels by destination (case-insensitive partial match).
    No authentication required — public endpoint.
    """
    hotels = hotel_service.search_hotels(db, destination=destination)
    return hotels

@router.get("/image/{query}")
async def get_hotel_image(query: str, fallback: str = ""):
    """
    Dynamically fetch a high-quality image for a hotel using its name.
    """
    url = get_best_destination_image(query, fallback_query=fallback)
    if not url:
        # Ultimate generic fallback so we never show a broken placeholder
        url = "https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=600&h=400&fit=crop"
    return {"url": url}


@router.get("/{hotel_id}", response_model=schemas.Hotel)
async def get_hotel(
    hotel_id: int,
    db: Session = Depends(get_db),
):
    """Get details for a single hotel by its ID."""
    hotel = hotel_service.get_hotel_by_id(db, hotel_id=hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail=f"Hotel #{hotel_id} not found.")
    return hotel


@router.post("/book", response_model=schemas.Booking)
async def book_hotel(
    booking: schemas.BookingCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: database.User = Depends(get_current_user),
):
    """
    Book a hotel room for the authenticated user.
    Validates date range, checks availability, computes total price.
    """
    db_booking, error_msg = hotel_service.book_room(
        db=db,
        user_id=current_user.id,
        booking=booking,
    )
    if error_msg:
        raise HTTPException(status_code=400, detail=error_msg)

    # Add MoroCoins for hotel booking
    if current_user.moro_coins is None:
        current_user.moro_coins = 0
    current_user.moro_coins += 50
    db.commit()
    db.refresh(current_user)

    # Queue SMS Notification
    room = crud.get_room(db, room_id=booking.room_id)
    hotel_name = room.hotel.name if room and room.hotel else "votre hôtel"
    msg = f"MoroGo: Votre réservation à {hotel_name} du {booking.start_date.strftime('%d/%m')} au {booking.end_date.strftime('%d/%m')} est confirmée."
    
    user_phone = current_user.phone if current_user.phone else "+212600000000"
    background_tasks.add_task(sms_service.send_booking_confirmation, user_phone, msg)

    logger.info(
        "Hotel booking #%s created — user=%s room=%s dates=%s→%s total=%.2f MAD",
        db_booking.id,
        current_user.username,
        booking.room_id,
        booking.start_date,
        booking.end_date,
        db_booking.total_price or 0,
    )
    return db_booking
