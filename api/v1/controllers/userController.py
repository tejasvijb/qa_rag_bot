"""
User controller - business logic for authentication
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple

import bcrypt
import jwt
from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.v1.models.user import User, UserRole

# Constants
TOKEN_EXPIRY = "15m"
TOKEN_EXPIRY_SECONDS = 15 * 60  # 15 minutes


def normalize_email(email: Optional[str]) -> str:
    """Normalize email to lowercase and trimmed"""
    if not email:
        return ""
    return email.strip().lower()





def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=10)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def generate_access_token(user: User) -> str:
    """Generate JWT access token"""
    access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
    if not access_token_secret:
        raise HTTPException(
            status_code=500,
            detail="Access token secret is not defined"
        )
    
    user_payload = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role
    }
    
    token_data = {
        "user": user_payload,
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(token_data, access_token_secret, algorithm="HS256")


def get_cookie_options() -> dict:
    """Get cookie configuration options"""
    is_production = os.getenv('ENVIRONMENT', '').lower() == 'production'
    
    return {
        "key": "accessToken",
        "httponly": True,
        "max_age": TOKEN_EXPIRY_SECONDS,
        "path": "/",
        "samesite": "none" if is_production else "lax",
        "secure": is_production
    }


def register_user(
    email: str,
    first_name: str,
    last_name: str,
    password: str,
    role: Optional[str],
    db: Session
) -> User:
    """
    Register a new user.
    
    Args:
        email: User email address
        first_name: User first name
        last_name: User last name
        password: User password (min 8 chars)
        role: User role (user or admin, defaults to user)
        db: Database session
    
    Returns:
        User: Created user object
    
    Raises:
        HTTPException: If validation fails or user already exists
    """
    # Normalize and validate email
    email = normalize_email(email)
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    # Validate names
    first_name = first_name.strip() if first_name else ""
    last_name = last_name.strip() if last_name else ""
    
    if not first_name or not last_name:
        raise HTTPException(status_code=400, detail="First name and last name are required")
    
    if len(first_name) < 2 or len(first_name) > 64:
        raise HTTPException(status_code=400, detail="First name must be between 2 and 64 characters")
    
    if len(last_name) < 2 or len(last_name) > 64:
        raise HTTPException(status_code=400, detail="Last name must be between 2 and 64 characters")
    
    # Validate password
    if not password or len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists")
    
    # Hash password
    hashed_password = hash_password(password)
    
    # Create new user
    new_user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=hashed_password,
        role=role or UserRole.USER.value
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


def login_user(email: str, password: str, db: Session) -> Tuple[User, str]:
    """
    Login user and verify password.
    
    Args:
        email: User email address
        password: User password
        db: Database session
    
    Returns:
        tuple: (User object, access_token string)
    
    Raises:
        HTTPException: If credentials are invalid or user is inactive
    """
    # Normalize and validate email
    email = normalize_email(email)
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    # Find user in database
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    
    # Generate token
    access_token = generate_access_token(user)
    
    return user, access_token


def logout_user() -> dict:
    """
    Logout user - returns success message.
    
    Returns:
        dict: Success message
    """
    return {"message": "Logged out successfully"}
