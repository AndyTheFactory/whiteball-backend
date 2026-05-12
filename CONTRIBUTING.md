# Contributing to Whiteball Backend

Thank you for your interest in contributing to the Whiteball Backend! This document outlines the development workflow and guidelines.

## Development Setup

### Prerequisites

- Python 3.12 or higher
- PostgreSQL 14 or higher (or use Docker)
- Git

### Option 1: Local Development (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AndyTheFactory/whiteball-backend.git
   cd whiteball-backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -e ".[dev]"
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```

5. **Ensure PostgreSQL is running** and database exists:
   ```bash
   createdb whiteball
   ```

6. **Seed test data**:
   ```bash
   python -m app.scripts.seed_test_company
   ```

7. **Run the development server**:
   ```bash
   python -m app
   ```

   API will be available at `http://localhost:8000`

### Option 2: Docker Development

```bash
docker-compose up -d
docker-compose exec api python -m app.scripts.seed_test_company
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `test/` - Tests
- `refactor/` - Code refactoring
- `chore/` - Maintenance tasks

### 2. Write Code

Follow the project structure and code style guidelines (see below).

### 3. Write Tests

For every feature or bug fix, write corresponding tests:

```bash
pytest tests/test_your_feature.py
```

Aim for >80% code coverage:

```bash
pytest --cov=app --cov-report=html
```

### 4. Lint and Format

Before committing, ensure your code is properly formatted:

```bash
# Format code
black app tests

# Check linting
ruff check app tests

# Type check
mypy app
```

Or use pre-commit hooks to automate:

```bash
pre-commit install
pre-commit run --all-files
```

### 5. Commit Changes

Write clear, descriptive commit messages:

```bash
git commit -m "feat(products): add product search endpoint

- Implement full-text search for products
- Add filter by category
- Add sorting by name/sku/date"
```

Commit message format:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear title describing the change
- Description of what was changed and why
- Reference to any related issues
- Screenshots for UI changes (if applicable)

## Code Style Guidelines

### Python

- **Line length**: 88 characters (Black default)
- **Imports**: Use absolute imports, organized by: stdlib, third-party, local
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Type hints**: Use type hints for function signatures (though not strictly enforced)
- **Docstrings**: Use triple quotes for module, class, and function docstrings

Example:

```python
"""Module for managing products."""
from typing import List
from uuid import UUID

def get_products(
    company_id: UUID,
    skip: int = 0,
    limit: int = 50,
) -> List[Product]:
    """
    Get products for a company.

    Args:
        company_id: Company identifier
        skip: Number of items to skip
        limit: Maximum items to return

    Returns:
        List of products
    """
    pass
```

### FastAPI Endpoints

- Use proper HTTP methods (GET, POST, PATCH, DELETE)
- Include response models for all endpoints
- Add status codes
- Include docstrings
- Use dependency injection for authentication

Example:

```python
@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProductResponse:
    """
    Create a new product for the authenticated company.

    - **sku**: Product SKU (required, unique per company)
    - **name**: Product name (required)
    - **category**: Optional category classification
    """
    pass
```

### Database Models

- Use UUIDs for primary keys
- Include `created_at` and `updated_at` timestamps
- Add foreign key constraints
- Add appropriate indexes
- Use proper data types (avoid storing booleans as strings, etc.)

### Tests

- Use descriptive test names: `test_<what>_<condition>_<expected>`
- Include docstrings explaining what's being tested
- Use fixtures from `conftest.py`
- Test both success and failure paths
- Use assertions with helpful messages

Example:

```python
def test_create_product_duplicate_sku_fails(
    client: TestClient,
    auth_headers: dict,
) -> None:
    """Test that creating a product with duplicate SKU fails."""
    # Setup
    client.post(
        "/api/v1/products",
        json={"sku": "DUP-001", "name": "Product 1"},
        headers=auth_headers,
    )

    # Execute
    response = client.post(
        "/api/v1/products",
        json={"sku": "DUP-001", "name": "Product 2"},
        headers=auth_headers,
    )

    # Assert
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "PRODUCT_DUPLICATE"
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_products.py
```

### Run Specific Test

```bash
pytest tests/test_products.py::test_create_product
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html to view coverage
```

### Run with Verbose Output

```bash
pytest -v
```

## Database Migrations

When you modify the SQLAlchemy models, create a migration:

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new column to products"

# Review the generated migration in alembic/versions/

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Common Development Tasks

### Start Fresh Database

```bash
# Drop and recreate database
dropdb whiteball
createdb whiteball

# Seed test data
python -m app.scripts.seed_test_company
```

### Reset Docker Environment

```bash
docker-compose down -v
docker-compose up -d
docker-compose exec api python -m app.scripts.seed_test_company
```

### View API Documentation

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Access PostgreSQL

```bash
# Local
psql whiteball

# Docker
docker-compose exec postgres psql -U postgres -d whiteball
```

## Pull Request Requirements

Before your PR will be merged:

1. ✅ All tests pass
2. ✅ Code is formatted with Black
3. ✅ No linting errors from Ruff
4. ✅ Type checking passes
5. ✅ PR has clear description
6. ✅ Changes are documented
7. ✅ All conversations are resolved

## Questions or Issues?

- Check existing issues
- Review the README
- Ask in a discussion
- Open a new issue if you find a bug

Thanks for contributing! 🎉
