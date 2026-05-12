# Whiteball Backend — Milestone 1

Backend API for the Whiteball packaging reporting platform. This implementation covers database integration, product catalog management, packaging items, and their associations.

## Features

- **Authentication**: JWT-based email/password login
- **Product Management**: Create, read, update, and list products with SKU, name, category, and pack quantities
- **Packaging Items**: Manage packaging components with material, weight, and type information
- **Product-Packaging Associations**: Link packaging items to products with quantity tracking
- **Company Isolation**: Multi-company support with data scoping to authenticated company
- **API Documentation**: OpenAPI/Swagger documentation at `/docs`

## Tech Stack

- **Python 3.12+**
- **FastAPI**: Modern async web framework
- **PostgreSQL**: Primary database
- **SQLAlchemy 2.x**: ORM layer
- **Pydantic v2**: Data validation and schemas
- **JWT Authentication**: Secure token-based auth
- **Docker Compose**: Local development environment
- **Pytest**: Testing framework

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Or: Python 3.12+, PostgreSQL, and uv

### Using Docker Compose (Recommended)

1. **Start the services**:
   ```bash
   docker-compose up -d
   ```

2. **Wait for PostgreSQL to be healthy** (about 10 seconds)

3. **Seed test data**:
   ```bash
   docker-compose exec api python -m app.scripts.seed_test_company
   ```

4. **Access the API**:
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Local Development (without Docker)

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   uv pip install -e ".[dev]"
   ```

3. **Set up environment**:
   ```bash
   cp .env.example .env
   ```

4. **Start PostgreSQL** (ensure it's running, adjust DATABASE_URL if needed):
   ```bash
   # On macOS with homebrew:
   brew services start postgresql
   ```

5. **Seed test data**:
   ```bash
   python -m app.scripts.seed_test_company
   ```

6. **Run the server**:
   ```bash
   python -m app
   ```

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/whiteball
SECRET_KEY=your-secret-key-here
DEBUG=true
LOG_LEVEL=info
TEST_ADMIN_EMAIL=admin@test.local
TEST_ADMIN_PASSWORD=change-me
```

## API Usage

### Authentication

**Login**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.local","password":"change-me"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "admin@test.local",
    "company_id": "...",
    "role": "admin",
    "is_active": true
  }
}
```

**Get Current User**:
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### Products

**Create Product**:
```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "SKU-001",
    "name": "Product Name",
    "category": "Electronics",
    "case_pack_quantity": 12,
    "pallet_quantity": 720
  }'
```

**List Products**:
```bash
curl -X GET "http://localhost:8000/api/v1/products?limit=50&offset=0" \
  -H "Authorization: Bearer <access_token>"
```

**Search Products**:
```bash
curl -X GET "http://localhost:8000/api/v1/products?search=SKU-001" \
  -H "Authorization: Bearer <access_token>"
```

**Get Product Detail**:
```bash
curl -X GET http://localhost:8000/api/v1/products/<product_id> \
  -H "Authorization: Bearer <access_token>"
```

**Update Product**:
```bash
curl -X PATCH http://localhost:8000/api/v1/products/<product_id> \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Updated Name"}'
```

**Delete Product** (soft delete):
```bash
curl -X DELETE http://localhost:8000/api/v1/products/<product_id> \
  -H "Authorization: Bearer <access_token>"
```

### Packaging Items

**Create Packaging Item**:
```bash
curl -X POST http://localhost:8000/api/v1/packaging-items \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "primary",
    "subtype": "commercial",
    "material": "plastic",
    "name": "Plastic Bottle",
    "weight_grams": 25.5
  }'
```

**List Packaging Items**:
```bash
curl -X GET http://localhost:8000/api/v1/packaging-items \
  -H "Authorization: Bearer <access_token>"
```

### Product-Packaging Associations

**Associate Packaging with Product**:
```bash
curl -X POST http://localhost:8000/api/v1/products/<product_id>/packaging \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "packaging_item": {
      "type": "primary",
      "material": "plastic",
      "name": "Bottle",
      "weight_grams": 25.5
    },
    "quantity_per_product_unit": 1
  }'
