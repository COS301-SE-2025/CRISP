# Multi-stage build: React frontend + Django backend
FROM node:18-slim AS frontend-builder

WORKDIR /app/frontend

# Copy React package files
COPY crisp-react/package*.json ./
RUN rm -rf node_modules package-lock.json && npm install

# Copy React source and build
COPY crisp-react/ ./
RUN npm run build

# Django backend stage
FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=crisp_unified.settings

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create django user
RUN addgroup --system --gid 1001 django && \
    adduser --system --uid 1001 --ingroup django django

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy Django application
COPY . .

# Copy built React frontend to Django static files
COPY --from=frontend-builder /app/frontend/dist /app/static/react

# Create necessary directories and set permissions
RUN mkdir -p /app/logs /app/media /app/staticfiles && \
    touch /app/crisp_unified.log && \
    chown -R django:django /app

# Collect static files (including React build)
RUN python manage.py collectstatic --noinput

USER django

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "crisp_unified.wsgi:application"]