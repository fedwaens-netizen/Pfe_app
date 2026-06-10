import asyncio
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import db.schemas as schemas
import db.database as database
from routers.auth import get_current_user
from db.database import SessionLocal

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payment", tags=["Payment"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/process", response_model=schemas.PaymentResponse)
async def process_payment(
    request: schemas.PaymentRequest,
    current_user: database.User = Depends(get_current_user),
):
    """
    Simulate a payment processing gateway (like Stripe or PayPal).
    """
    logger.info(f"Processing {request.method} payment for {current_user.username} - {request.amount} {request.currency}")
    
    # Simulate network delay for realistic experience
    await asyncio.sleep(2)
    
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount.")
        
    transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
    
    return schemas.PaymentResponse(
        status="success",
        transaction_id=transaction_id,
        message=f"Paiement de {request.amount} {request.currency} via {request.method} réussi."
    )
