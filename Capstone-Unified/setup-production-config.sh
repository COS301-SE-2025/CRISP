#!/bin/bash

# CRISP Production Configuration Setup
# This script creates production configuration files from templates
# Safe to include in git repository

set -e

echo "[SETUP] CRISP Production Configuration Setup"
echo "============================================"

# Domain and server configuration
DOMAIN="data-defenders.co.za"
SERVER_IP="206.81.22.242"
EMAIL="cos332practical6@gmail.com"

echo "[CONFIG] Setting up for domain: $DOMAIN"
echo "[CONFIG] Server IP: $SERVER_IP"

# Function to generate random secret
generate_secret() {
    python3 -c "
import secrets
import string
alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
password = ''.join(secrets.choice(alphabet) for i in range(50))
print(password)
" 2>/dev/null || openssl rand -base64 32 | tr -d "=+/" | cut -c1-50
}

# Create .env.production from template
if [ ! -f .env.production ]; then
    echo "[CREATE] Creating .env.production from template..."
    cp .env.production.template .env.production

    # Generate secure secrets
    DJANGO_SECRET=$(generate_secret)
    TRUST_SECRET=$(generate_secret)
    DB_PASSWORD=$(generate_secret | head -c 20)

    # Replace placeholders
    sed -i "s/REPLACE_WITH_SECURE_RANDOM_SECRET_KEY_IN_PRODUCTION/$DJANGO_SECRET/" .env.production
    sed -i "s/REPLACE_WITH_SECURE_TRUST_SECRET_KEY_IN_PRODUCTION/$TRUST_SECRET/" .env.production
    sed -i "s/your-secure-production-database-password/$DB_PASSWORD/" .env.production
    sed -i "s/your-domain.com/$DOMAIN/g" .env.production
    sed -i "s/www.your-domain.com/www.$DOMAIN/g" .env.production
    sed -i "s/your-server-ip/$SERVER_IP/g" .env.production
    sed -i "s/your-production-email@domain.com/$EMAIL/g" .env.production
    sed -i "s/admin@your-domain.com/admin@$DOMAIN/g" .env.production
    sed -i "s/test@your-domain.com/test@$DOMAIN/g" .env.production

    echo "[OK] .env.production created with secure random secrets"
else
    echo "[SKIP] .env.production already exists"
fi

# Create docker-compose.production.yml from template
if [ ! -f docker-compose.production.yml ]; then
    echo "[CREATE] Creating docker-compose.production.yml from template..."
    cp docker-compose.production.template.yml docker-compose.production.yml

    # Get database password from .env.production
    DB_PASSWORD=$(grep "DB_PASSWORD=" .env.production | cut -d'=' -f2)

    # Replace placeholders
    sed -i "s/YOUR_DOMAIN.COM/$DOMAIN/g" docker-compose.production.yml
    sed -i "s/www.YOUR_DOMAIN.COM/www.$DOMAIN/g" docker-compose.production.yml
    sed -i "s/YOUR_SERVER_IP/$SERVER_IP/g" docker-compose.production.yml
    sed -i "s/YOUR_DB_PASSWORD/$DB_PASSWORD/g" docker-compose.production.yml

    echo "[OK] docker-compose.production.yml created"
else
    echo "[SKIP] docker-compose.production.yml already exists"
fi

# Create basic nginx.conf
cat > nginx.conf << EOF
upstream django {
    server app:8000;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN $SERVER_IP;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Hide nginx version
    server_tokens off;

    # Client max body size for file uploads
    client_max_body_size 100M;

    # Health check endpoint
    location /health/ {
        proxy_pass http://django;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        access_log off;
    }

    # Static files
    location /static/ {
        alias /app/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /app/media/;
        expires 1d;
        add_header Cache-Control "public";
    }

    # All other requests to Django
    location / {
        proxy_pass http://django;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Gzip compression
    gzip on;
    gzip_comp_level 6;
    gzip_types
        application/javascript
        application/json
        application/xml
        text/css
        text/javascript
        text/plain
        text/xml;
}
EOF

echo "[OK] nginx.conf created"

# Create deployment script
cat > deploy-production.sh << 'EOF'
#!/bin/bash

# CRISP Production Deployment Script
# Generated automatically - customize as needed

set -e

echo "[DEPLOY] CRISP Production Deployment Starting..."
echo "==========================================="

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "[ERROR] Please run this script as root or with sudo"
    exit 1
fi

# Check if configuration files exist
if [ ! -f .env.production ]; then
    echo "[ERROR] .env.production not found! Run setup-production-config.sh first"
    exit 1
fi

if [ ! -f docker-compose.production.yml ]; then
    echo "[ERROR] docker-compose.production.yml not found! Run setup-production-config.sh first"
    exit 1
fi

echo "[DOCKER] Pulling latest Docker image..."
docker pull datadefenders/crisp:Dev

echo "[DOCKER] Stopping existing containers..."
docker-compose -f docker-compose.production.yml down --remove-orphans || true

echo "[CLEANUP] Cleaning up old containers and images..."
docker system prune -f

echo "[DOCKER] Starting production services..."
docker-compose -f docker-compose.production.yml up -d

echo "[WAIT] Waiting for services to start..."
sleep 30

echo "[CHECK] Checking service health..."
docker-compose -f docker-compose.production.yml ps

# Wait for application to be healthy
echo "[WAIT] Waiting for application health check..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost/health/ >/dev/null 2>&1; then
        echo "[OK] Application is healthy!"
        break
    fi

    attempt=$((attempt + 1))
    echo "[WAIT] Attempt $attempt/$max_attempts - waiting for application..."
    sleep 10
done

if [ $attempt -eq $max_attempts ]; then
    echo "[ERROR] Application failed to become healthy!"
    echo "[LOGS] Container logs:"
    docker-compose -f docker-compose.production.yml logs app
    exit 1
fi

echo "[SUCCESS] CRISP Production Deployment Complete!"
echo "========================================="
echo ""
echo "[INFO] Your application is available at:"
echo "   • HTTP:  http://DOMAIN_PLACEHOLDER"
echo "   • IP:    http://IP_PLACEHOLDER"
echo ""
echo "[MONITOR] Monitor your deployment:"
echo "   • View logs: docker-compose -f docker-compose.production.yml logs -f"
echo "   • Check status: docker-compose -f docker-compose.production.yml ps"
echo "   • Restart services: docker-compose -f docker-compose.production.yml restart"
echo ""
echo "[COMPLETE] Deployment completed successfully!"
EOF

# Replace placeholders in deployment script
sed -i "s/DOMAIN_PLACEHOLDER/$DOMAIN/g" deploy-production.sh
sed -i "s/IP_PLACEHOLDER/$SERVER_IP/g" deploy-production.sh

chmod +x deploy-production.sh
echo "[OK] deploy-production.sh created and made executable"

echo ""
echo "[SUCCESS] Production configuration setup complete!"
echo "================================================="
echo ""
echo "[FILES] Created:"
echo "  ✓ .env.production (with secure secrets)"
echo "  ✓ docker-compose.production.yml"
echo "  ✓ nginx.conf"
echo "  ✓ deploy-production.sh"
echo ""
echo "[NEXT] To deploy to production:"
echo "  1. Copy these files to your server"
echo "  2. Run: sudo ./deploy-production.sh"
echo ""
echo "[SECURITY] Important notes:"
echo "  • .env.production contains secure secrets - keep it safe!"
echo "  • Change database passwords if needed"
echo "  • Configure email settings in .env.production"
echo "  • Set up SSL certificates after deployment"