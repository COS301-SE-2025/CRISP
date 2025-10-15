#!/bin/bash
set -e

# Configuration
DOCKER_REPO="datadefenders/crisp-production"
TAG="latest"
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')

echo "Building CRISP Production Image"
echo "================================"
echo "Repository: $DOCKER_REPO"
echo "Tag: $TAG"
echo "Build Date: $BUILD_DATE"

# Change to the correct directory
cd /mnt/c/Users/jadyn/CRISP/Capstone-Unified

# Build the production image
echo "Building Docker image..."
docker build \
  --target production \
  --build-arg BUILD_DATE="$BUILD_DATE" \
  -t "$DOCKER_REPO:$TAG" \
  -t "$DOCKER_REPO:$(date +'%Y%m%d')" \
  .

echo "Docker image built successfully!"

# Push to Docker Hub
echo "Pushing to Docker Hub..."
docker push "$DOCKER_REPO:$TAG"
docker push "$DOCKER_REPO:$(date +'%Y%m%d')"

echo "Push complete!"
echo "Image available at: $DOCKER_REPO:$TAG"