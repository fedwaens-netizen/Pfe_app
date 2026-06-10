"""
Taxi Service — Business logic + driver/vehicle data for taxi bookings.
All domain data and computation are isolated here, keeping the router thin.
"""
import random
from sqlalchemy.orm import Session
from db import schemas, crud

# ─── Driver Pool ──────────────────────────────────────────────────
_MOROCCAN_DRIVERS = [
    {"name": "Youssef El Mansouri", "rating": 4.9, "trips": 1843},
    {"name": "Hassan Benali",        "rating": 4.8, "trips": 2210},
    {"name": "Rachid Ouazzani",      "rating": 4.7, "trips": 987},
    {"name": "Khalid Tazi",          "rating": 4.9, "trips": 3102},
    {"name": "Omar Benjelloun",      "rating": 4.6, "trips": 654},
    {"name": "Mehdi Cherkaoui",      "rating": 5.0, "trips": 421},
    {"name": "Abdelhak Filali",      "rating": 4.8, "trips": 1567},
    {"name": "Noureddine Skalli",    "rating": 4.7, "trips": 2089},
    {"name": "Samir Berrada",        "rating": 4.8, "trips": 1234},
    {"name": "Amine El Fassi",       "rating": 4.9, "trips": 2876},
]

# ─── Vehicle Categories ───────────────────────────────────────────
VEHICLE_CATEGORIES = {
    "petit_taxi": {
        "label": "Petit Taxi",
        "models": ["Dacia Logan", "Renault Symbol", "Fiat Tipo", "Hyundai Accent"],
        "colors": ["Rouge", "Beige", "Bleu"],
        "base_fare": 2.50,
        "per_km": 2.20,
        "description": "Pour trajets courts en ville",
        "capacity": 3,
    },
    "grand_taxi": {
        "label": "Grand Taxi",
        "models": ["Mercedes W124", "Mercedes W123", "Peugeot 504", "Mercedes Vito"],
        "colors": ["Beige", "Blanc", "Gris"],
        "base_fare": 5.00,
        "per_km": 3.50,
        "description": "Trajets inter-villes confortables",
        "capacity": 6,
    },
    "vtc_confort": {
        "label": "VTC Confort",
        "models": ["Toyota Camry", "Volkswagen Passat", "Peugeot 508", "Hyundai Sonata"],
        "colors": ["Noir", "Gris Fonce", "Blanc"],
        "base_fare": 8.00,
        "per_km": 4.50,
        "description": "Confort premium, chauffeur prive",
        "capacity": 4,
    },
    "van": {
        "label": "Van / Minibus",
        "models": ["Mercedes Sprinter", "Ford Transit", "Renault Master", "Peugeot Boxer"],
        "colors": ["Blanc", "Gris", "Bleu"],
        "base_fare": 15.00,
        "per_km": 6.00,
        "description": "Ideal pour groupes et familles",
        "capacity": 8,
    },
}


def get_all_categories() -> list:
    """Return a serializable list of all vehicle categories."""
    return [
        {
            "key": key,
            "label": cat["label"],
            "description": cat["description"],
            "capacity": cat["capacity"],
            "base_fare": cat["base_fare"],
            "per_km": cat["per_km"],
        }
        for key, cat in VEHICLE_CATEGORIES.items()
    ]


def _generate_plate() -> str:
    """Generate a Moroccan license plate e.g. '12345 A 21'."""
    return f"{random.randint(10000, 99999)} {random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')} {random.randint(1, 92)}"


def _generate_confirmation_code() -> str:
    return f"TX-{random.randint(100000, 999999)}"


def estimate_fare(pickup: str, destination: str, vehicle_category: str) -> dict:
    """Pseudo-deterministic distance estimator based on strings."""
    import hashlib
    hash_str = f"{pickup.lower().strip()}-{destination.lower().strip()}"
    hash_num = int(hashlib.md5(hash_str.encode()).hexdigest(), 16)
    
    # Distance between 2.0 and 50.0 km
    estimated_km = round(2.0 + (hash_num % 480) / 10.0, 1)
    estimated_duration_min = round(estimated_km * 2.2 + 5)
    
    category_key = vehicle_category if vehicle_category in VEHICLE_CATEGORIES else "petit_taxi"
    category = VEHICLE_CATEGORIES[category_key]
    
    fare = round(category["base_fare"] + category["per_km"] * estimated_km, 2)
    
    return {
        "estimated_km": estimated_km,
        "estimated_duration_min": estimated_duration_min,
        "fare": fare,
        "currency": "MAD"
    }


def process_booking(
    db: Session,
    user_id: int,
    request: schemas.TaxiBookingRequest,
) -> dict:
    """
    Core business logic for a taxi booking:
    1. Resolve vehicle category (fallback to petit_taxi if invalid)
    2. Estimate distance and compute fare
    3. Pick a random driver
    4. Persist to DB via CRUD
    5. Return the full response dict for the API
    """
    # Resolve category
    category_key = request.vehicle_category if request.vehicle_category in VEHICLE_CATEGORIES else "petit_taxi"
    category = VEHICLE_CATEGORIES[category_key]

    # Validate passenger count vs capacity
    passengers = min(request.passengers, category["capacity"])

    # Simulate distance using deterministic estimator
    estimation = estimate_fare(request.pickup, request.destination, category_key)
    estimated_km = estimation["estimated_km"]
    estimated_duration_min = estimation["estimated_duration_min"]
    calculated_fare = estimation["fare"]

    # Fare calculation
    suggested = request.fare if request.fare > 0 else None
    final_fare = suggested if (suggested and suggested >= calculated_fare * 0.8) else calculated_fare

    # Driver & vehicle
    driver = random.choice(_MOROCCAN_DRIVERS)
    vehicle_model = random.choice(category["models"])
    vehicle_color = random.choice(category["colors"])
    vehicle_plate = _generate_plate()
    confirmation_code = _generate_confirmation_code()
    wait_time = random.randint(3, 15)

    # Persist to DB
    taxi_create = schemas.TaxiBookingCreate(
        pickup=request.pickup,
        destination=request.destination,
        vehicle_category=category_key,
        driver_name=driver["name"],
        vehicle_model=vehicle_model,
        vehicle_color=vehicle_color,
        vehicle_plate=vehicle_plate,
        estimated_km=estimated_km,
        estimated_duration_min=estimated_duration_min,
        fare=final_fare,
        passengers=passengers,
        confirmation_code=confirmation_code,
    )
    db_booking = crud.create_taxi_booking(db=db, user_id=user_id, taxi=taxi_create)

    # Build full API response
    return {
        "status": "success",
        "booking_id": db_booking.id,
        "confirmation_code": confirmation_code,
        "message": f"Chauffeur trouve ! Votre trajet de {request.pickup} a {request.destination} est confirme.",
        "driver": {
            "name": driver["name"],
            "rating": driver["rating"],
            "trips": driver["trips"],
        },
        "vehicle": {
            "category": category["label"],
            "model": vehicle_model,
            "color": vehicle_color,
            "plate": vehicle_plate,
            "capacity": category["capacity"],
            "description": category["description"],
        },
        "trip": {
            "pickup": request.pickup,
            "destination": request.destination,
            "estimated_distance_km": estimated_km,
            "estimated_duration_min": estimated_duration_min,
            "estimated_arrival_min": wait_time,
        },
        "fare": {
            "calculated": calculated_fare,
            "suggested": suggested,
            "final": final_fare,
            "currency": "MAD",
        },
    }
