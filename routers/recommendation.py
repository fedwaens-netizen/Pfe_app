
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
import os

import db.crud as crud
import db.schemas as schemas
import db.database as database
from db.database import SessionLocal
from services.recommendation_service import get_prediction
from routers.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Recommendations"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# ─── DB Dependency ────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/api/recommend")
def recommendation_api(
    request: Request,
    rec_request: schemas.RecommendationRequest, 
    db: Session = Depends(get_db),
    current_user: database.User = Depends(get_current_user)
):
    """
    JSON API for recommendations. Returns the predicted destination and detail info.
    """
    try:
        # Pass the app state to the service so it can access the ML models
        prediction_name = get_prediction(request.app.state, rec_request, db)
        
        # Enforced auth and use current_user.id
        user_id = current_user.id
        
        # Log to history
        log_entry = schemas.RecommendationLogCreate(
            age=rec_request.Age,
            budget=rec_request.Budget,
            interest=rec_request.Interet,
            duration=rec_request.Duree,
            climate=rec_request.Climat,
            destination_type=rec_request.Type_Destination,
            season=rec_request.Saison,
            region=rec_request.Region,
            type_voyage=rec_request.Type_Voyage,
            predicted_destination=prediction_name
        )
        saved_log = crud.create_recommendation_history(db, log_entry, user_id=user_id)
        
        # Fetch detailed destination info for response using crud to trigger dynamic image fetch if needed
        destination = crud.get_destination_by_name(db, prediction_name)
        
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
        logger.error(f"API Recommendation Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend/")
def recommend(
    request: Request, 
    rec_request: schemas.RecommendationRequest, 
    db: Session = Depends(get_db),
    current_user: database.User = Depends(get_current_user)
):
    """
    Form post endpoint. Returns an HTML template portion.
    """
    try:
        prediction = get_prediction(request.app.state, rec_request, db)
        
        user_id = current_user.id 
        
        # Log to history
        log_entry = schemas.RecommendationLogCreate(
            age=rec_request.Age,
            budget=rec_request.Budget,
            interest=rec_request.Interet,
            duration=rec_request.Duree,
            climate=rec_request.Climat,
            destination_type=rec_request.Type_Destination,
            season=rec_request.Saison,
            region=rec_request.Region,
            type_voyage=rec_request.Type_Voyage,
            predicted_destination=prediction
        )
        crud.create_recommendation_history(db, log_entry, user_id=user_id)
        
        destination = crud.get_destination_by_name(db, prediction)
        if destination and destination.continent:
            display_text = f"{prediction} ({destination.continent} du maroc)"
        else:
            display_text = prediction
            
        return templates.TemplateResponse("_recommendation_result.html", {
            "request": request, 
            "recommendation": display_text
        })
    except Exception as e:
        logger.error(f"Recommendation Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error during recommendation.")


@router.get("/api/me/recommendations", response_model=List[schemas.RecommendationLog])
def get_my_recommendations(
    current_user: database.User = Depends(get_current_user), 
    db: Session = Depends(get_db),
    limit: int = 20
):
    """Get the logged-in user's recommendation history."""
    return crud.get_user_recommendations(db, user_id=current_user.id, limit=limit)

@router.get("/api/me/stats")
def get_my_stats(
    current_user: database.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Get statistics about the user's recommendations for the dashboard."""
    user_id = current_user.id
    
    total_recs = db.query(database.RecommendationHistory).filter(database.RecommendationHistory.user_id == user_id).count()
    
    if total_recs == 0:
        return {"total": 0}
        
    avg_budget = db.query(func.avg(database.RecommendationHistory.budget)).filter(database.RecommendationHistory.user_id == user_id).scalar()
    
    # Top destinations
    top_destinations = db.query(
        database.RecommendationHistory.predicted_destination,
        func.count(database.RecommendationHistory.id).label('count')
    ).filter(database.RecommendationHistory.user_id == user_id).group_by(database.RecommendationHistory.predicted_destination).order_by(func.count(database.RecommendationHistory.id).desc()).limit(5).all()
    
    # Top interests
    top_interests = db.query(
        database.RecommendationHistory.interest,
        func.count(database.RecommendationHistory.id).label('count')
    ).filter(database.RecommendationHistory.user_id == user_id).group_by(database.RecommendationHistory.interest).order_by(func.count(database.RecommendationHistory.id).desc()).limit(5).all()

    return {
        "total": total_recs,
        "avg_budget": round(avg_budget, 2) if avg_budget else 0,
        "top_destinations": [{"name": r[0], "count": r[1]} for r in top_destinations],
        "top_interests": [{"name": r[0], "count": r[1]} for r in top_interests]
    }
