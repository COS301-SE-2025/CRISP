FROM python:3.11-slim

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install basic tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements and install Python dependencies
COPY crisp/requirements/ ./crisp/requirements/
RUN pip install --no-cache-dir --timeout 1000 -r crisp/requirements/base.txt
RUN pip install --no-cache-dir --timeout 1000 -r crisp/requirements/production.txt

# Copy the entire project
COPY . .

# Set environment variables for Django
ENV DJANGO_SETTINGS_MODULE=TrustManagement.settings
ENV PYTHONPATH=/app:/app/crisp:/app/core
ENV DEBUG=False
ENV DB_HOST=db
ENV DB_NAME=crisp_trust_db
ENV DB_USER=crisp_user
ENV DB_PASSWORD=crisp_password
ENV DB_PORT=5432

# Create necessary directories and set permissions
RUN mkdir -p crisp/logs crisp/staticfiles crisp/media && \
    chmod 755 crisp/logs crisp/staticfiles crisp/media

# Create a non-root user
RUN useradd --create-home --shell /bin/bash crisp && \
    chown -R crisp:crisp /app

# Switch to non-root user
USER crisp

# Expose the port Django runs on
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD cd crisp && python manage.py check --database default || exit 1

# Default command
CMD ["bash", "-c", "cd crisp && python manage.py collectstatic --noinput && python manage.py migrate && python TrustManagement/prepare_test_environment.py && python manage.py runserver 0.0.0.0:8000 --noreload"]