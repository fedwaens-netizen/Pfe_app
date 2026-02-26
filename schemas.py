from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class User(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class RecommendationRequest(BaseModel):
    Age: int = Field(..., gt=0, le=120, description="Age must be between 1 and 120")
    Budget: int = Field(..., gt=0, description="Budget must be positive")
    Interet: str = Field(..., min_length=1)
    Duree: int = Field(..., gt=0, le=60, description="Duration in days, max 60")
    Climat: str = Field(..., min_length=1)
    Saison: str = Field(..., min_length=1)
    Type_Destination: str = Field(default="Mixte")

class RecommendationLogBase(BaseModel):
    age: int
    budget: float
    interest: str
    duration: int
    climate: str
    destination_type: str
    season: str
    predicted_destination: str

class RecommendationLogCreate(RecommendationLogBase):
    pass

class RecommendationLog(RecommendationLogBase):
    id: int
    user_id: int | None = None
    timestamp: date
    
    class Config:
        from_attributes = True

# Schemas for Hotel, Room, and Booking
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

    class Config:
        from_attributes = True

# Schemas for Destination API
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
    
    class Config:
        from_attributes = True
