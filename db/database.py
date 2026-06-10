import os
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv
from datetime import date, datetime

from core.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    bookings = relationship("Booking", back_populates="user")
    taxi_bookings = relationship("TaxiBooking", back_populates="user")

class Hotel(Base):
    __tablename__ = "hotels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    destination = Column(String, index=True, nullable=False)
    rating = Column(Integer, nullable=False)
    rooms = relationship("Room", back_populates="hotel")

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    room_type = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    availability = Column(Integer, nullable=False)
    hotel = relationship("Hotel", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_price = Column(Float, nullable=True)  # price_per_night * num_nights
    status = Column(String, default="Confirmée") # Confirmée, Annulée
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")

class TaxiBooking(Base):
    __tablename__ = "taxi_bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pickup = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    vehicle_category = Column(String, nullable=False)   # petit_taxi, grand_taxi, vtc_confort, van
    driver_name = Column(String)
    vehicle_model = Column(String)
    vehicle_color = Column(String)
    vehicle_plate = Column(String)
    estimated_km = Column(Float)
    estimated_duration_min = Column(Integer)
    fare = Column(Float, nullable=False)
    passengers = Column(Integer, default=1)
    confirmation_code = Column(String, unique=True, index=True)
    status = Column(String, default="Confirmée")        # Confirmée, En cours, Terminée, Annulée
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="taxi_bookings")

class Destination(Base):
    __tablename__ = "destination"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    continent = Column(String) # Now acts as Region (e.g., 'North', 'Atlas')
    cost_of_living = Column(Float)
    destination_type = Column(String)
    description = Column(String, nullable=True)
    
    tourism_data = relationship('TourismeData', backref='destination', lazy=True)
    images = relationship("DestinationImage", back_populates="destination", cascade="all, delete-orphan")
    places = relationship("Place", back_populates="destination", cascade="all, delete-orphan")

class DestinationImage(Base):
    __tablename__ = "destination_images"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    caption = Column(String, nullable=True)
    destination_id = Column(Integer, ForeignKey("destination.id"), nullable=False)
    
    destination = relationship("Destination", back_populates="images")

class Place(Base):
    __tablename__ = "places"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    destination_id = Column(Integer, ForeignKey("destination.id"), nullable=False)
    
    destination = relationship("Destination", back_populates="places")

class TourismeData(Base):
    __tablename__ = "tourisme_data"
    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer)
    budget = Column(Float)
    interest = Column(String)
    duration = Column(Integer)
    climate = Column(String)
    season = Column(String)  # Added: Saison field
    destination_id = Column(Integer, ForeignKey('destination.id'), nullable=False)

class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nullable for anonymous users
    
    # Input features
    age = Column(Integer)
    budget = Column(Float)
    interest = Column(String)
    duration = Column(Integer)
    climate = Column(String)
    continent = Column(String)
    destination_type = Column(String)
    season = Column(String)
    type_voyage = Column(String)
    region = Column(String)
    
    # Prediction
    predicted_destination = Column(String)
    
    # Metadata
    timestamp = Column(Date, default=date.today) # Simple date or DateTime if needed
    
    user = relationship("User")

