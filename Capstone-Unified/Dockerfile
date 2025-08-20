# Frontend development stage
FROM node:18-slim AS frontend-dev
WORKDIR /app
COPY crisp-react/package*.json ./
RUN npm install
COPY crisp-react/ ./
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Frontend production build stage
FROM node:18-slim AS frontend-builder
WORKDIR /app/frontend
COPY crisp-react/package*.json ./
RUN rm -rf node_modules package-lock.json && npm install
COPY crisp-react/ ./
RUN npm run build

# Django backend stage
FROM python:3.11 AS backend
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

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy Django application
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/media /app/staticfiles && \
    touch /app/crisp_unified.log

EXPOSE 8000

# Production backend with static files
FROM backend AS production
COPY --from=frontend-builder /app/frontend/dist /app/static/react
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "crisp_unified.wsgi:application"]