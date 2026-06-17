from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

class UserCreate(BaseModel):
    username: str
    email: str
    phone: Optional[str] = None
    password: str

class User(BaseModel):
    id: int
    username: str
    email: str
    phone: Optional[str] = None
    is_admin: bool = False
    moro_coins: int = 0

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenWithUser(Token):
    """Returned by /auth/signin – includes token AND basic user profile."""
    user: "User"

class TokenData(BaseModel):
    username: str | None = None

class RecommendationRequest(BaseModel):
    Age: int = Field(..., gt=0, le=120, description="Age must be between 1 and 120")
    Budget: int = Field(..., gt=0, description="Budget must be positive")
    Interet: str = Field(..., min_length=1)
    activite: str = Field(default="Culture", min_length=1)  # Default value for safety
    Duree: int = Field(..., gt=0, le=60, description="Duration in days, max 60")
    Climat: str = Field(..., min_length=1)
    Saison: str = Field(..., min_length=1)
    Type_Voyage: str = Field(..., min_length=1)
    Type_Destination: str = Field(default="Mixte")
    Region: str = Field(default="Toutes")

class RecommendationLogBase(BaseModel):
    age: int
    budget: float
    interest: str
    duration: int
    climate: str
    destination_type: str
    season: str
    region: str
    type_voyage: str
    predicted_destination: str

class RecommendationLogCreate(RecommendationLogBase):
    pass

class RecommendationLog(RecommendationLogBase):
    id: int
    user_id: int | None = None
    timestamp: date
    
    class Config:
        from_attributes = True

# ─── Hotel Schemas ─────────────────────────────────────────────────
class RoomBase(BaseModel):
    room_type: str
    price: float
    availability: int

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    id: int
    hotel_id: int

    class Config:
        from_attributes = True

class HotelBase(BaseModel):
    name: str
    destination: str
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5 stars")

class HotelCreate(HotelBase):
    pass

class Hotel(HotelBase):
    id: int
    rooms: List[Room] = []

    class Config:
        from_attributes = True

class BookingBase(BaseModel):
    room_id: int
    start_date: date
    end_date: date

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    user_id: int
    total_price: Optional[float] = None
    status: str = "Confirmée"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ─── Taxi Schemas ──────────────────────────────────────────────────
class TaxiEstimateRequest(BaseModel):
    pickup: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    vehicle_category: str = Field(default="petit_taxi")

class TaxiEstimateResponse(BaseModel):
    estimated_km: float
    estimated_duration_min: int
    fare: float
    currency: str = "MAD"

class TaxiBookingRequest(BaseModel):
    """Request body sent by the frontend to book a taxi."""
    pickup: str = Field(..., min_length=1, description="Lieu de prise en charge")
    destination: str = Field(..., min_length=1, description="Destination")
    vehicle_category: str = Field(default="petit_taxi", description="Category: petit_taxi, grand_taxi, vtc_confort, van")
    passengers: int = Field(default=1, ge=1, le=8)
    fare: float = Field(default=0, ge=0, description="Tarif suggéré par l'utilisateur (0 = auto)")

class TaxiBookingCreate(BaseModel):
    """Internal schema used by CRUD to persist a taxi booking."""
    pickup: str
    destination: str
    vehicle_category: str
    driver_name: str
    vehicle_model: str
    vehicle_color: str
    vehicle_plate: str
    estimated_km: float
    estimated_duration_min: int
    fare: float
    passengers: int = 1
    confirmation_code: str

class TaxiBookingOut(BaseModel):
    """Returned from DB queries for taxi bookings."""
    id: int
    pickup: str
    destination: str
    vehicle_category: str
    driver_name: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_color: Optional[str] = None
    vehicle_plate: Optional[str] = None
    estimated_km: Optional[float] = None
    estimated_duration_min: Optional[int] = None
    fare: float
    passengers: int = 1
    confirmation_code: Optional[str] = None
    status: str = "Confirmée"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ─── Destination Schemas ───────────────────────────────────────────
class PlaceOut(BaseModel):
    name: str
    image_url: Optional[str] = None
    description: Optional[str] = None
    
    class Config:
        from_attributes = True

class DestinationImageOut(BaseModel):
    url: str
    caption: Optional[str] = None
    
    class Config:
        from_attributes = True

class DestinationOut(BaseModel):
    id: int
    name: str
    continent: str  # Region
    cost_of_living: float
    destination_type: str
    description: Optional[str] = None
    images: List[DestinationImageOut] = []
    places: List[PlaceOut] = []
    
    class Config:
        from_attributes = True

class DestinationListItem(BaseModel):
    id: int
    name: str
    continent: str
    destination_type: str
    images: List[DestinationImageOut] = []
    
    class Config:
        from_attributes = True

# ─── Payment Schemas ───────────────────────────────────────────────
class PaymentRequest(BaseModel):
    amount: float
    currency: str = "MAD"
    method: str = Field(..., description="Method of payment: 'card' or 'paypal'")
    service: str = Field(..., description="Service being paid for: 'taxi' or 'hotel'")

class PaymentResponse(BaseModel):
    status: str
    transaction_id: str
    message: str
