"""
services/auth_service.py
─────────────────────────
Business logic for authentication: sign-up and sign-in.
Keeps routers thin — all validation / DB interaction lives here.
"""
import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

import db.crud as crud
import db.schemas as schemas
from core.security import verify_password, get_password_hash, create_access_token

logger = logging.getLogger(__name__)


# ─── Sign-Up ──────────────────────────────────────────────────────

def register_user(db: Session, user_data: schemas.UserCreate) -> schemas.User:
    """
    Create a new user account.

    Raises:
        HTTPException 400  – if the username is already taken.
        HTTPException 400  – if the email is already registered.
    """
    # 1. Check for duplicate username
    existing = crud.get_user_by_username(db, username=user_data.username)
    if existing:
        logger.warning("Sign-up attempt with existing username: %s", user_data.username)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà pris.",  # Username already taken
        )

    # 2. Check for duplicate email
    existing_email = crud.get_user_by_email(db, email=user_data.email)
    if existing_email:
        logger.warning("Sign-up attempt with existing email: %s", user_data.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette adresse e-mail est déjà utilisée.",  # Email already in use
        )

    # 3. Hash password and persist user
    db_user = crud.create_user(db=db, user=user_data)
    logger.info("New user registered: %s", db_user.username)
    return db_user


# ─── Sign-In ──────────────────────────────────────────────────────

def authenticate_user(db: Session, username: str, password: str) -> dict:
    """
    Validate credentials and return a JWT access token.

    Raises:
        HTTPException 401  – on invalid username or password.

    Returns:
        {"access_token": str, "token_type": "bearer"}
    """
    user = crud.get_user_by_username(db, username=username)
    if not user:
        logger.warning("Sign-in attempt for unknown user: %s", username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect.",  # Wrong credentials
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(password, user.password_hash):
        logger.warning("Failed sign-in for user: %s (wrong password)", username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    logger.info("User signed in: %s", user.username)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
        },
    }
