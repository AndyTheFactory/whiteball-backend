Below is a backend implementation outline you can give to **Claude Code** for building **Milestone 1**. It is written as an engineering task brief, focused on the backend only.

---

# Backend Implementation Outline — Milestone 1

## Whiteball Database Integration and Product / Packaging Catalog

## 1. Project Context

Build the backend foundation for an online packaging reporting platform. In Milestone 1, the goal is to implement the core data model and API needed for managing products, packaging items, and the association between them.

This milestone does **not** include the full multi-company system, full user administration, import processing workflows, matching logic, reporting, dashboard calculations, or OTR report generation. Those are planned for later milestones.
---

## 2. Backend Scope for Milestone 1

Implement the backend for:

1. Authentication any company account.
2. Database structure for:

   * companies;
   * users (foreign key to companies);
   * products-catalog (foreign key to companies);
   * packaging items (foreign key to companies and to product-catalog);
   * product-packaging associations;
   * Large packaging reference data (package-reference).
3. Manual initial loading of the package-reference database.
4. API endpoints for:

   * login / current user;
   * listing, searching, filtering products;
   * viewing a product (details);
   * creating and editing products;
   * listing packaging associated with a product;
   * creating, editing, deleting packaging associations;
   * searching package-reference by various criteria.
5. Basic validation and error handling.
6. Seed data for one test company and one test user.
7. API documentation through OpenAPI / Swagger.

---

## 3. Recommended Technical Stack

Use the following stack unless the existing project already defines another one:

* **Python 3.12+**
* **FastAPI** for the backend API
* **PostgreSQL** as the main database
* **SQLAlchemy 2.x** or SQLModel for ORM
* **Alembic** for migrations
* **Pydantic v2** for schemas and validation
* **JWT authentication** with email/password login
* **Passlib / bcrypt** for password hashing
* **Docker Compose** for local development with API + PostgreSQL
* **Pytest** for backend tests

---

## 4. Suggested Project Structure

```text
backend/
  app/
    main.py
    core/
      config.py
      security.py
      auth.py
      exceptions.py
    db/
      session.py
      base.py
      init_db.py
    models/
      company.py
      user.py
      product.py
      packaging.py
      packaging_reference.py
    schemas/
      auth.py
      user.py
      product.py
      packaging.py
      packaging_reference.py
      common.py
    api/
      deps.py
      router.py
      routes/
        auth.py
        products.py
        packaging.py
        packaging_reference.py
    services/
      product_service.py
      packaging_service.py
      packaging_reference_import_service.py
    repositories/
      product_repository.py
      packaging_repository.py
      packaging_reference_repository.py
    scripts/
      seed_test_company.py
      import_packaging_reference.py
  alembic/
  tests/
  docker-compose.yml
  Dockerfile
  pyproject.toml
  README.md
```

---

## 5. Data Model

### 5.1 Company

Even though full multi-company support is not part of Milestone 1, create a minimal `companies` table so the backend is ready for later isolation.

Fields:

```text
id: UUID / integer primary key
name: string
address_type
country
county
city
postal_code
street
street_number
building
entrance
floor
apartment
additional_address_info
vat_number
registration_number
phone_number
role: enum, values: admin, customer
is_active: boolean
created_at: datetime
updated_at: datetime
```

For Milestone 1, seed one company manually, for example:

```text
Whiteball Test Company
```

---

### 5.2 User

Minimal authentication user model.

Fields:

```text
id
company_id -> companies.id
email: string, unique
password_hash: string
full_name: string nullable
phone_number
role: enum, values: admin, user
is_active: boolean
created_at
updated_at
```

For this milestone, role handling can be basic. The main requirement is that a test user can log in and access the product catalog.

---

### 5.3 Product

Product catalog model.

Fields:

```text
id
company_id -> companies.id
sku: string
name: string
category: string nullable
case_pack_quantity: integer nullable
pallet_quantity: integer nullable
description: text nullable
is_active: boolean
created_at
updated_at
```

Notes:

* `sku` should be unique per company.
* Add an index on `company_id`.
* Add an index on `sku`.
* Add text search support later if needed, but for Milestone 1 simple `ILIKE` search is enough.
* `case_pack_quantity` corresponds to baxare.
* `pallet_quantity` corresponds to paletare.

Suggested uniqueness rule:

```text
unique(company_id, sku)
```

---

### 5.4 Packaging Item

This represents a packaging component that can be associated with one or more products.

Fields:

```text
id
company_id -> companies.id
type: enum
subtype: enum / string
material: enum / string
name: string
description: text nullable
weight_grams: numeric
matched_with_reference_id: nullable foreign key to packaging_reference.id
created_at
updated_at
```

Suggested `type` values:

```text
primary
secondary
tertiary
```

Suggested `subtype` examples:

```text
commercial
municipal
unknown
```

Suggested `material` examples:

```text
plastic
pet
glass
paper_cardboard
metal
aluminium
wood
other
```

