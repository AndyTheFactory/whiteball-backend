"""Company routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.exceptions import DuplicateException, NotFoundException
from app.models.company import Company
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=PaginatedResponse)
async def list_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: str | None = Query(None),
    country: str | None = Query(None),
    city: str | None = Query(None),
    role: str | None = Query(None, pattern="^(admin|customer)$"),
    is_active: bool | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("name", pattern="^(name|created_at|updated_at)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
) -> PaginatedResponse:
    """List companies with pagination and filters."""
    # Build query
    stmt = select(Company)

    # Apply filters
    if search:
        stmt = stmt.where(
            (Company.name.ilike(f"%{search}%"))
            | (Company.vat_number.ilike(f"%{search}%"))
            | (Company.registration_number.ilike(f"%{search}%"))
        )

    if country:
        stmt = stmt.where(Company.country.ilike(f"%{country}%"))

    if city:
        stmt = stmt.where(Company.city.ilike(f"%{city}%"))

    if role:
        stmt = stmt.where(Company.role == role)

    if is_active is not None:
        stmt = stmt.where(Company.is_active == is_active)

    # Count total
    count_stmt = select(func.count()).select_from(Company)
    if search:
        count_stmt = count_stmt.where(
            (Company.name.ilike(f"%{search}%"))
            | (Company.vat_number.ilike(f"%{search}%"))
            | (Company.registration_number.ilike(f"%{search}%"))
        )
    if country:
        count_stmt = count_stmt.where(Company.country.ilike(f"%{country}%"))
    if city:
        count_stmt = count_stmt.where(Company.city.ilike(f"%{city}%"))
    if role:
        count_stmt = count_stmt.where(Company.role == role)
    if is_active is not None:
        count_stmt = count_stmt.where(Company.is_active == is_active)

    total = db.execute(count_stmt).scalar() or 0

    # Apply sorting
    if sort_order == "desc":
        stmt = stmt.order_by(getattr(Company, sort_by).desc())
    else:
        stmt = stmt.order_by(getattr(Company, sort_by))

    # Apply pagination
    stmt = stmt.limit(limit).offset(offset)

    companies = db.execute(stmt).scalars().all()
    items = [CompanyResponse(**company.__dict__) for company in companies]

    return PaginatedResponse(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompanyResponse:
    """Create a new company."""
    # Check if VAT number already exists
    if company_data.vat_number:
        stmt = select(Company).where(Company.vat_number == company_data.vat_number)
        existing = db.execute(stmt).scalars().first()
        if existing:
            raise DuplicateException("company", "VAT number")

    # Check if registration number already exists
    if company_data.registration_number:
        stmt = select(Company).where(Company.registration_number == company_data.registration_number)
        existing = db.execute(stmt).scalars().first()
        if existing:
            raise DuplicateException("company", "registration number")

    # Create company
    company = Company(**company_data.model_dump())

    db.add(company)
    db.commit()
    db.refresh(company)

    return CompanyResponse(**company.__dict__)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompanyResponse:
    """Get company details."""
    stmt = select(Company).where(Company.id == company_id)
    company = db.execute(stmt).scalars().first()

    if not company:
        raise NotFoundException("Company")

    return CompanyResponse(**company.__dict__)


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: UUID,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompanyResponse:
    """Update company details."""
    stmt = select(Company).where(Company.id == company_id)
    company = db.execute(stmt).scalars().first()

    if not company:
        raise NotFoundException("Company")

    # Check if VAT number is being updated and already exists elsewhere
    if company_data.vat_number and company_data.vat_number != company.vat_number:
        stmt = select(Company).where((Company.vat_number == company_data.vat_number) & (Company.id != company_id))
        existing = db.execute(stmt).scalars().first()
        if existing:
            raise DuplicateException("company", "VAT number")

    # Check if registration number is being updated and already exists elsewhere
    if company_data.registration_number and company_data.registration_number != company.registration_number:
        stmt = select(Company).where(
            (Company.registration_number == company_data.registration_number) & (Company.id != company_id)
        )
        existing = db.execute(stmt).scalars().first()
        if existing:
            raise DuplicateException("company", "registration number")

    # Update company with provided fields only
    update_data = company_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)

    db.add(company)
    db.commit()
    db.refresh(company)

    return CompanyResponse(**company.__dict__)
