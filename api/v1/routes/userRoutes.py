"""
User routes for authentication endpoints
"""
from typing import Optional

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from api.v1.config.dbconnection import SessionLocal
from api.v1.models.user import UserRole
from api.v1.controllers.userController import (
    register_user as register_user_controller,
    login_user as login_user_controller,
    logout_user as logout_user_controller,
    get_cookie_options
)

# Router
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# Request/Response Models
class RegisterUserRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    role: Optional[str] = UserRole.USER.value


class LoginUserRequest(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class UserPayload(BaseModel):
    """JWT user payload"""
    id: str
    email: str
    first_name: str
    last_name: str
    role: str


class UserResponse(BaseModel):
    """User response"""
    user: UserPayload


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(request: RegisterUserRequest, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **email**: User email address
    - **first_name**: User first name
    - **last_name**: User last name
    - **password**: User password (min 8 chars)
    - **role**: User role (user or admin, defaults to user)
    
    Returns the created user data (without password).
    """
    user = register_user_controller(
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        password=request.password,
        role=request.role,
        db=db
    )
    
    return UserResponse(
        user=UserPayload(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role
        )
    )


@router.post("/login", response_model=UserResponse, status_code=200)
async def login(
    request: LoginUserRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Login user and return access token.
    
    - **email**: User email address
    - **password**: User password
    
    Returns user data and sets accessToken cookie.
    """
    user, access_token = login_user_controller(
        email=request.email,
        password=request.password,
        db=db
    )
    
    # Set cookie
    cookie_options = get_cookie_options()
    response.set_cookie(
        key=cookie_options["key"],
        value=access_token,
        httponly=cookie_options["httponly"],
        max_age=cookie_options["max_age"],
        path=cookie_options["path"],
        samesite=cookie_options["samesite"],
        secure=cookie_options["secure"]
    )
    
    return UserResponse(
        user=UserPayload(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role
        )
    )


@router.post("/logout", response_model=MessageResponse, status_code=200)
async def logout(response: Response):
    """
    Logout user by clearing the access token cookie.
    
    Returns success message.
    """
    import os
    
    is_production = os.getenv('ENVIRONMENT', '').lower() == 'production'
    
    response.delete_cookie(
        key="accessToken",
        path="/",
        samesite="none" if is_production else "lax",
        secure=is_production,
        httponly=True
    )
    
    logout_user_controller()
    
    return MessageResponse(message="Logged out successfully")
