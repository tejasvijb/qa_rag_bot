"""
Token validation middleware for FastAPI
"""
import os
from datetime import datetime
from typing import Optional
from fastapi import Depends, HTTPException, Cookie
from jwt import decode as jwt_decode
from jwt import DecodeError, ExpiredSignatureError
from sqlalchemy.orm import Session

from api.v1.config.dbconnection import SessionLocal
from api.v1.models.user import User


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def validate_token(
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
) -> dict:
    """
    Validate JWT token from cookies and attach user info to request.
    
    Usage in routes:
        from fastapi import Depends
        
        @app.get("/protected")
        async def protected_route(user: dict = Depends(validate_token)):
            return {"message": f"Hello {user['email']}"}
    
    Args:
        access_token: JWT token from cookies
        db: Database session
    
    Returns:
        dict: User information
        
    Raises:
        HTTPException: If token is missing, invalid, or user not found
    """
    
    # Check if token is provided
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="User is not authorized or token is missing"
        )
    
    # Get JWT secret
    access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')
    if not access_token_secret:
        raise HTTPException(
            status_code=500,
            detail="Internal server error: ACCESS_TOKEN_SECRET is not defined"
        )
    
    try:
        # Verify and decode token
        payload = jwt_decode(access_token, access_token_secret, algorithms=["HS256"])
        user_id: str = payload.get("user", {}).get("id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User is not authorized")
            
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="User is not authorized")
    
    # Query user from database
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(status_code=401, detail="User is not authorized")
    
    if not db_user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")
    
    # Return user info
    return {
        "id": db_user.id,
        "email": db_user.email,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "role": db_user.role
    }
