#!/bin/bash

# CRISP Auto-Deploy Script
# Pulls latest Docker image and deploys with production configuration

echo "=== CRISP Auto-Deploy Started ==="
echo "Timestamp: $(date)"
echo

# Configuration
COMPOSE_FILE="docker-compose.production.yml"
IMAGE="datadefenders/crisp:Dev"
BACKUP_DIR="/root/backups"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Function to backup database
backup_database() {
    echo "Creating database backup..."
    BACKUP_FILE="$BACKUP_DIR/crisp_backup_$(date +%Y%m%d_%H%M%S).sql"

    if docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump -U postgres crisp > "$BACKUP_FILE"; then
        echo "✅ Database backup created: $BACKUP_FILE"

        # Keep only last 5 backups
        ls -t "$BACKUP_DIR"/crisp_backup_*.sql | tail -n +6 | xargs -r rm
        echo "Old backups cleaned up"
    else
        echo "⚠️  Database backup failed, continuing anyway..."
    fi
}

# Function to check if services are healthy
check_health() {
    echo "Checking service health..."

    # Wait for services to start
    sleep 15

    # Check if containers are running
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        echo "✅ Services are running"

        # Test HTTP endpoint
        if curl -f -s http://localhost:80 > /dev/null; then
            echo "✅ Application is responding"
            return 0
        else
            echo "❌ Application not responding"
            return 1
        fi
    else
        echo "❌ Services failed to start"
        return 1
    fi
}

# Function to rollback on failure
rollback() {
    echo "🔄 Rolling back to previous version..."

    # Stop current containers
    docker-compose -f "$COMPOSE_FILE" down

    # Remove failed image
    docker rmi "$IMAGE" || true

    # Try to start with previous image (if available)
    docker-compose -f "$COMPOSE_FILE" up -d

    echo "Rollback completed - check logs for issues"
}

echo "1. Pulling latest Docker image..."
if docker pull "$IMAGE"; then
    echo "✅ Successfully pulled $IMAGE"
else
    echo "❌ Failed to pull image"
    exit 1
fi

echo
echo "2. Creating database backup..."
backup_database

echo
echo "3. Stopping existing services..."
docker-compose -f "$COMPOSE_FILE" down

echo
echo "4. Starting services with new image..."
if docker-compose -f "$COMPOSE_FILE" up -d; then
    echo "✅ Services started"
else
    echo "❌ Failed to start services"
    exit 1
fi

echo
echo "5. Checking service health..."
if check_health; then
    echo "✅ Deployment successful!"
    echo
    echo "🌐 CRISP is now available at:"
    echo "   - http://data-defenders.co.za"
    echo "   - http://www.data-defenders.co.za"
    echo "   - http://206.81.22.242"
    echo
    echo "📊 Service Status:"
    docker-compose -f "$COMPOSE_FILE" ps
else
    echo "❌ Deployment failed - initiating rollback"
    rollback
    exit 1
fi

echo
echo "=== CRISP Auto-Deploy Completed Successfully ==="
echo "Timestamp: $(date)"