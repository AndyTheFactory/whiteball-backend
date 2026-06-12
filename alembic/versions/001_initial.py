"""Initial migration: create all tables

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op
from data.data_001 import seed_data as initial_data

# revision identifiers, used by Alembic.
revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create dictionary_types and dictionary_values tables for configurable dropdowns and reference data
    op.create_table(
        "dictionary_types",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "code",
            sa.String(length=100),
            nullable=False,
            comment="Stable machine-readable code for the dictionary type. "
            "Ex values: 'packaging_materials', 'battery_types'.",
        ),
        sa.Column("name", sa.String(length=255), nullable=False, comment="Human-readable name of the dictionary type."),
        sa.UniqueConstraint("code", name="uq_dictionary_types_code"),
        comment="Defines groups of configurable dictionary values, "
        "such as packaging materials, packaging types, or battery types.",
    )

    # Create dictionary_values table with a foreign key to dictionary_types, and
    # fields for code, names in multiple languages, active status, and sort order
    op.create_table(
        "dictionary_values",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "dictionary_type_code",
            sa.String(length=100),
            sa.ForeignKey("dictionary_types.code", ondelete="CASCADE"),
            nullable=False,
            comment="Dictionary type this value belongs to.",
        ),
        sa.Column(
            "code",
            sa.String(length=100),
            nullable=False,
            comment="Stable machine-readable code used in imports, exports, APIs, and business logic. "
            "Ex values for a 'packaging_materials' type: 'plastic', 'paper', 'metal'.",
        ),
        sa.Column("name_ro", sa.String(length=255), nullable=False, comment="Romanian display label."),
        sa.Column("name_en", sa.String(length=255), nullable=True, comment="English display label."),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.UniqueConstraint("dictionary_type_code", "code", name="uq_dictionary_values_type_code"),
        sa.UniqueConstraint("code", name="uq_dictionary_values_code"),
        comment="Stores configurable values for each dictionary type.",
    )

    op.create_index("ix_dictionary_values_dictionary_type_code", "dictionary_values", ["dictionary_type_code"])

    op.create_index("ix_dictionary_values_is_active", "dictionary_values", ["is_active"])

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
        sa.Column(
            "role", sa.Enum("customer", "admin", name="company_roles"), nullable=False, server_default="customer"
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        comment="Table to store company information, including address and contact details",
    )
    op.create_index("ix_companies_country", "companies", ["country"])
    op.create_index("ix_companies_city", "companies", ["city"])

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("phone_number", sa.String(20), nullable=True),
        sa.Column("role", sa.Enum("user", "admin", name="user_roles"), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        comment="Table to store user information, linked to companies, with roles and contact details",
    )
    op.create_index("ix_users_company_id", "users", ["company_id"])
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_full_name", "users", ["full_name"])

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
        sa.Column("net_weight", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("manufacturer", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        comment="Table to store product information, linked to companies, with SKU and other details",
    )
    op.create_index("ix_products_company_id", "products", ["company_id"])
    op.create_index("ix_products_sku", "products", ["sku"])
    op.create_index("ix_products_company_sku", "products", ["company_id", "sku"], unique=True)

    # Create product_classifications table
    op.create_table(
        "product_classifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("classification_code", sa.String(50), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.ForeignKeyConstraint(
            ["classification_code"],
            ["dictionary_values.code"],
        ),
        sa.PrimaryKeyConstraint("id"),
        comment="Table to store product classifications (packaging, sgr, batteries, etc.),"
        " linking products to classification codes from the dictionary_values table",
    )
    op.create_index("ix_product_classifications_product_id", "product_classifications", ["product_id"])
    op.create_index(
        "ix_product_classifications_classification_code", "product_classifications", ["classification_code"]
    )

    # Create product_elements table
    op.create_table(
        "product_elements",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("classification_code", sa.String(50), nullable=False),
        sa.Column("type_code", sa.String(50), nullable=True),
        sa.Column("material_code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("weight_grams", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "attributes",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["classification_code"],
            ["dictionary_values.code"],
        ),
        sa.ForeignKeyConstraint(
            ["type_code"],
            ["dictionary_values.code"],
        ),
        sa.ForeignKeyConstraint(
            ["material_code"],
            ["dictionary_values.code"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_product_elements_company_id", "product_elements", ["company_id"])

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

    # Bulk insert seed data in order respecting foreign key constraints
    if initial_data.get("dictionary_types"):
        op.bulk_insert(
            sa.table(
                "dictionary_types",
                sa.Column("id", sa.Uuid()),
                sa.Column("code", sa.String(length=100)),
                sa.Column("name", sa.String(length=255)),
            ),
            initial_data["dictionary_types"],
        )

    if initial_data.get("dictionary_values"):
        op.bulk_insert(
            sa.table(
                "dictionary_values",
                sa.Column("id", sa.Uuid()),
                sa.Column("dictionary_type_code", sa.String(length=100)),
                sa.Column("code", sa.String(length=100)),
                sa.Column("name_ro", sa.String(length=255)),
                sa.Column("name_en", sa.String(length=255)),
                sa.Column("is_active", sa.Boolean()),
                sa.Column("sort_order", sa.Integer()),
            ),
            initial_data["dictionary_values"],
        )

    if initial_data.get("companies"):
        op.bulk_insert(
            sa.table(
                "companies",
                sa.Column("id", postgresql.UUID(as_uuid=True)),
                sa.Column("name", sa.String(255)),
                sa.Column("address_type", sa.String(100)),
                sa.Column("country", sa.String(100)),
                sa.Column("county", sa.String(100)),
                sa.Column("city", sa.String(100)),
                sa.Column("postal_code", sa.String(20)),
                sa.Column("street", sa.String(255)),
                sa.Column("street_number", sa.String(50)),
                sa.Column("building", sa.String(50)),
                sa.Column("entrance", sa.String(50)),
                sa.Column("floor", sa.String(50)),
                sa.Column("apartment", sa.String(50)),
                sa.Column("additional_address_info", sa.Text()),
                sa.Column("vat_number", sa.String(50)),
                sa.Column("registration_number", sa.String(50)),
                sa.Column("phone_number", sa.String(20)),
                sa.Column("role", sa.String(50)),
                sa.Column("is_active", sa.Boolean()),
            ),
            initial_data["companies"],
        )

    if initial_data.get("users"):
        op.bulk_insert(
            sa.table(
                "users",
                sa.Column("id", postgresql.UUID(as_uuid=True)),
                sa.Column("company_id", postgresql.UUID(as_uuid=True)),
                sa.Column("email", sa.String(255)),
                sa.Column("password_hash", sa.String(255)),
                sa.Column("full_name", sa.String(255)),
                sa.Column("phone_number", sa.String(20)),
                sa.Column("role", sa.String(50)),
                sa.Column("is_active", sa.Boolean()),
            ),
            initial_data["users"],
        )

    if initial_data.get("products"):
        op.bulk_insert(
            sa.table(
                "products",
                sa.Column("id", postgresql.UUID(as_uuid=True)),
                sa.Column("company_id", postgresql.UUID(as_uuid=True)),
                sa.Column("sku", sa.String(100)),
                sa.Column("name", sa.String(255)),
                sa.Column("category", sa.String(255)),
                sa.Column("case_pack_quantity", sa.Integer()),
                sa.Column("pallet_quantity", sa.Integer()),
                sa.Column("net_weight", sa.Numeric(precision=10, scale=2)),
                sa.Column("manufacturer", sa.String(255)),
                sa.Column("description", sa.Text()),
                sa.Column("is_active", sa.Boolean()),
            ),
            initial_data["products"],
        )

    if initial_data.get("product_classifications"):
        op.bulk_insert(
            sa.table(
                "product_classifications",
                sa.Column("id", postgresql.UUID(as_uuid=True)),
                sa.Column("product_id", postgresql.UUID(as_uuid=True)),
                sa.Column("classification_code", sa.String(50)),
            ),
            initial_data["product_classifications"],
        )

    if initial_data.get("product_elements"):
        op.bulk_insert(
            sa.table(
                "product_elements",
                sa.Column("id", postgresql.UUID(as_uuid=True)),
                sa.Column("company_id", postgresql.UUID(as_uuid=True)),
                sa.Column("classification_code", sa.String(50)),
                sa.Column("type_code", sa.String(50)),
                sa.Column("material_code", sa.String(50)),
                sa.Column("name", sa.String(255)),
                sa.Column("description", sa.Text()),
                sa.Column("weight_grams", sa.Numeric(precision=10, scale=2)),
                sa.Column("attributes", postgresql.JSONB()),
            ),
            initial_data["product_elements"],
        )

    if initial_data.get("whiteball_packaging_items"):
        op.bulk_insert(
            sa.table(
                "whiteball_packaging_items",
                sa.Column("id", postgresql.UUID(as_uuid=True)),
                sa.Column("type", sa.String(50)),
                sa.Column("subtype", sa.String(100)),
                sa.Column("material", sa.String(100)),
                sa.Column("name", sa.String(255)),
                sa.Column("description", sa.Text()),
                sa.Column("weight_grams", sa.Numeric(precision=10, scale=2)),
                sa.Column("source_id", sa.String(100)),
            ),
            initial_data["whiteball_packaging_items"],
        )


def downgrade() -> None:
    # Drop in reverse order of creation to respect foreign key constraints

    op.drop_index("ix_product_classifications_classification_code", table_name="product_classifications")
    op.drop_index("ix_product_classifications_product_id", table_name="product_classifications")
    op.drop_table("product_classifications")

    op.drop_index("ix_product_elements_company_id", table_name="product_elements")
    op.drop_table("product_elements")

    op.drop_index("ix_products_company_sku", table_name="products")
    op.drop_index("ix_products_sku", table_name="products")
    op.drop_index("ix_products_company_id", table_name="products")
    op.drop_table("products")

    op.drop_table("whiteball_packaging_items")

    op.drop_index("ix_users_full_name", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_company_id", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_companies_city", table_name="companies")
    op.drop_index("ix_companies_country", table_name="companies")
    op.drop_table("companies")

    op.drop_index("ix_dictionary_values_is_active", table_name="dictionary_values")
    op.drop_index("ix_dictionary_values_dictionary_type_code", table_name="dictionary_values")

    op.drop_table("dictionary_values")
    op.drop_table("dictionary_types")

    # Then drop enum types
    op.execute("DROP TYPE IF EXISTS company_roles")
    op.execute("DROP TYPE IF EXISTS user_roles")
