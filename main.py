from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from jose import jwt, JWTError
import pandas as pd
import joblib
from sqlalchemy.orm import Session
from pathlib import Path
import requests
import os
from cachetools import TTLCache
from typing import List
from datetime import date
import random
import numpy as np

import crud, database, schemas, security
from database import SessionLocal, engine

# Create all tables
database.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Cache for currency rates (TTL: 1 hour)
currency_cache = TTLCache(maxsize=10, ttl=3600)

# Load models
model = joblib.load('recommendation_model.joblib')
preprocessor = joblib.load('preprocessor.joblib')
label_encoder = joblib.load('label_encoder.joblib')

templates = Jinja2Templates(directory="templates")

# Pydantic models for request bodies
class TaxiBookingRequest(BaseModel):
    pickup: str
    destination: str
    fare: float

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/signup/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

def calculate_relevance_score(rec_request, destination):
    """
    Calculate a relevance score for a destination based on user preferences.
    Higher score = better match. Scores can be negative for poor matches.
    """
    score = 0
    
    # 1. Interest Matching (High Weight: +30 for match, -10 for mismatch)
    interest_map = {
        'Culture': ['Historique', 'Ville'],
        'Nature': ['Montagne', 'Désert', 'Plage'],
        'Plage': ['Plage'],
        'Aventure': ['Désert', 'Montagne'],
        'Ville': ['Ville', 'Historique'],
        'Shopping': ['Ville', 'Historique'],
        'Gastronomie': ['Ville', 'Historique'],
        'Histoire': ['Historique', 'Ville']
    }
    
    related_types = interest_map.get(rec_request.Interet, [])
    
    if destination.destination_type in related_types:
        score += 30  # Strong match
    elif rec_request.Interet == 'Autre':
        score += 5   # Neutral
    else:
        score -= 10  # Mismatch penalty
        
    # 2. Climate Matching (Weight: +20 to -20)
    user_climate_pref = rec_request.Climat.lower()
    dest_type = destination.destination_type
    
    # Hot climate preferences
    if any(kw in user_climate_pref for kw in ['chaud', 'summer', 'été', 'tropical']):
        if dest_type == 'Plage':
            score += 25  # Perfect for hot weather
        elif dest_type == 'Montagne':
            score += 15  # Cooler escape from heat
        elif dest_type == 'Désert':
            score -= 15  # Too hot in desert during summer
        elif dest_type in ['Ville', 'Historique']:
            score += 5   # Neutral
            
    # Cold climate preferences
    elif any(kw in user_climate_pref for kw in ['froid', 'winter', 'hiver', 'cold']):
        if dest_type == 'Désert':
            score += 20  # Pleasant desert in winter
        elif dest_type in ['Ville', 'Historique']:
            score += 15  # Good for winter exploration
        elif dest_type == 'Plage':
            score -= 15  # Too cold for beach
        elif dest_type == 'Montagne':
            score -= 10  # Too cold/snowy
            
    # Temperate/mild preferences  
    elif any(kw in user_climate_pref for kw in ['tempéré', 'mild', 'spring', 'printemps', 'autumn', 'automne']):
        score += 10  # All destinations work for mild weather
            
    # 3. Budget Fit (Weight: +25 to -40)
    estimated_daily_cost = destination.cost_of_living * 35  # Approx daily cost in currency
    user_daily_budget = rec_request.Budget / max(rec_request.Duree, 1)
    
    budget_ratio = user_daily_budget / max(estimated_daily_cost, 1)
    
    if budget_ratio >= 1.5:
        score += 25  # Generous budget
    elif budget_ratio >= 1.0:
        score += 15 + (budget_ratio - 1.0) * 10  # Sufficient budget
    elif budget_ratio >= 0.7:
        score -= 10  # Tight budget
    elif budget_ratio >= 0.5:
        score -= 25  # Very tight
    else:
        score -= 40  # Severely insufficient
        
    # 4. Destination Type Request (Highest Weight: +35 for explicit match)
    if rec_request.Type_Destination and rec_request.Type_Destination not in ["Mixte", ""]:
        if destination.destination_type == rec_request.Type_Destination:
            score += 35  # User explicitly requested this type
        else:
            score -= 15  # User wanted something specific but this isn't it
            
    # 5. Region Bonus (Small boost for matching region)
    if destination.continent == rec_request.Region:
        score += 10
            
    return score

