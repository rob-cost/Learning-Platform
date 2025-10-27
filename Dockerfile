# -----------------------------
# Stage 1: Build stage
# -----------------------------
FROM python:3.11-slim AS build

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Upgrade pip and install dependencies
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir \
    celery>=5.5.3 \
    django>=5.2.6 \
    python-dotenv>=0.9.9 \
    groq>=0.31.1 \
    markdown>=3.9 \
    markdown2>=2.5.4 \
    psycopg2-binary>=2.9.11 \
    redis>=6.4.0 \
    whitenoise>=6.11.0 \
    uvicorn>=0.23.0 \
    gunicorn>=21.2.0

# -----------------------------
# Stage 2: Production stage
# -----------------------------
FROM python:3.11-slim AS prod

WORKDIR /app

# Copy installed packages from build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy project files
COPY . .

# Set working directory to src (where manage.py lives)
WORKDIR /app/src

# Expose port for Cloud Run
EXPOSE 8080

# Environment variables (override in Cloud Run)
ENV DJANGO_SETTINGS_MODULE=learningPlatform.settings \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Collect static files
RUN python manage.py collectstatic --noinput


# CMD for Django HTTP service:
CMD ["gunicorn", "learningPlatform.asgi:application", "-w", "3", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]

