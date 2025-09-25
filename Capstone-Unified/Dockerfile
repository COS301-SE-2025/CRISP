# Frontend development stage
FROM node:18-slim AS frontend-dev
WORKDIR /app
COPY frontend/crisp-react/package*.json ./
RUN npm ci --only=production=false
COPY frontend/crisp-react/ ./
RUN npm list tailwindcss && ls -la node_modules/.bin/tailwind*
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Frontend production build stage
FROM node:18-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/crisp-react/package*.json ./
RUN npm ci --only=production=false
COPY frontend/crisp-react/ ./
RUN npm run build

# Django backend stage
FROM python:3.11 AS backend
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=settings.settings

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy Django application
COPY core/ ./core/
COPY settings/ ./settings/
COPY manage.py .

# Create necessary directories
RUN mkdir -p /app/logs /app/media /app/staticfiles

EXPOSE 8000

# Production backend with static files
FROM backend AS production
COPY --from=frontend-builder /app/frontend/dist /app/static/react
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "settings.wsgi:application"]