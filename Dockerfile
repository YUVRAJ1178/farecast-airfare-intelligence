# ============================================================
# Airfare Intelligence Platform (FareCast) — Production Dockerfile
# Optimized for Render Cloud Web Service Deployment
# ============================================================

FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    APP_ENV=production \
    DEMO_MODE=false

# Install minimal OS dependencies for compilation and healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (leverage Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application directories and assets
COPY backend/ ./backend/
COPY data/ ./data/
COPY ml/ ./ml/
COPY models/ ./models/
COPY frontend/dist/ ./frontend/dist/

# Copy baseline verified database (179k observations with full provenance)
COPY airfare.db ./airfare.db

# Ensure runtime directories exist with appropriate permissions
RUN mkdir -p data/raw data/processed data/processed/eda logs

# Expose internal port
EXPOSE 8000

# Healthcheck for container status
HEALTHCHECK --interval=20s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Launch production server binding to the environment-assigned port
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
