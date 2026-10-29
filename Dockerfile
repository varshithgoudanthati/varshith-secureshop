# Multi-stage / lightweight Python base for SecureShop
FROM python:3.11-slim

WORKDIR /app

# Set non-interactive environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SECURESHOP_MODE=secure \
    PORT=5000

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application codebase
COPY . .

# Seed initial database
RUN python secureshop/seed.py

# Expose service port
EXPOSE 5000

# Default command starts in secure mode
CMD ["python", "run.py", "--mode", "secure", "--port", "5000"]
