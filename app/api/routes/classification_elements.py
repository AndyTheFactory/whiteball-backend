"""Classification-specific product element routes.

Each classification gets three endpoints:
  POST   /products/{product_id}/elements/{classification}  – upsert (replace-all)
  GET    /products/{product_id}/elements/{classification}  – list all
  DELETE /products/{product_id}/elements/{classification}  – delete all

{classification} is a literal path segment (packaging, scp, tire, …), not a
dynamic parameter, so every classification has its own typed request/response
schema.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.exceptions import NotFoundException
from app.models.product import Product
from app.models.product_elements import ProductElements
from app.models.user import User
from app.schemas.classification_elements import (
    BatteryElementInput,
    BatteryElementResponse,
    EeeElementInput,
    EeeElementResponse,
    OilElementInput,
    OilElementResponse,
    PackagingElementInput,
    PackagingElementResponse,
    ScpElementInput,
    ScpElementResponse,
    SgrElementInput,
    SgrElementResponse,
    SupElementInput,
    SupElementResponse,
    TireElementInput,
    TireElementResponse,
    TransportPackElementInput,
    TransportPackElementResponse,
)

router = APIRouter(prefix="/products", tags=["Classification Specific Elements"])


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _get_owned_product(db: Session, product_id: UUID, current_user: User) -> Product:
    product = (
        db.execute(select(Product).where((Product.id == product_id) & (Product.company_id == current_user.company_id)))
        .scalars()
        .first()
    )
    if not product:
        raise NotFoundException("Product")
    return product


def _delete_by_classification(db: Session, product_id: UUID, classification_code: str) -> None:
    rows = (
        db.execute(
            select(ProductElements).where(
                (ProductElements.product_id == product_id)
                & (ProductElements.classification_code == classification_code)
            )
        )
        .scalars()
        .all()
    )
    for row in rows:
        db.delete(row)
    db.flush()


def _list_by_classification(db: Session, product_id: UUID, classification_code: str) -> list[ProductElements]:
    return (
        db.execute(
            select(ProductElements).where(
                (ProductElements.product_id == product_id)
                & (ProductElements.classification_code == classification_code)
            )
        )
        .scalars()
        .all()
    )


def _attrs_from_model(elem: ProductElements) -> dict:
    return elem.attributes or {}


# ---------------------------------------------------------------------------
# packaging
# ---------------------------------------------------------------------------

_PACKAGING = "packaging"


def _packaging_from_input(inp: PackagingElementInput, product_id: UUID) -> ProductElements:
    attrs: dict = {}
    if inp.grouping is not None:
        attrs["grouping"] = inp.grouping
    return ProductElements(
        product_id=product_id,
        classification_code=_PACKAGING,
        type_code=inp.type_code,
        material_code=inp.material_code,
        name=inp.name,
        weight_grams=inp.weight_grams,
        attributes=attrs,
    )


def _packaging_to_response(elem: ProductElements) -> PackagingElementResponse:
    attrs = _attrs_from_model(elem)
    return PackagingElementResponse(
        id=elem.id,
        type_code=elem.type_code,
        material_code=elem.material_code,
        name=elem.name,
        weight_grams=elem.weight_grams,
        grouping=attrs.get("grouping"),
    )


@router.post(
    "/{product_id}/elements/packaging",
    response_model=list[PackagingElementResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upsert_packaging_elements(
    product_id: UUID,
    items: list[PackagingElementInput],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PackagingElementResponse]:
    """Replace all packaging elements for a product (upsert via delete + create)."""
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _PACKAGING)
    created = []
    for inp in items:
        elem = _packaging_from_input(inp, product_id)
        db.add(elem)
        db.flush()
        db.refresh(elem)
        created.append(_packaging_to_response(elem))
    db.commit()
    return created


@router.get("/{product_id}/elements/packaging", response_model=list[PackagingElementResponse])
async def get_packaging_elements(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PackagingElementResponse]:
    """List all packaging elements for a product."""
    _get_owned_product(db, product_id, current_user)
    return [_packaging_to_response(e) for e in _list_by_classification(db, product_id, _PACKAGING)]


@router.delete("/{product_id}/elements/packaging", status_code=status.HTTP_204_NO_CONTENT)
async def delete_packaging_elements(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete all packaging elements for a product."""
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _PACKAGING)
    db.commit()


# ---------------------------------------------------------------------------
# scp
# ---------------------------------------------------------------------------

_SCP = "scp"


