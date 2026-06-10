import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
from datetime import datetime

import db.crud as crud
import db.database as database
from db.database import SessionLocal
from routers.auth import get_current_user, get_optional_user
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# ─── DB Dependency ────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/my-bookings", tags=["Pages"])
def my_bookings_page(request: Request, current_user: Optional[database.User] = Depends(get_optional_user)):
    """Serve the 'My Bookings' HTML page shell."""
    return templates.TemplateResponse("my_bookings.html", {"request": request})

@router.get("/api/my-bookings", tags=["Bookings"])
def get_my_bookings_api(
    current_user: database.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """JSON API to get user bookings (Hotels and Taxis unified)."""
    hotel_bookings = crud.get_user_bookings(db, user_id=current_user.id)
    taxi_bookings = crud.get_user_taxi_bookings(db, user_id=current_user.id)
    
    unified_bookings = []
    
    # 1. Map Hotel Bookings
    for b in hotel_bookings:
        unified_bookings.append({
            "id": b.id,
            "type": "hotel",
            "title": f"Hôtel {b.room.hotel.name} - {b.room.hotel.destination}",
            "subtitle": f"Chambre {b.room.room_type}",
            "sort_date": b.start_date, # For sorting
            "display_date": f"{b.start_date.strftime('%d/%m/%Y')} au {b.end_date.strftime('%d/%m/%Y')}",
            "price": b.total_price if b.total_price else b.room.price,
            "status": b.status
        })
        
    # 2. Map Taxi Bookings
    for t in taxi_bookings:
        unified_bookings.append({
            "id": t.id,
            "type": "taxi",
            "title": f"Taxi : {t.pickup} → {t.destination}",
            "subtitle": f"{t.vehicle_category.replace('_', ' ').title()} - {t.driver_name}",
            "sort_date": t.created_at.date() if t.created_at else datetime.now().date(),
            "display_date": t.created_at.strftime('%d/%m/%Y %H:%M') if t.created_at else "Aujourd'hui",
            "price": t.fare,
            "status": t.status,
            "taxi_code": t.confirmation_code
        })
        
    # 3. Sort chronologically (newest first)
    unified_bookings.sort(key=lambda x: x["sort_date"], reverse=True)
    
    return unified_bookings

@router.post("/api/bookings/{booking_id}/cancel", tags=["Bookings"])
async def cancel_user_booking(
    booking_id: int,
    current_user: database.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """API endpoint to cancel a HOTEL booking."""
    booking, error = crud.cancel_booking(db, booking_id=booking_id, user_id=current_user.id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return {
        "status": "success",
        "message": "Réservation d'hôtel annulée avec succès.",
        "booking_id": booking.id
    }
