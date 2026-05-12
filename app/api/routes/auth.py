"""Authentication routes."""
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse
from app.core.security import verify_password, create_access_token
from app.core.exceptions import AuthException
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
) -> LoginResponse:
    """Login with email and password."""
    # Find user by email
    stmt = select(User).where(User.email == credentials.email)
    user = db.execute(stmt).scalars().first()
    
    if user is None:
        raise AuthException()
    
    if not user.is_active:
        raise AuthException(code="AUTH_INACTIVE_USER", message="User is inactive")
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise AuthException()
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "company_id": str(user.company_id),
            "role": user.role,
        },
        expires_delta=access_token_expires,
    )
    
    return LoginResponse(
        access_token=access_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            company_id=user.company_id,
            role=user.role,
            full_name=user.full_name,
            is_active=user.is_active,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current authenticated user info."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        company_id=current_user.company_id,
        role=current_user.role,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
    )
