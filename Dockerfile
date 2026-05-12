FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml .
COPY app/ ./app/
COPY tests/ ./tests/
COPY .env.example ./.env

# Install dependencies using uv
RUN uv pip install --system -e .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "app"]
