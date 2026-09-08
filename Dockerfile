# ============================================================
# Airfare Intelligence Platform (FareCast) — Production Dockerfile
# Multi-stage build: Node.js frontend build + Python backend
# Optimized for Render Cloud Web Service Deployment
# ============================================================

# ── Stage 1: Build the React frontend ──────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /frontend

# Copy package files and install deps
COPY frontend/package*.json ./
RUN npm ci --silent

# Copy source and build
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python production runtime ─────────────────────
FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=10000 \
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

# Copy the freshly built frontend from Stage 1
COPY --from=frontend-builder /frontend/dist/ ./frontend/dist/

# Copy baseline verified database (179k observations with full provenance)
COPY airfare.db ./airfare.db

# Ensure runtime directories exist with appropriate permissions
RUN mkdir -p data/raw data/processed data/processed/eda logs

# Expose Render standard port
EXPOSE 10000

# Healthcheck for container status with start period for clean initialisation
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=60s \
    CMD curl -f http://localhost:${PORT:-10000}/health || exit 1

# Launch production server binding to the environment-assigned port (defaults to 10000)
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
