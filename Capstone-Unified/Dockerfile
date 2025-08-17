# Multi-stage Docker build for CRISP Unified Application
# Stage 1: Build React frontend
FROM node:18-slim as frontend-builder

WORKDIR /app/frontend

# Copy React package files
COPY crisp-react-ut/package*.json ./

# Install all dependencies (including dev dependencies needed for build)
RUN npm ci

# Copy React source code
COPY crisp-react-ut/ ./

# Build React application
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim as backend

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=crisp_settings.settings

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create non-root user
RUN addgroup --system --gid 1001 django \
    && adduser --system --uid 1001 --ingroup django django

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy Django application
COPY . .

# Copy built React frontend from frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist ./static/

# Create necessary directories
RUN mkdir -p /app/logs /app/media /app/staticfiles \
    && chown -R django:django /app

# Collect static files
RUN python manage.py collectstatic --noinput

# Change to non-root user
USER django

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/admin/ || exit 1

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "crisp_settings.wsgi:application"]