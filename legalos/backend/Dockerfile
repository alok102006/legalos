FROM python:3.10-slim

WORKDIR /app

# Install basic Linux dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy dependency configs
COPY pyproject.toml /app/

# Configure poetry to install packages system-wide inside the container
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copy application source
COPY . /app

# Expose FastAPI server port
EXPOSE 8000

# Execute server with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
