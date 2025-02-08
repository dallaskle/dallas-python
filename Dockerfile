FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ /app/

# Create logs directory
RUN mkdir -p /app/logs

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden in docker-compose.yml)
CMD ["python", "api_server.py"] 