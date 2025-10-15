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
# Copy package files first for better layer caching
COPY frontend/crisp-react/package*.json ./
RUN npm ci --only=production=false
# Copy all frontend source code
COPY frontend/crisp-react/ ./
# Add build argument to bust cache when needed
ARG BUILD_DATE
ARG VITE_API_BASE_URL=""
# Build the React application with the environment variable
RUN VITE_API_BASE_URL="${VITE_API_BASE_URL}" npm run build

# Django backend stage
FROM python:3.11 AS backend
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/media /app/staticfiles

# Production stage
FROM backend AS production

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist /app/staticfiles/react

# Collect all static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/api/health/', timeout=5)" || exit 1

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "settings.wsgi:application"]
