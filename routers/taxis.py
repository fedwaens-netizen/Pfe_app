"""
Taxis Router — Clean API endpoints for taxi booking, history, and cancellation.
All business logic delegated to services/taxi_service.py.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

import db.crud as crud
import db.schemas as schemas
import db.database as database
from db.database import SessionLocal
from routers.auth import get_current_user
from services import taxi_service
from services import sms_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/taxis", tags=["Taxis"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/categories")
async def list_categories():
    """
    Return all available vehicle categories with pricing info.
    Public endpoint — used by the frontend to populate the category selector.
    """
    return taxi_service.get_all_categories()


@router.post("/estimate", response_model=schemas.TaxiEstimateResponse)
async def estimate_taxi_fare(request: schemas.TaxiEstimateRequest):
    """
    Estimate taxi fare and distance based on pickup and destination.
    Public endpoint.
    """
    result = taxi_service.estimate_fare(request.pickup, request.destination, request.vehicle_category)
    return result


@router.post("/book")
async def book_taxi(
    request: schemas.TaxiBookingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: database.User = Depends(get_current_user),
):
    """
    Book a taxi for the authenticated user.
    Persists the booking in the database and sends SMS confirmation.
    """
    result = taxi_service.process_booking(db=db, user_id=current_user.id, request=request)

    # Queue SMS Notification
    msg = f"MoroGo: Votre taxi {result['vehicle']['model']} avec {result['driver']['name']} est confirmé. Code: {result['confirmation_code']}."
    user_phone = current_user.phone if current_user.phone else "+212600000000"
    background_tasks.add_task(sms_service.send_booking_confirmation, user_phone, msg)

    logger.info(
        "Taxi booking %s created — user=%s category=%s fare=%.2f MAD km=%.1f",
        result["confirmation_code"],
        current_user.username,
        request.vehicle_category,
        result["fare"]["final"],
        result["trip"]["estimated_distance_km"],
    )
    return result


@router.get("/history", response_model=List[schemas.TaxiBookingOut])
async def get_taxi_history(
    current_user: database.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all taxi bookings for the authenticated user, most recent first."""
    return crud.get_user_taxi_bookings(db, user_id=current_user.id)


@router.post("/{booking_id}/cancel")
async def cancel_taxi(
    booking_id: int,
    current_user: database.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel a taxi booking by ID (only if it belongs to the current user)."""
    booking, error = crud.cancel_taxi_booking(
        db, booking_id=booking_id, user_id=current_user.id
    )
    if error:
        raise HTTPException(status_code=400, detail=error)

    return {
        "status": "success",
        "message": "Reservation taxi annulee avec succes.",
        "booking_id": booking.id,
        "confirmation_code": booking.confirmation_code,
    }
