#!/bin/bash
set -e

# Configuration
DOCKER_HUB_IMAGE="datadefenders/crisp:Dev"
COMPOSE_FILE="docker-compose.production.yml"

# 1. Login to Docker Hub (ensure you have run 'docker login' on the server before)
echo "Logging in to Docker Hub..."
# The official recommendation is to login via `docker login` command manually first.
# If you have credentials stored, this will use them.

# 2. Pull the latest image for the Dev branch
echo "Pulling the latest image: $DOCKER_HUB_IMAGE"
docker pull $DOCKER_HUB_IMAGE

# 3. Shut down the old services
echo "Shutting down running services..."
docker-compose -f $COMPOSE_FILE down

# 4. Start the new services in detached mode
echo "Starting services with the new image..."
docker-compose -f $COMPOSE_FILE up -d --build

# 5. Run database migrations
echo "Running database migrations..."
docker-compose -f $COMPOSE_FILE exec -T backend python manage.py migrate --noinput

# 6. Optional: Prune old images to save space
echo "Pruning old Docker images..."
docker image prune -f

echo "
Deployment Complete!
Your application should be running at http://data-defenders.co.za
"