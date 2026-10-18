# ==============================================================================
# Dockerfile: AI-Thermal-detect Container
# Multi-stage lightweight Python container with CPU inference fallback
# ==============================================================================

FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system utilities and native dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy source code and default model weights
COPY . .

# Set default environment variables
ENV API_PORT=8080 \
    APP_MODULE="timeseries_service.thermal_receiver:app" \
    MODEL_DIR="/app/timeseries_service/model" \
    DATA_DIR="/app/timeseries_service/data" \
    HORIZON=5 \
    PREDICTION_CALLBACK_URL="http://master-station:8100/api/prediction"

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -fsS http://localhost:${API_PORT}/health || exit 1

# Launch FastAPI via uvicorn
CMD ["sh", "-c", "uvicorn timeseries_service.thermal_receiver:app --host 0.0.0.0 --port ${API_PORT}"]
