"""Base SQLAlchemy model."""

from importlib import import_module

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


def import_all_models() -> None:
    """Import all model modules so Base metadata is populated."""
    for module in (
        "app.models.company",
        "app.models.dictionary",
        "app.models.user",
        "app.models.product",
        "app.models.product_elements",
        "app.models.product_classification",
        "app.models.reference_table",
    ):
        import_module(module)


import_all_models()
