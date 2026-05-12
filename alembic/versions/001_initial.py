"""Initial migration: create all tables

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create companies table
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("address_type", sa.String(100), nullable=True),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("county", sa.String(100), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column("street", sa.String(255), nullable=True),
        sa.Column("street_number", sa.String(50), nullable=True),
        sa.Column("building", sa.String(50), nullable=True),
        sa.Column("entrance", sa.String(50), nullable=True),
        sa.Column("floor", sa.String(50), nullable=True),
        sa.Column("apartment", sa.String(50), nullable=True),
        sa.Column("additional_address_info", sa.Text(), nullable=True),
        sa.Column("vat_number", sa.String(50), nullable=True),
        sa.Column("registration_number", sa.String(50), nullable=True),
        sa.Column("phone_number", sa.String(20), nullable=True),
        sa.Column("role", sa.String(50), nullable=False, server_default="customer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("phone_number", sa.String(20), nullable=True),
        sa.Column("role", sa.String(50), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_company_id", "users", ["company_id"])
    op.create_index("ix_users_email", "users", ["email"])

    # Create products table
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sku", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(255), nullable=True),
        sa.Column("case_pack_quantity", sa.Integer(), nullable=True),
        sa.Column("pallet_quantity", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_company_id", "products", ["company_id"])
    op.create_index("ix_products_sku", "products", ["sku"])
    op.create_index("ix_products_company_sku", "products", ["company_id", "sku"], unique=True)

    # Create whiteball_packaging_items table
    op.create_table(
        "whiteball_packaging_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("subtype", sa.String(100), nullable=True),
        sa.Column("material", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("weight_grams", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("source_id", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create packaging_items table
    op.create_table(
        "packaging_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("subtype", sa.String(100), nullable=True),
        sa.Column("material", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("weight_grams", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("matched_with_reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["matched_with_reference_id"],
            ["whiteball_packaging_items.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_packaging_items_company_id", "packaging_items", ["company_id"])

    # Create product_packaging_associations table
    op.create_table(
        "product_packaging_associations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("packaging_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quantity_per_product_unit", sa.Numeric(precision=10, scale=2), nullable=False, server_default="1"),
        sa.Column("applies_to_unit", sa.String(50), nullable=False, server_default="unit"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["packaging_item_id"],
            ["packaging_items.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_product_packaging_associations_product_id", "product_packaging_associations", ["product_id"])
    op.create_index(
        "ix_product_packaging_associations_packaging_item_id", "product_packaging_associations", ["packaging_item_id"]
    )


def downgrade() -> None:
    op.drop_table("product_packaging_associations")
    op.drop_table("packaging_items")
    op.drop_table("whiteball_packaging_items")
    op.drop_table("products")
    op.drop_table("users")
    op.drop_table("companies")