Use enums only if the material list is reasonably stable. Otherwise, use a lookup table or string field to avoid migration overhead.

---

### 5.5 Product Packaging Association

This table links products to packaging items.

Fields:

```text
id
product_id -> products.id
packaging_item_id -> packaging_items.id
quantity_per_product_unit: numeric (decimal), default 1
notes: text nullable
applies_to_unit: enum/string, e.g. unit, case, pallet
created_at
updated_at
```

For Milestone 1, keep this simple unless the reporting calculation already needs more structure.

---

### 5.6 Packaging Reference Tables

Create separate tables for the manually loaded packaging reference database. Do not mix raw packaging reference source data directly into editable company data.

Suggested model:


```text
whiteball_packaging_items
  id
  type
  subtype
  material
  name
  description nullable
  weight_grams numeric nullable
  source_id string nullable
  created_at
  updated_at
```

Important: the Whiteball import in this milestone should be a manual admin/developer script, not an end-user upload feature.

---

## 6. Authentication Requirements

Implement:

### Endpoints

```http
POST /auth/login
GET /auth/me
```

### Login Request

```json
{
  "email": "test@example.com",
  "password": "password"
}
```

### Login Response

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "test@example.com",
    "company_id": "...",
    "role": "admin"
  }
}
```

Authentication rules:

* Passwords must be hashed.
* JWT should include at least:

  * `sub`: user id;
  * `company_id`;
  * `role`;
  * expiration.
* All catalog endpoints should require authentication.
* All product and packaging queries must be scoped to the authenticated user’s company.

---

## 7. Product API Endpoints

### 7.1 List Products

```http
GET /products
```

Query parameters:

```text
search: optional string
category: optional string
is_active: optional boolean
limit: default 50
offset: default 0
sort_by: optional, default name
sort_order: asc / desc
```

Response:

```json
{
  "items": [
    {
      "id": "...",
      "sku": "SKU-001",
      "name": "Product name",
      "category": "Category",
      "case_pack_quantity": 12,
      "pallet_quantity": 720,
      "packaging_count": 3
    }
  ],
  "total": 120,
  "limit": 50,
  "offset": 0
}
```

---

### 7.2 Get Product Detail

```http
GET /products/{product_id}
```

Include associated packaging in the response.

```json
{
  "id": "...",
  "sku": "SKU-001",
  "name": "Product name",
  "category": "Category",
  "case_pack_quantity": 12,
  "pallet_quantity": 720,
  "packaging": [
    {
      "association_id": "...",
      "packaging_item_id": "...",
      "type": "primary",
      "subtype": "commercial",
      "material": "plastic",
      "name": "Plastic bottle",
      "weight_grams": 25.5,
      "quantity_per_product_unit": 1
    }
  ]
}
```

---

### 7.3 Create Product

```http
POST /products
```

Request:

```json
{
  "sku": "SKU-001",
  "name": "Product name",
  "category": "Category",
  "case_pack_quantity": 12,
  "pallet_quantity": 720,
  "description": "Optional notes"
}
```

Validation:

* `sku` is required.
* `name` is required.
* `sku` must be unique within the authenticated company.
* `case_pack_quantity` and `pallet_quantity` must be positive integers if provided.

---

### 7.4 Update Product

```http
PATCH /products/{product_id}
```

Allow partial updates.

```json
{
  "name": "Updated product name",
  "category": "Updated category",
  "case_pack_quantity": 24
}
```

Rules:

* Only update products belonging to the authenticated user’s company.
* Return `404` if the product does not exist or is outside the company scope.

---

### 7.5 Soft Delete / Deactivate Product

Optional for Milestone 1, but useful:

```http
DELETE /products/{product_id}
```

Instead of hard delete, set:

```text
is_active = false
```

---

## 8. Packaging API Endpoints

### 8.1 List Packaging Items

```http
GET /packaging-items
```

Query parameters:

```text
search
product_id
product_sku
type
subtype
material
limit
offset
```

This endpoint supports reuse and lookup of packaging items.

---

### 8.2 Create Packaging Item

```http
POST /packaging-items
```

Request:

```json
{
  "type": "primary",
  "subtype": "commercial",
  "material": "plastic",
  "name": "Plastic bottle",
  "description": "500ml PET bottle",
  "weight_grams": 25.5
}
```

Validation:

* `type`, `material`, `name`, and `weight_grams` are required.
* `weight_grams` must be greater than or equal to 0.

---

### 8.3 Update Packaging Item

```http
PATCH /packaging-items/{packaging_item_id}
```

Allow editing fields.

---

### 8.4 Associate Packaging with Product

```http
POST /products/{product_id}/packaging
```

Option A — create a new packaging item and associate it:

```json
{
  "packaging_item": {
    "type": "primary",
    "subtype": "commercial",
    "material": "plastic",
    "name": "Plastic bottle",
    "description": "500ml PET bottle",
    "weight_grams": 25.5
  },
  "quantity_per_product_unit": 1
}
```

Option B — associate an existing packaging item:

```json
{
  "packaging_item_id": "...",
  "quantity_per_product_unit": 1
}
```

Implement both.

---

### 8.5 Update Product Packaging Association

```http
PATCH /products/{product_id}/packaging/{association_id}
```

Request:

```json
{
  "quantity_per_product_unit": 2,
  "packaging_item": {
    "weight_grams": 26.0,
    "material": "pet"
  }
}
```

For simplicity, this can update the association and optionally the packaging item.

---

### 8.6 Remove Packaging from Product

```http
DELETE /products/{product_id}/packaging/{association_id}
```

Remove only the association, not necessarily the packaging item itself.

---

### 8.7 Remove Packaging Item
```http
DELETE /packaging-items/{packaging_item_id}
```
Remove the packaging item itself. This should also remove all associations with products.
---

## 9. Seeding Requirements

Implement a seed script:

```bash
python -m app.scripts.seed_test_company
```

It should create:

```text
Company:
  name: Whiteball Test Company

