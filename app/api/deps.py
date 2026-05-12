"""API dependencies."""

from typing import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AuthException
from app.core.security import decode_token
from app.db import get_db_session
from app.models.user import User

security = HTTPBearer()


async def get_db() -> Generator[Session, None, None]:
    """Get database session dependency."""
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user from token."""
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise AuthException(message="Could not validate credentials")

    user_id = payload.get("sub")
    if user_id is None:
        raise AuthException(message="Could not validate credentials")

    # Fetch user from database
    stmt = select(User).where(User.id == user_id)
    user = db.execute(stmt).scalars().first()

    if user is None:
        raise AuthException(message="User not found")

    if not user.is_active:
        raise AuthException(code="AUTH_INACTIVE_USER", message="User is inactive")

    return user
