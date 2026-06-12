"""Dictionary routes."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.dictionary import DictionaryValue
from app.schemas.dictionary import DictionaryValueResponse

router = APIRouter(prefix="/dictionaries", tags=["dictionaries"])


@router.get("/{dictionary_type_code}/values", response_model=list[DictionaryValueResponse])
async def list_dictionary_values(
    dictionary_type_code: str,
    db: Session = Depends(get_db),
) -> list[DictionaryValueResponse]:
    """List dictionary values for a dictionary type, sorted by sort order."""
    stmt = (
        select(DictionaryValue)
        .where(DictionaryValue.dictionary_type_code == dictionary_type_code)
        .order_by(DictionaryValue.sort_order, DictionaryValue.code)
    )
    values = db.execute(stmt).scalars().all()

    return [DictionaryValueResponse.model_validate(value) for value in values]