def get_prediction(rec_request, db):
    """
    Hybrid recommendation: ML predicts destination TYPE, heuristic picks the best specific city.
    """
    # 1. Fetch ALL destinations from DB
    all_destinations = crud.get_all_destinations(db)

    if not all_destinations:
        return "Marrakech"

    # 2. Get ML model prediction (predicts DESTINATION TYPE, e.g. 'Plage', 'Montagne')
    predicted_type = None
    try:
        input_df = pd.DataFrame([{
            'age': rec_request.Age,
            'budget': rec_request.Budget,
            'Duree': rec_request.Duree,
            'Interet': rec_request.Interet,
            'Climat': rec_request.Climat,
            'Type_Voyage': 'Solo',
            'Saison': rec_request.Saison,
            'Nationalite': 'Marocain',
            'Activite': rec_request.Interet,
        }])
        processed_input = preprocessor.transform(input_df)
        predicted_type_encoded = model.predict(processed_input)[0]
        predicted_type = label_encoder.inverse_transform([predicted_type_encoded])[0]
    except Exception as e:
        print(f"ML prediction failed, using heuristics only: {e}")

    # 3. Build hybrid scores: ML TYPE boost + Heuristics
    scored_dests = []
    for dest in all_destinations:
        # Heuristic score (budget / climate / interest matching)
        heuristic_score = calculate_relevance_score(rec_request, dest)

        # ML TYPE boost: strong signal when the model agrees on destination type
        ml_type_boost = 0
        if predicted_type and dest.destination_type == predicted_type:
            ml_type_boost = 40  # significant boost for type match

        combined_score = heuristic_score + ml_type_boost

        scored_dests.append({
            'dest': dest,
            'name': dest.name,
            'ml_type_boost': ml_type_boost,
            'heuristic_score': heuristic_score,
            'combined': combined_score
        })

    # 4. Sort by combined score
    scored_dests.sort(key=lambda x: x['combined'], reverse=True)

    # 5. Weighted random selection among top 3 for diversity
    top_n = min(3, len(scored_dests))
    top_candidates = scored_dests[:top_n]
    weights = [max(c['combined'] + 100, 0.1) for c in top_candidates]  # shift to positive
    total_weight = sum(weights)

    if total_weight <= 0:
        return top_candidates[0]['name'] if top_candidates else "Marrakech"

    probabilities = [w / total_weight for w in weights]
    selected_idx = random.choices(range(len(top_candidates)), weights=probabilities, k=1)[0]

    return top_candidates[selected_idx]['name']

@app.post("/api/recommend") 
def recommendation_api(rec_request: schemas.RecommendationRequest, 
                       db: Session = Depends(get_db)):
    try:
        prediction_name = get_prediction(rec_request, db)
        
        # User tracking could be added here similar to web endpoint (optional auth)
        user_id = None
        
        # Log to history
        log_entry = schemas.RecommendationLogCreate(
            age=rec_request.Age,
            budget=rec_request.Budget,
            interest=rec_request.Interet,
            duration=rec_request.Duree,
            climate=rec_request.Climat,
            destination_type=rec_request.Type_Destination,
            season=rec_request.Saison,
            predicted_destination=prediction_name
        )
        saved_log = crud.create_recommendation_history(db, log_entry, user_id=user_id)
        
        # Fetch detailed destination info for response
        destination = db.query(database.Destination).filter(database.Destination.name == prediction_name).first()
        
        response_data = {
            "log_id": saved_log.id,
            "recommendation": {
                "name": prediction_name,
                "description": destination.description if destination else "",
                "images": [img.url for img in destination.images] if destination else [],
                "places": [
                    {"name": p.name, "image": p.image_url} for p in destination.places
                ] if destination else []
            }
        }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        print(f"API Recommendation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend/")
def recommend(request: Request, rec_request: schemas.RecommendationRequest, db: Session = Depends(get_db)):
    try:
        prediction = get_prediction(rec_request, db)
        
        # Attempt to get user if logged in, otherwise None
        # Note: In a real app we'd parse the cookie/token manually if not using Depends(oauth2_scheme) on this endpoint
        # For simplicity, we'll log as anonymous for now if this endpoint doesn't enforce auth
        user_id = None 
        
        # Log to history
        log_entry = schemas.RecommendationLogCreate(
            age=rec_request.Age,
            budget=rec_request.Budget,
            interest=rec_request.Interet,
            duration=rec_request.Duree,
            climate=rec_request.Climat,
            destination_type=rec_request.Type_Destination,
            season=rec_request.Saison,
            predicted_destination=prediction
        )
        crud.create_recommendation_history(db, log_entry, user_id=user_id)
        
        return templates.TemplateResponse("_recommendation_result.html", {"request": request, "recommendation": prediction})
    except Exception as e:
        print(f"Recommendation Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during recommendation.")

@app.get("/my-bookings")
def my_bookings_page(request: Request, current_user: database.User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookings = crud.get_user_bookings(db, user_id=current_user.id)
    return templates.TemplateResponse("my_bookings.html", {"request": request, "bookings": bookings})

# Page serving endpoints
@app.get("/")
def home(request: Request):
    # Updated values for Morocco - all categorical inputs as dropdowns
    regions = ['Centre-Sud', 'Nord-Est', 'Nord', 'Sud-Ouest', 'Sud-Est', 'Ouest']
    interests = ['Culture', 'Nature', 'Détente', 'Aventure', 'Sport', 'Shopping', 'Gastronomie', 'Histoire']
    climates = ['Chaud', 'Tempéré', 'Froid', 'Désertique']
    saisons = ['Printemps', 'Été', 'Automne', 'Hiver']
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "continents": regions,  # Keep variable name for backward compatibility
        "interests": interests,
        "climates": climates,
        "saisons": saisons
    })