User:
  email: admin@test.local
  password: configurable through env var
  role: admin
```

Use environment variables for default credentials where possible.

Example:

```env
TEST_ADMIN_EMAIL=admin@test.local
TEST_ADMIN_PASSWORD=change-me
```

---

## 10. Validation and Business Rules

Implement the following backend validation rules:

### Product

* SKU required.
* Name required.
* SKU unique per company.
* Case pack quantity must be positive if provided.
* Pallet quantity must be positive if provided.
* Product queries must always be scoped by `company_id`.

### Packaging

* Type required.
* Material required.
* Name required.
* Weight required.
* Weight must be non-negative.
* Packaging records must belong to the authenticated company.
* Product-packaging associations must not cross company boundaries.

### Authentication

* Inactive users cannot log in.
* Invalid credentials return `401`.
* Missing or expired token returns `401`.
* Protect against timing attacks on login endpoint.
* Protect agains brute force attacks (e.g. rate limiting, account lockout after multiple failed attempts).
* Ensure password hashing is secure (e.g. bcrypt with appropriate work factor, salting).

---

## 11. Error Handling

Use consistent API error responses.

Example:

```json
{
  "detail": {
    "code": "PRODUCT_SKU_ALREADY_EXISTS",
    "message": "A product with this SKU already exists for this company."
  }
}
```

Suggested error codes:

```text
AUTH_INVALID_CREDENTIALS
AUTH_INACTIVE_USER
PRODUCT_NOT_FOUND
PRODUCT_SKU_ALREADY_EXISTS
PACKAGING_ITEM_NOT_FOUND
PRODUCT_PACKAGING_ASSOCIATION_NOT_FOUND
VALIDATION_ERROR
```

---

## 12. Acceptance Criteria for Backend

The backend for Milestone 1 is complete when:

1. A test company and test user can be seeded.
2. The user can authenticate using email and password.
3. Authenticated requests are scoped to the test company.
4. Whiteball data can be manually loaded through a backend script.
5. Products can be listed, searched, filtered, created, edited, and retrieved.
6. Product data includes SKU, name, category, case pack quantity, and pallet quantity.
7. Packaging items can be created and edited.
8. Packaging items can be associated with products.
9. Product detail responses include associated packaging.
10. Product-packaging associations can be updated and removed.
11. The API exposes OpenAPI documentation.
12. Basic automated tests cover authentication, product CRUD, packaging CRUD, and product-packaging association flows.

---

## 14. Tests to Implement

Create tests for:

### Authentication

```text
test_login_success
test_login_invalid_password
test_get_current_user
test_protected_endpoint_requires_token
```

### Products

```text
test_create_product
test_create_product_duplicate_sku_same_company_fails
test_list_products
test_search_products_by_sku_or_name
test_filter_products_by_category
test_update_product
test_get_product_detail
```

### Packaging

```text
test_create_packaging_item
test_update_packaging_item
test_associate_packaging_with_product
test_update_product_packaging_association
test_remove_packaging_from_product
```

### Whiteball Import

```text
test_whiteball_import_valid_file
test_whiteball_import_missing_required_columns_fails
test_whiteball_import_is_idempotent
```

---

## 15. Development Instructions for Copilot Agent

Implement this incrementally:

1. Create project skeleton and configuration. Create pre-commit hooks for linting and formatting. use uv tooling for virtual environment and dependency management.
2. Add database connection and Alembic migrations.
3. Implement models.
4. Implement authentication and test user seed.
5. Implement product CRUD.
6. Implement packaging CRUD.
7. Implement product-packaging association endpoints.
8. Add docker compose and dockerfile to instantiate the development environment.
9. Add tests.
10. Create CI/CD pipeline for ensuring formats, code quality, spellchecking, and running tests on push.
11. Add README with local setup, migrations, seed, and import commands.

The backend should prioritize clean data modeling and reliable API behavior over premature optimization. Keep the implementation simple, but design the database so later milestones can add monthly imports, matching, reporting, and true multi-company isolation without major rewrites.