```

**Update Association**:
```bash
curl -X PATCH http://localhost:8000/api/v1/products/<product_id>/packaging/<association_id> \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"quantity_per_product_unit": 2}'
```

**Remove Association**:
```bash
curl -X DELETE http://localhost:8000/api/v1/products/<product_id>/packaging/<association_id> \
  -H "Authorization: Bearer <access_token>"
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_login_success

# Run with verbose output
pytest -v
```

## Project Structure

```
app/
├── __init__.py
├── __main__.py          # Entry point
├── main.py              # FastAPI app factory
├── core/
│   ├── config.py        # Settings and configuration
│   ├── security.py      # JWT and password utilities
│   └── exceptions.py    # Custom exceptions
├── db/
│   ├── base.py          # SQLAlchemy base
│   └── session.py       # Database session
├── models/
│   ├── company.py
│   ├── user.py
│   ├── product.py
│   ├── packaging.py
│   └── product_packaging_association.py
├── schemas/
│   ├── common.py
│   ├── auth.py
│   ├── product.py
│   └── packaging.py
├── api/
│   ├── deps.py          # Dependency injection
│   ├── router.py        # API router
│   └── routes/
│       ├── auth.py
│       ├── products.py
│       └── packaging.py
└── scripts/
    └── seed_test_company.py

tests/
├── conftest.py          # Pytest fixtures
├── test_auth.py
├── test_products.py
└── test_packaging.py
```

## Database Schema

### Companies
- `id` (UUID): Primary key
- `name` (String): Company name
- `country`, `city`, `postal_code`: Address fields
- `vat_number`, `registration_number`: Business identifiers
- `role` (String): admin or customer
- `is_active` (Boolean): Active status
- `created_at`, `updated_at`: Timestamps

### Users
- `id` (UUID): Primary key
- `company_id` (FK): Company reference
- `email` (String): Unique email
- `password_hash` (String): Hashed password
- `full_name` (String): User name
- `role` (String): admin or user
- `is_active` (Boolean): Active status

### Products
- `id` (UUID): Primary key
- `company_id` (FK): Company reference
- `sku` (String): Product SKU (unique per company)
- `name` (String): Product name
- `category` (String): Product category
- `case_pack_quantity` (Integer): Items per case
- `pallet_quantity` (Integer): Items per pallet
- `is_active` (Boolean): Active status

### Packaging Items
- `id` (UUID): Primary key
- `company_id` (FK): Company reference
- `type` (String): primary, secondary, or tertiary
- `subtype` (String): commercial, municipal, unknown
- `material` (String): plastic, pet, glass, etc.
- `name` (String): Item name
- `weight_grams` (Decimal): Weight in grams

### Product Packaging Associations
- `id` (UUID): Primary key
- `product_id` (FK): Product reference
- `packaging_item_id` (FK): Packaging item reference
- `quantity_per_product_unit` (Decimal): Quantity per unit
- `applies_to_unit` (String): unit, case, or pallet

## Error Responses

All errors follow this format:

```json
{
  "detail": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

### Error Codes

- `AUTH_INVALID_CREDENTIALS`: Invalid email or password
- `AUTH_INACTIVE_USER`: User account is inactive
- `PRODUCT_NOT_FOUND`: Product not found
- `PRODUCT_DUPLICATE`: Duplicate product SKU
- `PACKAGING_ITEM_NOT_FOUND`: Packaging item not found
- `VALIDATION_ERROR`: Input validation failed
- `UNAUTHORIZED`: User not authorized

## Development Workflow

1. **Make changes** to code
2. **Run tests** to verify: `pytest`
3. **Format code**: `black app tests`
4. **Lint code**: `ruff check app tests`
5. **Type check**: `mypy app`
6. **Commit and push**

## Next Steps (Future Milestones)

- Alembic migrations for database versioning
- CI/CD pipeline with GitHub Actions
- Multi-company admin panel
- Whiteball reference data import workflow
- Monthly import processing
- Matching algorithms and reporting
- Dashboard calculations
- OTR report generation

## Support

For issues or questions, please open an issue on the repository.
