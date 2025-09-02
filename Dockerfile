# syntax=docker/dockerfile:1

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# App code
COPY app /app

# Default config can be overridden by mounting or env vars
ENV CONFIG_PATH=/app/config.yaml

# Metrics port (Prometheus) and optional app port if using a server
EXPOSE 9000

CMD ["python", "/app/main.py"]


