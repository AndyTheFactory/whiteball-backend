"""User routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.exceptions import DuplicateException, NotFoundException
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=PaginatedResponse)
async def list_users(
    company_id: UUID = Query(..., description="Company ID filter (required)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: str | None = Query(None, description="Search by email or full name"),
    email: str | None = Query(None),
    role: str | None = Query(None, pattern="^(admin|user)$"),
    is_active: bool | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("created_at", pattern="^(email|full_name|role|created_at|updated_at)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
) -> PaginatedResponse:
    """List users with pagination and filters. Requires company_id filter."""
    # Build query
    stmt = select(User).where(User.company_id == company_id)

    # Apply filters
    if search:
        stmt = stmt.where((User.email.ilike(f"%{search}%")) | (User.full_name.ilike(f"%{search}%")))

    if email:
        stmt = stmt.where(User.email.ilike(f"%{email}%"))

    if role:
        stmt = stmt.where(User.role == role)

    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)

    # Count total
    count_stmt = select(func.count()).select_from(User).where(User.company_id == company_id)
    if search:
        count_stmt = count_stmt.where((User.email.ilike(f"%{search}%")) | (User.full_name.ilike(f"%{search}%")))
    if email:
        count_stmt = count_stmt.where(User.email.ilike(f"%{email}%"))
    if role:
        count_stmt = count_stmt.where(User.role == role)
    if is_active is not None:
        count_stmt = count_stmt.where(User.is_active == is_active)

    total = db.execute(count_stmt).scalar() or 0

    # Apply sorting
    if sort_order == "desc":
        stmt = stmt.order_by(getattr(User, sort_by).desc())
    else:
        stmt = stmt.order_by(getattr(User, sort_by))

    # Apply pagination
    stmt = stmt.limit(limit).offset(offset)

    users = db.execute(stmt).scalars().all()
    items = [UserResponse(**user.__dict__) for user in users]

    return PaginatedResponse(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Create a new user."""
    # Check if email already exists
    stmt = select(User).where(User.email == user_data.email)
    existing = db.execute(stmt).scalars().first()
    if existing:
        raise DuplicateException("user", "email")

    # Hash password and create user
    user = User(
        company_id=UUID(user_data.company_id),
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        role=user_data.role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(**user.__dict__)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get user details."""
    stmt = select(User).where(User.id == user_id)
    user = db.execute(stmt).scalars().first()

    if not user:
        raise NotFoundException("User")

    return UserResponse(**user.__dict__)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Update user details."""
    stmt = select(User).where(User.id == user_id)
    user = db.execute(stmt).scalars().first()

    if not user:
        raise NotFoundException("User")

    # Check if email is being updated and already exists elsewhere
    if user_data.email and user_data.email != user.email:
        stmt = select(User).where((User.email == user_data.email) & (User.id != user_id))
        existing = db.execute(stmt).scalars().first()
        if existing:
            raise DuplicateException("user", "email")

    # Update user with provided fields only
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(**user.__dict__)
