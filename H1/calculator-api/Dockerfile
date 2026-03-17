# Stage 1: Builder — install dependencies
FROM python:3.12-slim AS builder

WORKDIR /build

COPY pyproject.toml .

RUN pip install --no-cache-dir --prefix=/install .

# Stage 2: Runtime — minimal image
FROM python:3.12-slim AS runtime

WORKDIR /home/appuser/app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app/ ./app/

# Create non-privileged user
RUN useradd --create-home --shell /bin/bash appuser

# Switch to non-privileged user
USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
