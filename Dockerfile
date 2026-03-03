# ── Backend Dockerfile ───────────────────────────────────────
# Multi-stage build: install deps → download checkpoints → run
# ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS base

WORKDIR /app

# System deps for torch / build tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency manifests first (layer caching)
COPY pyproject.toml uv.lock* ./

# Install production dependencies only
RUN uv sync --no-dev

# Copy the rest of the application
COPY api/ api/
COPY model/ model/
COPY src/ src/
COPY scripts/ scripts/
COPY data/*.dvc data/
COPY checkpoints.dvc ./

# ── Runtime stage ────────────────────────────────────────────
FROM base AS runtime

# Download model checkpoints from DagsHub S3
# (credentials passed as build args so they don't persist in image)
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
RUN if [ -n "$AWS_ACCESS_KEY_ID" ]; then \
      AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
      AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
      uv run python scripts/download_checkpoints.py; \
    fi

EXPOSE 8000

# Environment variables (overridden at deploy time)
ENV ENVIRONMENT=production
ENV PORT=8000

CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