def _scp_to_response(elem: ProductElements) -> ScpElementResponse:
    attrs = _attrs_from_model(elem)
    raw = attrs.get("product_value")
    return ScpElementResponse(
        id=elem.id,
        product_value=raw if raw is None else type(raw)(raw),
    )


@router.post(
    "/{product_id}/elements/scp",
    response_model=list[ScpElementResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upsert_scp_element(
    product_id: UUID,
    item: ScpElementInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ScpElementResponse]:
    """Replace the SCP element for a product."""
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _SCP)
    attrs: dict = {}
    if item.product_value is not None:
        attrs["product_value"] = float(item.product_value)
    elem = ProductElements(
        product_id=product_id,
        classification_code=_SCP,
        attributes=attrs,
    )
    db.add(elem)
    db.flush()
    db.refresh(elem)
    db.commit()
    return [_scp_to_response(elem)]


@router.get("/{product_id}/elements/scp", response_model=list[ScpElementResponse])
async def get_scp_element(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ScpElementResponse]:
    _get_owned_product(db, product_id, current_user)
    return [_scp_to_response(e) for e in _list_by_classification(db, product_id, _SCP)]


@router.delete("/{product_id}/elements/scp", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scp_element(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _SCP)
    db.commit()


# ---------------------------------------------------------------------------
# tire
# ---------------------------------------------------------------------------

_TIRE = "tire"


def _tire_to_response(elem: ProductElements) -> TireElementResponse:
    return TireElementResponse(id=elem.id, weight_grams=elem.weight_grams)


@router.post(
    "/{product_id}/elements/tire",
    response_model=list[TireElementResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upsert_tire_element(
    product_id: UUID,
    item: TireElementInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TireElementResponse]:
    """Replace the tire element for a product."""
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _TIRE)
    elem = ProductElements(
        product_id=product_id,
        classification_code=_TIRE,
        weight_grams=item.weight_grams,
        attributes={},
    )
    db.add(elem)
    db.flush()
    db.refresh(elem)
    db.commit()
    return [_tire_to_response(elem)]


@router.get("/{product_id}/elements/tire", response_model=list[TireElementResponse])
async def get_tire_element(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TireElementResponse]:
    _get_owned_product(db, product_id, current_user)
    return [_tire_to_response(e) for e in _list_by_classification(db, product_id, _TIRE)]


@router.delete("/{product_id}/elements/tire", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tire_element(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _TIRE)
    db.commit()


# ---------------------------------------------------------------------------
# transport_pack
# ---------------------------------------------------------------------------

_TRANSPORT_PACK = "transport_pack"


def _transport_pack_to_response(elem: ProductElements) -> TransportPackElementResponse:
    attrs = _attrs_from_model(elem)
    raw = attrs.get("thickness_micron")
    return TransportPackElementResponse(
        id=elem.id,
        name=elem.name,
        material_code=elem.material_code,
        thickness_micron=raw,
        weight_grams=elem.weight_grams,
    )


@router.post(
    "/{product_id}/elements/transport_pack",
    response_model=list[TransportPackElementResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upsert_transport_pack_element(
    product_id: UUID,
    item: TransportPackElementInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TransportPackElementResponse]:
    """Replace the transport packaging element for a product."""
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _TRANSPORT_PACK)
    attrs: dict = {}
    if item.thickness_micron is not None:
        attrs["thickness_micron"] = float(item.thickness_micron)
    elem = ProductElements(
        product_id=product_id,
        classification_code=_TRANSPORT_PACK,
        name=item.name,
        material_code=item.material_code,
        weight_grams=item.weight_grams,
        attributes=attrs,
    )
    db.add(elem)
    db.flush()
    db.refresh(elem)
    db.commit()
    return [_transport_pack_to_response(elem)]


@router.get(
    "/{product_id}/elements/transport_pack",
    response_model=list[TransportPackElementResponse],
)
async def get_transport_pack_element(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TransportPackElementResponse]:
    _get_owned_product(db, product_id, current_user)
    return [_transport_pack_to_response(e) for e in _list_by_classification(db, product_id, _TRANSPORT_PACK)]


@router.delete("/{product_id}/elements/transport_pack", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transport_pack_element(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _TRANSPORT_PACK)
    db.commit()


# ---------------------------------------------------------------------------
# oil
# ---------------------------------------------------------------------------

_OIL = "oil"


def _oil_to_response(elem: ProductElements) -> OilElementResponse:
    attrs = _attrs_from_model(elem)
    return OilElementResponse(
        id=elem.id,
        quantity=attrs.get("quantity"),
        measure_unit=attrs.get("measure_unit"),
    )


@router.post(
    "/{product_id}/elements/oil",
    response_model=list[OilElementResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upsert_oil_element(
    product_id: UUID,
    item: OilElementInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[OilElementResponse]:
    """Replace the oil element for a product."""
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _OIL)
    attrs: dict = {}
    if item.quantity is not None:
        attrs["quantity"] = float(item.quantity)
    if item.measure_unit is not None:
        attrs["measure_unit"] = item.measure_unit
    elem = ProductElements(
        product_id=product_id,
        classification_code=_OIL,
        attributes=attrs,
    )
    db.add(elem)
    db.flush()
    db.refresh(elem)
    db.commit()
    return [_oil_to_response(elem)]


@router.get("/{product_id}/elements/oil", response_model=list[OilElementResponse])
async def get_oil_element(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[OilElementResponse]:
    _get_owned_product(db, product_id, current_user)
    return [_oil_to_response(e) for e in _list_by_classification(db, product_id, _OIL)]


@router.delete("/{product_id}/elements/oil", status_code=status.HTTP_204_NO_CONTENT)
async def delete_oil_element(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _OIL)
    db.commit()


# ---------------------------------------------------------------------------
# eee
# ---------------------------------------------------------------------------

_EEE = "eee"


def _eee_to_response(elem: ProductElements) -> EeeElementResponse:
    attrs = _attrs_from_model(elem)
    return EeeElementResponse(
        id=elem.id,
        height_mm=attrs.get("height_mm"),
        width_mm=attrs.get("width_mm"),
        depth_mm=attrs.get("depth_mm"),
        weight_grams=elem.weight_grams,
        category_code=attrs.get("category_code"),
    )


@router.post(
    "/{product_id}/elements/eee",
    response_model=list[EeeElementResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upsert_eee_element(
    product_id: UUID,
    item: EeeElementInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[EeeElementResponse]:
    """Replace the EEE element for a product."""
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _EEE)
    attrs: dict = {}
    if item.height_mm is not None:
        attrs["height_mm"] = float(item.height_mm)
    if item.width_mm is not None:
        attrs["width_mm"] = float(item.width_mm)
    if item.depth_mm is not None:
        attrs["depth_mm"] = float(item.depth_mm)
    if item.category_code is not None:
        attrs["category_code"] = item.category_code
    elem = ProductElements(
        product_id=product_id,
        classification_code=_EEE,
        weight_grams=item.weight_grams,
        attributes=attrs,
    )
    db.add(elem)
    db.flush()
    db.refresh(elem)
    db.commit()
    return [_eee_to_response(elem)]


@router.get("/{product_id}/elements/eee", response_model=list[EeeElementResponse])
async def get_eee_element(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[EeeElementResponse]:
    _get_owned_product(db, product_id, current_user)
    return [_eee_to_response(e) for e in _list_by_classification(db, product_id, _EEE)]


@router.delete("/{product_id}/elements/eee", status_code=status.HTTP_204_NO_CONTENT)
async def delete_eee_element(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _EEE)
    db.commit()


# ---------------------------------------------------------------------------
# batteries
# ---------------------------------------------------------------------------

_BATTERIES = "batteries"


def _batteries_to_response(elem: ProductElements) -> BatteryElementResponse:
    attrs = _attrs_from_model(elem)
    return BatteryElementResponse(
        id=elem.id,
        chemical_composition_code=attrs.get("chemical_composition_code"),
        weight_grams=elem.weight_grams,
        category_code=attrs.get("category_code"),
    )


@router.post(
    "/{product_id}/elements/batteries",
    response_model=list[BatteryElementResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upsert_batteries_element(
    product_id: UUID,
    item: BatteryElementInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BatteryElementResponse]:
    """Replace the batteries element for a product."""
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _BATTERIES)
    attrs: dict = {}
    if item.chemical_composition_code is not None:
        attrs["chemical_composition_code"] = item.chemical_composition_code
    if item.category_code is not None:
        attrs["category_code"] = item.category_code
    elem = ProductElements(
        product_id=product_id,
        classification_code=_BATTERIES,
        weight_grams=item.weight_grams,
        attributes=attrs,
    )
    db.add(elem)
    db.flush()
    db.refresh(elem)
    db.commit()
    return [_batteries_to_response(elem)]


@router.get("/{product_id}/elements/batteries", response_model=list[BatteryElementResponse])
async def get_batteries_element(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BatteryElementResponse]:
    _get_owned_product(db, product_id, current_user)
    return [_batteries_to_response(e) for e in _list_by_classification(db, product_id, _BATTERIES)]


@router.delete("/{product_id}/elements/batteries", status_code=status.HTTP_204_NO_CONTENT)
async def delete_batteries_element(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _BATTERIES)
    db.commit()


# ---------------------------------------------------------------------------
# sgr
# ---------------------------------------------------------------------------

_SGR = "sgr"


def _sgr_to_response(elem: ProductElements) -> SgrElementResponse:
    attrs = _attrs_from_model(elem)
    return SgrElementResponse(
        id=elem.id,
        material_code=elem.material_code,
        color_code=attrs.get("color_code"),
        has_uv_protection=attrs.get("has_uv_protection"),
        volume_ml=attrs.get("volume_ml"),
        height_wo_cap_mm=attrs.get("height_wo_cap_mm"),
        height_w_cap_mm=attrs.get("height_w_cap_mm"),
        diameter_mm=attrs.get("diameter_mm"),
        weight_grams=elem.weight_grams,
    )


@router.post(
    "/{product_id}/elements/sgr",
    response_model=list[SgrElementResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upsert_sgr_element(
    product_id: UUID,
    item: SgrElementInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SgrElementResponse]:
    """Replace the SGR element for a product."""
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _SGR)
    attrs: dict = {}
    if item.color_code is not None:
        attrs["color_code"] = item.color_code
    if item.has_uv_protection is not None:
        attrs["has_uv_protection"] = item.has_uv_protection
    if item.volume_ml is not None:
        attrs["volume_ml"] = float(item.volume_ml)
    if item.height_wo_cap_mm is not None:
        attrs["height_wo_cap_mm"] = float(item.height_wo_cap_mm)
    if item.height_w_cap_mm is not None:
        attrs["height_w_cap_mm"] = float(item.height_w_cap_mm)
    if item.diameter_mm is not None:
        attrs["diameter_mm"] = float(item.diameter_mm)
    elem = ProductElements(
        product_id=product_id,
        classification_code=_SGR,
        material_code=item.material_code,
        weight_grams=item.weight_grams,
        attributes=attrs,
    )
    db.add(elem)
    db.flush()
    db.refresh(elem)
    db.commit()
    return [_sgr_to_response(elem)]


@router.get("/{product_id}/elements/sgr", response_model=list[SgrElementResponse])
async def get_sgr_element(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SgrElementResponse]:
    _get_owned_product(db, product_id, current_user)
    return [_sgr_to_response(e) for e in _list_by_classification(db, product_id, _SGR)]


@router.delete("/{product_id}/elements/sgr", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sgr_element(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _SGR)
    db.commit()


# ---------------------------------------------------------------------------
# sup
# ---------------------------------------------------------------------------

_SUP = "sup"


def _sup_to_response(elem: ProductElements) -> SupElementResponse:
    attrs = _attrs_from_model(elem)
    return SupElementResponse(
        id=elem.id,
        composition_code=attrs.get("composition_code"),
        percentage_plastic=attrs.get("percentage_plastic"),
        percentage_RPET=attrs.get("percentage_RPET"),
        weight_grams=elem.weight_grams,
    )


@router.post(
    "/{product_id}/elements/sup",
    response_model=list[SupElementResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upsert_sup_element(
    product_id: UUID,
    item: SupElementInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SupElementResponse]:
    """Replace the SUP element for a product."""
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _SUP)
    attrs: dict = {}
    if item.composition_code is not None:
        attrs["composition_code"] = item.composition_code
    if item.percentage_plastic is not None:
        attrs["percentage_plastic"] = float(item.percentage_plastic)
    if item.percentage_RPET is not None:
        attrs["percentage_RPET"] = float(item.percentage_RPET)
    elem = ProductElements(
        product_id=product_id,
        classification_code=_SUP,
        weight_grams=item.weight_grams,
        attributes=attrs,
    )
    db.add(elem)
    db.flush()
    db.refresh(elem)
    db.commit()
    return [_sup_to_response(elem)]


@router.get("/{product_id}/elements/sup", response_model=list[SupElementResponse])
async def get_sup_element(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SupElementResponse]:
    _get_owned_product(db, product_id, current_user)
    return [_sup_to_response(e) for e in _list_by_classification(db, product_id, _SUP)]


@router.delete("/{product_id}/elements/sup", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sup_element(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    _get_owned_product(db, product_id, current_user)
    _delete_by_classification(db, product_id, _SUP)
    db.commit()
