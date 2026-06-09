# mock-server/Dockerfile
FROM python:3.12 AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# --- Development ---
FROM base AS development
COPY . .
RUN pip install --no-cache-dir -e .

# --- Production ---
FROM base AS production
COPY pyproject.toml ./
COPY app/ ./app/
RUN pip install --no-cache-dir .
RUN adduser --disabled-password --no-create-home appuser
USER appuser
EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
