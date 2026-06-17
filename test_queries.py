import sys
import os
sys.path.append(os.getcwd())

from datetime import datetime, timedelta
from sqlalchemy import func
from db.database import SessionLocal, User, Booking, TaxiBooking

db = SessionLocal()

# Recent bookings (last 5)
recent_hotels = db.query(Booking).order_by(Booking.created_at.desc()).limit(5).all()
recent_taxis = db.query(TaxiBooking).order_by(TaxiBooking.created_at.desc()).limit(5).all()

# Combine and sort by date
recent_combined = []
for h in recent_hotels:
    # Need to fetch related user? The API doesn't serialize objects directly without models, so we create dicts.
    user = h.user
    username = user.username if user else "Inconnu"
    room_type = h.room.room_type if h.room else "Chambre"
    hotel_name = h.room.hotel.name if (h.room and h.room.hotel) else "Hôtel"
    recent_combined.append({
        "type": "hotel",
        "title": f"Réservation Hôtel: {hotel_name} ({room_type})",
        "user": username,
        "amount": h.total_price or 0,
        "date": h.created_at.isoformat() if h.created_at else None,
        "status": h.status
    })

for t in recent_taxis:
    user = t.user
    username = user.username if user else "Inconnu"
    recent_combined.append({
        "type": "taxi",
        "title": f"Course Taxi: {t.pickup} -> {t.destination}",
        "user": username,
        "amount": t.fare or 0,
        "date": t.created_at.isoformat() if t.created_at else None,
        "status": t.status
    })

recent_combined.sort(key=lambda x: x["date"] or "", reverse=True)
recent_combined = recent_combined[:5]

print("Recent:", recent_combined)

# Trend data (last 7 days)
trend_data = []
for i in range(6, -1, -1):
    target_date = (datetime.utcnow() - timedelta(days=i)).date()
    
    # Hotel revenue
    h_rev = db.query(func.sum(Booking.total_price)).filter(func.date(Booking.created_at) == target_date).scalar() or 0
    h_count = db.query(Booking).filter(func.date(Booking.created_at) == target_date).count()
    
    # Taxi revenue
    t_rev = db.query(func.sum(TaxiBooking.fare)).filter(func.date(TaxiBooking.created_at) == target_date).scalar() or 0
    t_count = db.query(TaxiBooking).filter(func.date(TaxiBooking.created_at) == target_date).count()
    
    trend_data.append({
        "date": target_date.strftime("%d/%m"),
        "revenue": h_rev + t_rev,
        "bookings": h_count + t_count
    })

print("Trend:", trend_data)
