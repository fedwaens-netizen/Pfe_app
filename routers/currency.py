from fastapi import APIRouter, HTTPException, Depends
from services.currency_service import currency_service
from typing import Dict, Optional
from routers.auth import get_current_user, get_optional_user
import db.database as database

router = APIRouter(
    prefix="/api/currency",
    tags=["Currency"]
)

@router.get("/rates")
async def get_currency_rates(current_user: Optional[database.User] = Depends(get_optional_user)):
    """Get latest exchange rates."""
    data = currency_service.get_latest_rates()
    if not data:
        raise HTTPException(status_code=503, detail="Currency rates are not available.")
    return data

@router.get("/convert")
async def convert_currency(
    amount: float, 
    from_currency: str, 
    to_currency: str, 
    current_user: Optional[database.User] = Depends(get_optional_user)
):
    """Convert an amount from one currency to another."""
    result, error = currency_service.convert(amount, from_currency, to_currency)
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return {
        "result": "success",
        "from": from_currency,
        "to": to_currency,
        "amount": amount,
        "conversion_result": result
    }

@router.get("/history")
async def get_history(
    from_currency: str, 
    to_currency: str, 
    current_user: Optional[database.User] = Depends(get_optional_user)
):
    """Get simulated historical data for charts."""
    history = currency_service.get_history(from_currency, to_currency)
    if not history:
        raise HTTPException(status_code=400, detail="Could not generate history.")
    return history
