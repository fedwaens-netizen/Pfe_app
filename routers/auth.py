
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from fastapi.requests import HTTPConnection
from sqlalchemy.orm import Session
from typing import Optional

import db.crud as crud
import db.schemas as schemas
import db.database as database
from db.database import SessionLocal
from services.auth_service import register_user, authenticate_user
from core.security import decode_access_token
import random
from datetime import datetime, timedelta
from pydantic import BaseModel
from services.email_service import send_otp_email

logger = logging.getLogger(__name__)

# Simple in-memory store for OTPs keyed by email: { email: {"otp": "123456", "expires": datetime} }
OTP_STORE = {}

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")


# ─── Optional OAuth2 scheme that doesn't raise 401 ─────────────────
class OptionalOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: HTTPConnection) -> Optional[str]:
        try:
            return await super().__call__(request)
        except HTTPException:
            return None

optional_oauth2_scheme = OptionalOAuth2PasswordBearer(tokenUrl="/auth/signin")


# ─── DB Dependency ────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── Current-User Dependency ──────────────────────────────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> database.User:
    """
    Decode the JWT and return the matching User from the database.
    Raises HTTP 401 if the token is invalid or the user no longer exists.
    """
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token malformé.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ─── Optional Current-User Dependency ─────────────────────────────
async def get_optional_user(
    token: Optional[str] = Depends(optional_oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[database.User]:
    """
    Decode the JWT and return the matching User, or None if not authenticated.
    Does NOT raise HTTPException for missing/invalid tokens.
    """
    if token is None:
        return None
    payload = decode_access_token(token)
    if payload is None:
        return None
    username: str = payload.get("sub")
    if not username:
        return None
    return crud.get_user_by_username(db, username=username)


# ─── Sign-Up ──────────────────────────────────────────────────────
@router.post(
    "/signup",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un compte",
    description="Inscrit un nouvel utilisateur. Renvoie le profil créé (sans mot de passe).",
)
def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    - **username**: must be unique
    - **email**: must be unique
    - **password**: will be hashed before storage (bcrypt)
    """
    return register_user(db=db, user_data=user_data)


# ─── Sign-In ──────────────────────────────────────────────────────
@router.post(
    "/signin",
    response_model=schemas.TokenWithUser,
    summary="Se connecter",
    description=(
        "Renvoie un JWT Bearer token à inclure dans l'en-tête Authorization "
        "pour tous les endpoints protégés."
    ),
)
def signin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate with **username** + **password**.

    Returns a signed JWT `access_token`.
    """
    return authenticate_user(db=db, username=form_data.username, password=form_data.password)


# ─── Current User Profile ─────────────────────────────────────────
@router.get(
    "/me",
    response_model=schemas.User,
    summary="Mon profil",
    description="Retourne les informations du compte actuellement connecté.",
)
def get_me(current_user: database.User = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    return current_user

# ─── Forgot Password / Reset Password (Email OTP) ──────────────────
@router.post("/forgot-password", summary="Demander la réinitialisation du mot de passe")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=req.email)
    if not user:
        raise HTTPException(status_code=404, detail="Aucun compte trouvé avec cette adresse email.")
    
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    expires = datetime.now() + timedelta(minutes=10)
    
    # Store OTP keyed by email
    OTP_STORE[req.email] = {"otp": otp, "expires": expires}
    
    # Send OTP by email
    success = send_otp_email(req.email, otp)
    if not success:
        # Ne pas bloquer si l'email échoue (ex: SMTP non configuré en dev)
        logger.warning(f"L'email OTP n'a pas pu être envoyé à {req.email}")

    # Obfuscate email for frontend (e.g., ab***@gmail.com)
    parts = req.email.split("@")
    if len(parts) == 2:
        local = parts[0]
        masked_local = local[:2] + "***" if len(local) > 2 else "***"
        masked_email = f"{masked_local}@{parts[1]}"
    else:
        masked_email = "***"
    
    return {"message": "Si l'utilisateur existe, un email a été envoyé.", "masked_email": masked_email}

@router.post("/reset-password", summary="Réinitialiser le mot de passe")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    if req.email not in OTP_STORE:
        raise HTTPException(status_code=400, detail="Aucune demande de réinitialisation trouvée ou code expiré.")
    
    stored_data = OTP_STORE[req.email]
    if datetime.now() > stored_data["expires"]:
        del OTP_STORE[req.email]
        raise HTTPException(status_code=400, detail="Le code a expiré.")
        
    if req.otp != stored_data["otp"]:
        raise HTTPException(status_code=400, detail="Code de vérification incorrect.")
        
    # Valid OTP -> Update Password by email
    user = crud.get_user_by_email(db, email=req.email)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    
    updated_user = crud.update_user_password(db, user.username, req.new_password)
    if not updated_user:
        raise HTTPException(status_code=404, detail="Erreur lors de la mise à jour du mot de passe.")
        
    # Clean up OTP
    del OTP_STORE[req.email]
    
    return {"message": "Mot de passe réinitialisé avec succès."}

# ─── Admin Dashboard ──────────────────────────────────────────────
from sqlalchemy import func

@router.get("/admin/stats", summary="Get Admin Dashboard Stats")
def get_admin_stats(db: Session = Depends(get_db)):
    # Total users
    total_users = db.query(database.User).count()
    
    # Total bookings
    hotel_bookings_count = db.query(database.Booking).count()
    taxi_bookings_count = db.query(database.TaxiBooking).count()
    
    # Total revenue (sum of hotel total_price + taxi fare)
    hotel_revenue = db.query(func.sum(database.Booking.total_price)).scalar() or 0
    taxi_revenue = db.query(func.sum(database.TaxiBooking.fare)).scalar() or 0
    total_revenue = hotel_revenue + taxi_revenue
    
    return {
        "total_users": total_users,
        "hotel_bookings": hotel_bookings_count,
        "taxi_bookings": taxi_bookings_count,
        "total_revenue": total_revenue,
        "hotel_revenue": hotel_revenue,
        "taxi_revenue": taxi_revenue
    }
