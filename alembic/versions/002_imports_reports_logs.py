"""Create import, reporting, file storage, and log tables

Revision ID: 002_imports_reports_logs
Revises: 001_initial
Create Date: 2026-05-17 00:00:00.000000

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "002_imports_reports_logs"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Generic metadata for files stored in S3-compatible object storage.
    # Used for uploaded Excel files, generated reports, and later other file types.
    op.create_table(
        "stored_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("uploaded_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("file_type", sa.String(50), nullable=False),  # import_excel, report_excel, etc.
        sa.Column("original_filename", sa.String(255), nullable=True),
        sa.Column("mime_type", sa.String(255), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("storage_bucket", sa.String(255), nullable=True),
        sa.Column("storage_key", sa.String(1024), nullable=False),
        sa.Column("checksum_sha256", sa.String(64), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_stored_files_company_id", "stored_files", ["company_id"])
    op.create_index("ix_stored_files_uploaded_by_user_id", "stored_files", ["uploaded_by_user_id"])
    op.create_index("ix_stored_files_file_type", "stored_files", ["file_type"])
    op.create_index("ix_stored_files_storage_key", "stored_files", ["storage_key"], unique=True)

    # One uploaded monthly import. It references stored_files, but also keeps the most useful
    # file metadata here for simple listing/filtering in the import UI.
    op.create_table(
        "import_batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("uploaded_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("stored_file_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("period_year", sa.Integer(), nullable=False),
        sa.Column("period_month", sa.Integer(), nullable=False),
        sa.Column("import_format", sa.String(100), nullable=False, server_default="default_excel"),
        sa.Column("status", sa.String(50), nullable=False, server_default="uploaded"),
        # Duplicated file summary for fast list views and easier debugging.
        sa.Column("original_filename", sa.String(255), nullable=True),
        sa.Column("total_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("valid_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("warning_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("matched_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unmatched_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["stored_file_id"], ["stored_files.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("period_month >= 1 AND period_month <= 12", name="ck_import_batches_period_month"),
        sa.CheckConstraint("period_year >= 2000", name="ck_import_batches_period_year"),
    )
    op.create_index("ix_import_batches_company_id", "import_batches", ["company_id"])
    op.create_index("ix_import_batches_uploaded_by_user_id", "import_batches", ["uploaded_by_user_id"])
    op.create_index("ix_import_batches_stored_file_id", "import_batches", ["stored_file_id"])
    op.create_index("ix_import_batches_status", "import_batches", ["status"])
    op.create_index("ix_import_batches_company_period", "import_batches", ["company_id", "period_year", "period_month"])

    # Parsed rows from the uploaded Excel file. matched_product_id is the source of truth for
    # whether a row is matched; match_status captures the workflow state.
    op.create_table(
        "import_rows",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("import_batch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("raw_data_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("external_sku", sa.String(100), nullable=True),
        sa.Column("external_product_name", sa.String(255), nullable=True),
        sa.Column("document_date", sa.DateTime(), nullable=True, server_default=None),
        sa.Column("document_number", sa.String(50), nullable=True),
        sa.Column("invoice_number", sa.String(50), nullable=True),
        sa.Column("quantity", sa.Numeric(precision=14, scale=3), nullable=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("normalized_quantity_units", sa.Numeric(precision=14, scale=3), nullable=True),
        sa.Column("matched_product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resolved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["import_batch_id"], ["import_batches.id"]),
        sa.ForeignKeyConstraint(["matched_product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["resolved_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("import_batch_id", "row_number", name="uq_import_rows_batch_row_number"),
    )
    op.create_index("ix_import_rows_import_batch_id", "import_rows", ["import_batch_id"])
    op.create_index("ix_import_rows_external_sku", "import_rows", ["external_sku"])
    op.create_index("ix_import_rows_external_product_name", "import_rows", ["external_product_name"])
    op.create_index("ix_import_rows_matched_product_id", "import_rows", ["matched_product_id"])
    op.create_index("ix_import_rows_match_status", "import_rows", ["match_status"])
    op.create_index("ix_import_rows_resolved_by_user_id", "import_rows", ["resolved_by_user_id"])
    op.create_index(
        "ix_import_rows_unmatched_partial",
        "import_rows",
        ["import_batch_id"],
        postgresql_where=sa.text("matched_product_id IS NULL"),
    )

    # Validation messages related to imported files/rows.
    op.create_table(
        "import_validation_errors",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("import_batch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("import_row_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("severity", sa.String(50), nullable=False, server_default="error"),  # error, warning, info
        sa.Column("error_code", sa.String(100), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["import_batch_id"], ["import_batches.id"]),
        sa.ForeignKeyConstraint(["import_row_id"], ["import_rows.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_import_validation_errors_import_batch_id", "import_validation_errors", ["import_batch_id"])
    op.create_index("ix_import_validation_errors_import_row_id", "import_validation_errors", ["import_row_id"])
    op.create_index("ix_import_validation_errors_severity", "import_validation_errors", ["severity"])
    op.create_index("ix_import_validation_errors_error_code", "import_validation_errors", ["error_code"])

    # Generated reports, e.g. OTR Excel report for a period.
    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("stored_file_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("report_type", sa.String(50), nullable=False, server_default="OTR"),
        sa.Column("period_year", sa.Integer(), nullable=False),
        sa.Column("period_month", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("generated_filename", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("generated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["stored_file_id"], ["stored_files.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("period_month >= 1 AND period_month <= 12", name="ck_reports_period_month"),
        sa.CheckConstraint("period_year >= 2000", name="ck_reports_period_year"),
    )
    op.create_index("ix_reports_company_id", "reports", ["company_id"])
    op.create_index("ix_reports_created_by_user_id", "reports", ["created_by_user_id"])
    op.create_index("ix_reports_stored_file_id", "reports", ["stored_file_id"])
    op.create_index("ix_reports_status", "reports", ["status"])
    op.create_index("ix_reports_type", "reports", ["report_type"])
    op.create_index("ix_reports_company_period", "reports", ["company_id", "period_year", "period_month"])

    # One-to-many mapping between generated reports and the import batches used as input.
    op.create_table(
        "report_to_import_batch",
        sa.Column("report_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("import_batch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["report_id"], ["reports.id"]),
        sa.ForeignKeyConstraint(["import_batch_id"], ["import_batches.id"]),
        sa.PrimaryKeyConstraint("report_id", "import_batch_id"),
    )
    op.create_index("ix_report_to_import_batch_report_id", "report_to_import_batch", ["report_id"])
    op.create_index("ix_report_to_import_batch_import_batch_id", "report_to_import_batch", ["import_batch_id"])

    # Aggregated report data. Usually one row per material / packaging type / subtype combination.
    op.create_table(
        "report_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("report_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("material", sa.String(100), nullable=False),
        sa.Column("packaging_type", sa.String(50), nullable=True),  # primary, secondary, tertiary
        sa.Column("packaging_subtype", sa.String(100), nullable=True),  # commercial, municipal, etc.
        sa.Column("total_quantity_units", sa.Numeric(precision=14, scale=3), nullable=True),
        sa.Column("total_weight_grams", sa.Numeric(precision=14, scale=3), nullable=False, server_default="0"),
        sa.Column("total_weight_kg", sa.Numeric(precision=14, scale=6), nullable=False, server_default="0"),
        sa.Column("source_row_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("source_product_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("details_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["report_id"], ["reports.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_report_lines_report_id", "report_lines", ["report_id"])
    op.create_index("ix_report_lines_material", "report_lines", ["material"])
    op.create_index(
        "ix_report_lines_report_material_type_subtype",
        "report_lines",
        ["report_id", "material", "packaging_type", "packaging_subtype"],
    )

    # General application log messages. The scope fields are intentionally generic so logs can
    # be filtered by company, user, module, entity, import, report, request/correlation id, etc.
    op.create_table(
        "log_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "severity", sa.String(50), nullable=False, server_default="info"
        ),  # debug, info, warning, error, critical
        sa.Column("module", sa.String(100), nullable=True),  # auth, import, matching, reporting, admin, etc.
        sa.Column("event_type", sa.String(100), nullable=True),  # import_started, report_generated, login_failed, etc.
        sa.Column(
            "scope_type", sa.String(100), nullable=True
        ),  # platform, company, import_batch, report, product, etc.
        sa.Column("scope_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("entity_type", sa.String(100), nullable=True),  # table, module, etc
        sa.Column("entity_name", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("details_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_log_messages_company_id", "log_messages", ["company_id"])
    op.create_index("ix_log_messages_user_id", "log_messages", ["user_id"])
    op.create_index("ix_log_messages_severity", "log_messages", ["severity"])
    op.create_index("ix_log_messages_module", "log_messages", ["module"])
    op.create_index("ix_log_messages_event_type", "log_messages", ["event_type"])
    op.create_index("ix_log_messages_scope", "log_messages", ["scope_type", "scope_id"])
    op.create_index("ix_log_messages_entity", "log_messages", ["entity_type", "entity_id"])
    op.create_index("ix_log_messages_correlation_id", "log_messages", ["correlation_id"])
    op.create_index("ix_log_messages_created_at", "log_messages", ["created_at"])


def downgrade() -> None:
    op.drop_table("log_messages")
    op.drop_table("report_lines")
    op.drop_table("report_to_import_batch")
    op.drop_table("reports")
    op.drop_table("import_validation_errors")
    op.drop_table("import_rows")
    op.drop_table("import_batches")
    op.drop_table("stored_files")
