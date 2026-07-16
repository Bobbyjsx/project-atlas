FROM python:3.11-slim

WORKDIR /app

# Install base platform dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy platform source
COPY . .

# Cloud Run execution command
CMD uvicorn gateway.main:app --host 0.0.0.0 --port ${PORT:-8080}
