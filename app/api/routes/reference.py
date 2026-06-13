from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.packaging import WhiteballPackagingItem
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.packaging import WhiteballPackagingItemResponse

router = APIRouter(tags=["reference database"])


@router.get("/whiteball-packaging-items", response_model=PaginatedResponse)
@router.get("/reference/whiteball-packaging-items", response_model=PaginatedResponse)
async def list_whiteball_packaging_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: str | None = Query(None),
    type_filter: str | None = Query(None, alias="type"),
    material: str | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse:
    """List Whiteball reference packaging items."""
    stmt = select(WhiteballPackagingItem)

    if search:
        stmt = stmt.where(
            (WhiteballPackagingItem.name.ilike(f"%{search}%"))
            | (WhiteballPackagingItem.description.ilike(f"%{search}%"))
        )
    if type_filter:
        stmt = stmt.where(WhiteballPackagingItem.type.ilike(f"%{type_filter}%"))
    if material:
        stmt = stmt.where(WhiteballPackagingItem.material.ilike(f"%{material}%"))

    count_stmt = select(func.count()).select_from(WhiteballPackagingItem)
    total = db.execute(count_stmt).scalar() or 0
    items = db.execute(stmt.limit(limit).offset(offset)).scalars().all()

    return PaginatedResponse(
        items=[WhiteballPackagingItemResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )
