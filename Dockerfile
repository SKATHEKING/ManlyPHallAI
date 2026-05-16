# Multi-stage Dockerfile for ManlyPHallAI
# Optimized for development and production

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Build Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Set PATH to include user Python packages
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH
ENV PYTHONUNBUFFERED=1

# Copy application code
COPY backend/ backend/
COPY bot/ bot/
COPY scripts/ scripts/

# Create data directory
RUN mkdir -p data

# Pre-download embedding model
RUN python scripts/download_embeddings_model.py || echo "Model download optional"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden)
CMD ["python", "scripts/run_api.py"]

# Metadata
LABEL maintainer="ManlyPHallAI Project"
LABEL description="Hermetic Knowledge RAG System with Discord Integration"
LABEL version="1.0"
