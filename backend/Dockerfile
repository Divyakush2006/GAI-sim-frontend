# GovernAI Studio Backend
# Multi-stage Docker build for Render Free Tier deployment
# Optimized for minimal image size and fast cold starts

FROM python:3.12-slim AS base

# Security: run as non-root
RUN groupadd -r governai && useradd -r -g governai governai

WORKDIR /app

# Install system dependencies for PyMuPDF and numpy
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# === Dependencies layer (cached unless requirements.txt changes) ===
FROM base AS dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# === Application layer ===
FROM dependencies AS app

# Copy application code
COPY app/ ./app/
COPY corpus/ ./corpus/ 2>/dev/null || true
COPY graph_data/ ./graph_data/ 2>/dev/null || true
COPY scripts/ ./scripts/ 2>/dev/null || true

# Create data directories
RUN mkdir -p graph_data corpus/raw corpus/processed && \
    chown -R governai:governai /app

# Switch to non-root user
USER governai

# Expose port
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:10000/health')" || exit 1

# Start with uvicorn
# Workers=1 for Render free tier (512MB RAM)
# Timeout=120 for LLM response time
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000", \
     "--workers", "1", "--timeout-keep-alive", "120", "--log-level", "info"]
