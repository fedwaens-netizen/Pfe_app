from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# import pandas as pd
import joblib
from sqlalchemy.orm import Session
from pathlib import Path
# import requests
import os
import logging
# from cachetools import TTLCache
from typing import List, Optional
# from datetime import date
import random
import numpy as np
from contextlib import asynccontextmanager

# ─── New modular router imports ───────────────────────────────────
from routers.auth import router as auth_router, get_current_user, get_optional_user
from routers.recommendation import router as recommend_router
from routers.currency import router as currency_router
from routers.bookings import router as bookings_router
from routers.hotels import router as hotels_router
from routers.taxis import router as taxis_router
from routers.payment import router as payment_router
from routers.chat import router as chat_router

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

import db.crud as crud
import db.database as database
import db.schemas as schemas
#from core import security
from db.database import SessionLocal, engine

# Create all tables
database.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── ML Model Lifespan ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models on startup
    logger.info("Loading ML models...")
    try:
        app.state.zone_model = joblib.load(os.path.join(BASE_DIR, 'zone_model.joblib'))
        app.state.model = joblib.load(os.path.join(BASE_DIR, 'recommendation_model.joblib'))
        app.state.preprocessor = joblib.load(os.path.join(BASE_DIR, 'preprocessor.joblib'))
        app.state.label_encoder = joblib.load(os.path.join(BASE_DIR, 'label_encoder.joblib'))
        app.state.zone_encoder = joblib.load(os.path.join(BASE_DIR, 'zone_encoder.joblib'))
        logger.info("ML models loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load ML models: {e}")
        app.state.zone_model = None
        app.state.model = None
        app.state.preprocessor = None
        app.state.label_encoder = None
        app.state.zone_encoder = None
    
    yield  # Application runs here
    
    # Cleanup on shutdown (if necessary)
    logger.info("Shutting down and cleaning up...")
    app.state.zone_model = None
    app.state.model = None
    app.state.preprocessor = None
    app.state.label_encoder = None
    app.state.zone_encoder = None


app = FastAPI(
    title="Maroc Tourisme API",
    description="API de recommandation de destinations touristiques au Maroc.",
    version="1.0.0",
    lifespan=lifespan
)

# ─── CORS Configuration for React Frontend ─────────────────────────
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS, images, favicon)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(BASE_DIR, "static", "favicon.ico"))

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if exc.__class__.__name__ == 'RequestValidationError': logger.error(f'422 Error details: {exc.errors()}\\nBody: {exc.body}')

    logger.error(f"Global exception caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "message": str(exc)},
    )

# ─── Register routers ─────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(recommend_router)
app.include_router(currency_router)
app.include_router(bookings_router)
app.include_router(hotels_router)
app.include_router(taxis_router)
app.include_router(payment_router)
app.include_router(chat_router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

# (Moved caching to services/currency_service.py)

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Pydantic models for request bodies
# (Moved to schemas.py)

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# get_current_user is now imported from routers.auth (shared dependency)
# Recommendation logic and endpoints are now in routers/recommendation.py

# (Moved bookings endpoints to routers/bookings.py)

# Page serving endpoints
@app.get("/destination/{name}")
def destination_page(
    request: Request, 
    name: str, 
    db: Session = Depends(get_db), 
    current_user: Optional[database.User] = Depends(get_optional_user)
):
    destination = crud.get_destination_by_name(db, name)
    if not destination:
        # Fallback to 404
        raise HTTPException(status_code=404, detail=f"Destination '{name}' not found")
    return templates.TemplateResponse("destination.html", {"request": request, "destination": destination})

@app.get("/")
def home(request: Request, current_user: Optional[database.User] = Depends(get_optional_user)):
    import json
    
    # Les 12 régions officielles du Maroc
    regions = [
        "Tanger-Tétouan-Al Hoceïma",
        "Région de l'Oriental",
        "Fès-Meknès",
        "Rabat-Salé-Kénitra",
        "Béni Mellal-Khénifra",
        "Casablanca-Settat",
        "Marrakech-Safi",
        "Drâa-Tafilalet",
        "Souss-Massa",
        "Guelmim-Oued Noun",
        "Laâyoune-Sakia El Hamra",
        "Dakhla-Oued Ed-Dahab"
    ]

    interests = ['Culture', 'Nature', 'Détente', 'Aventure', 'Sport', 'Shopping', 'Gastronomie', 'Histoire']
    climates = ['Chaud', 'Tempéré', 'Froid', 'Désertique']
    saisons = ['Printemps', 'Été', 'Automne', 'Hiver']
    travel_types = ['Solo', 'Couple', 'Famille', 'Amis']
    destination_types = ['Ville', 'Plage', 'Montagne', 'Désert']

    return templates.TemplateResponse("index.html", {
        "request": request,
        "regions": regions,
        "interests": interests,
        "climates": climates,
        "saisons": saisons,
        "travel_types": travel_types,
        "destination_types": destination_types,
    })


@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/hotels")
def hotels_page(request: Request, current_user: Optional[database.User] = Depends(get_optional_user)):
    return templates.TemplateResponse("hotels.html", {"request": request})

@app.get("/currency")
def currency_page(request: Request, current_user: Optional[database.User] = Depends(get_optional_user)):
    return templates.TemplateResponse("currency_converter.html", {"request": request})

@app.get("/taxis")
def taxis_page(request: Request, current_user: Optional[database.User] = Depends(get_optional_user)):
    return templates.TemplateResponse("taxis.html", {"request": request})

# my-bookings page moved to routers/bookings.py

# API Endpoints for services

# Destination API
@app.get("/api/destinations", response_model=List[schemas.DestinationListItem])
def list_destinations(
    db: Session = Depends(get_db), 
    current_user: database.User = Depends(get_current_user)
):
    """List all available Moroccan destinations."""
    destinations = crud.get_all_destinations(db)
    return destinations

@app.get("/api/destinations/{name}", response_model=schemas.DestinationOut)
def get_destination(
    name: str, 
    db: Session = Depends(get_db), 
    current_user: database.User = Depends(get_current_user)
):
    """Get detailed information about a specific destination."""
    destination = crud.get_destination_by_name(db, name)
    if not destination:
        raise HTTPException(status_code=404, detail=f"Destination '{name}' not found")
    return destination

# User History API (Handled in routers/recommendation.py)

# Hotel API (Handled in routers/hotels.py)

# Taxi API (Handled in routers/taxis.py)

# Locale endpoint
@app.get("/locales/{lng}.json")
async def read_locale(lng: str):
    # Handle empty or invalid language codes by defaulting to English
    if not lng or lng.strip() == "":
        lng = "en"
    file_path = f"locales/{lng}.json"
    if not Path(file_path).is_file():
        # Fallback to English if requested language doesn't exist
        file_path = "locales/en.json"
        if not Path(file_path).is_file():
            raise HTTPException(status_code=404, detail="Locale not found")
    return FileResponse(file_path)

# (Moved currency conversion endpoints to routers/currency.py)