@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/hotels")
def hotels_page(request: Request):
    return templates.TemplateResponse("hotels.html", {"request": request})

@app.get("/currency")
def currency_page(request: Request):
    return templates.TemplateResponse("currency_converter.html", {"request": request})

@app.get("/taxis")
def taxis_page(request: Request):
    return templates.TemplateResponse("taxis.html", {"request": request})

# API Endpoints for services

# Destination API
@app.get("/api/destinations", response_model=List[schemas.DestinationListItem])
def list_destinations(db: Session = Depends(get_db)):
    """List all available Moroccan destinations."""
    destinations = crud.get_all_destinations(db)
    return destinations

@app.get("/api/destinations/{name}", response_model=schemas.DestinationOut)
def get_destination(name: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific destination."""
    destination = crud.get_destination_by_name(db, name)
    if not destination:
        raise HTTPException(status_code=404, detail=f"Destination '{name}' not found")
    return destination

# User History API
@app.get("/api/me/recommendations", response_model=List[schemas.RecommendationLog])
def get_my_recommendations(
    current_user: database.User = Depends(get_current_user), 
    db: Session = Depends(get_db),
    limit: int = 20
):
    """Get the current user's recommendation history."""
    recommendations = crud.get_user_recommendations(db, user_id=current_user.id, limit=limit)
    return recommendations

# Hotel API
@app.get("/api/hotels/search", response_model=List[schemas.Hotel])
async def search_hotels(destination: str, db: Session = Depends(get_db)):
    hotels = crud.get_hotels_by_destination(db, destination=destination)
    return hotels

@app.post("/api/hotels/book", response_model=schemas.Booking)
async def book_hotel(booking: schemas.BookingCreate, db: Session = Depends(get_db), current_user: database.User = Depends(get_current_user)):
    if booking.end_date <= booking.start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date.")

    db_booking, error_msg = crud.create_booking(db=db, user_id=current_user.id, booking=booking)
    if error_msg:
        raise HTTPException(status_code=400, detail=error_msg)
    return db_booking

# Taxi API
# Improved mock implementation with realistic data
@app.post("/api/taxis/book")
async def book_taxi(booking: TaxiBookingRequest):
    import random
    wait_time = random.randint(3, 12)
    # If fare is 0 or not provided, estimate it
    estimated_fare = booking.fare if booking.fare > 0 else round(random.uniform(15.0, 45.0), 2)
    
    return JSONResponse(content={
        "status": "success",
        "message": f"Driver found! Your ride from {booking.pickup} to {booking.destination} is confirmed.",
        "estimated_arrival": f"{wait_time} minutes",
        "estimated_fare": f"${estimated_fare}",
        "driver_name": random.choice(["Alex", "Sarah", "Marco", "Elena"]),
        "vehicle": random.choice(["Tesla Model 3", "Toyota Prius", "Mercedes E-Class"])
    })

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

# Currency Converter API Proxy
@app.get("/api/currency/rates")
async def get_currency_rates():
    cache_key = "currency_rates_USD"
    if cache_key in currency_cache:
        return JSONResponse(content=currency_cache[cache_key])

    api_key = os.environ.get("EXCHANGE_RATE_API_KEY", "")
    if not api_key or api_key == "YOUR_API_KEY":
        # Return mock data when API key is not configured
        mock_rates = {
            "base": "USD",
            "rates": {"EUR": 0.92, "GBP": 0.79, "JPY": 149.50, "MAD": 10.05, "CAD": 1.35}
        }
        return JSONResponse(content=mock_rates)

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("result") == "success":
            currency_cache[cache_key] = data
            return JSONResponse(content=data)
        else:
            raise HTTPException(status_code=502, detail="Failed to fetch valid data from currency API.")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Error communicating with currency API: {e}")

@app.get("/api/currency/convert")
async def convert_currency(amount: float, from_currency: str, to_currency: str):
    cache_key = "currency_rates_USD"

    if cache_key not in currency_cache:
        await get_currency_rates()

    rates_data = currency_cache.get(cache_key)
    if not rates_data or "conversion_rates" not in rates_data:
        raise HTTPException(status_code=500, detail="Currency rates are not available in cache.")

    rates = rates_data["conversion_rates"]

    if from_currency not in rates or to_currency not in rates:
        raise HTTPException(status_code=404, detail=f"Currency code not found. Cannot convert from {from_currency} to {to_currency}.")

    amount_in_usd = amount / rates[from_currency]
    converted_amount = amount_in_usd * rates[to_currency]

    return JSONResponse(content={
        "result": "success",
        "from": from_currency,
        "to": to_currency,
        "amount": amount,
        "conversion_result": converted_amount
    })
