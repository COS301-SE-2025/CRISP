#!/bin/bash

# CRISP Quick Deployment Script
# This script automates the deployment of CRISP from Docker Hub

set -e  # Exit on any error

echo "🚀 CRISP Deployment Script"
echo "=========================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root or with sudo
if [ "$EUID" -eq 0 ]; then 
    echo -e "${YELLOW}⚠️  Running as root. This is okay, but make sure you trust this script.${NC}"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker is installed"
echo -e "${GREEN}✓${NC} Docker Compose is installed"
echo ""

# Check if production-docker-compose.yml exists
if [ ! -f "production-docker-compose.yml" ]; then
    echo -e "${RED}❌ production-docker-compose.yml not found in current directory${NC}"
    echo "Please run this script from the Capstone-Unified directory"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found production-docker-compose.yml"
echo ""

# Ask user what they want to do
echo "What would you like to do?"
echo "1) Fresh deployment (pull image and start)"
echo "2) Update existing deployment (pull new image, restart)"
echo "3) Stop deployment"
echo "4) View logs"
echo "5) Setup AlienVault OTX feed"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}📦 Starting fresh deployment...${NC}"
        echo ""
        
        # Pull latest image
        echo "Pulling latest image from Docker Hub..."
        docker pull datadefenders/crisp:latest
        
        # Stop any existing containers
        echo "Stopping any existing containers..."
        docker-compose -f production-docker-compose.yml down 2>/dev/null || true
        
        # Start services
        echo "Starting services..."
        docker-compose -f production-docker-compose.yml up -d
        
        echo ""
        echo -e "${GREEN}✅ Deployment complete!${NC}"
        echo ""
        echo "Waiting 30 seconds for services to initialize..."
        sleep 30
        
        # Check service status
        echo ""
        echo "Service Status:"
        docker-compose -f production-docker-compose.yml ps
        
        echo ""
        echo -e "${GREEN}🎉 CRISP is now running!${NC}"
        echo ""
        echo "Access your system at: http://localhost/"
        echo "Default credentials:"
        echo "  Username: admin"
        echo "  Password: AdminPass123!"
        echo ""
        echo "To view logs: docker-compose -f production-docker-compose.yml logs -f"
        ;;
        
    2)
        echo ""
        echo -e "${YELLOW}🔄 Updating deployment...${NC}"
        echo ""
        
        # Pull latest image
        echo "Pulling latest image from Docker Hub..."
        docker pull datadefenders/crisp:latest
        
        # Restart services
        echo "Restarting services..."
        docker-compose -f production-docker-compose.yml down
        docker-compose -f production-docker-compose.yml up -d
        
        echo ""
        echo -e "${GREEN}✅ Update complete!${NC}"
        echo ""
        echo "Waiting 30 seconds for services to initialize..."
        sleep 30
        
        # Check service status
        echo ""
        echo "Service Status:"
        docker-compose -f production-docker-compose.yml ps
        ;;
        
    3)
        echo ""
        echo -e "${YELLOW}🛑 Stopping deployment...${NC}"
        docker-compose -f production-docker-compose.yml down
        echo ""
        echo -e "${GREEN}✅ Services stopped${NC}"
        echo ""
        echo "Note: Data is preserved in Docker volumes"
        echo "To start again, run this script and choose option 1"
        ;;
        
    4)
        echo ""
        echo -e "${YELLOW}📋 Viewing logs (Ctrl+C to exit)...${NC}"
        echo ""
        docker-compose -f production-docker-compose.yml logs -f
        ;;
        
    5)
        echo ""
        echo -e "${YELLOW}🌐 Setting up AlienVault OTX feed...${NC}"
        echo ""
        
        # Get container name
        CONTAINER_NAME=$(docker-compose -f production-docker-compose.yml ps -q app)
        
        if [ -z "$CONTAINER_NAME" ]; then
            echo -e "${RED}❌ App container is not running${NC}"
            echo "Please start the deployment first (option 1 or 2)"
            exit 1
        fi
        
        # Setup OTX feed
        echo "Creating AlienVault OTX feed..."
        docker exec $CONTAINER_NAME python /app/setup_otx_feed.py
        
        echo ""
        read -p "Do you want to consume indicators from OTX now? (y/n): " consume
        
        if [ "$consume" = "y" ] || [ "$consume" = "Y" ]; then
            echo ""
            echo "Consuming indicators from AlienVault OTX (this may take a few minutes)..."
            docker exec $CONTAINER_NAME python manage.py consume_threat_feeds --feed-name "AlienVault" --limit 100
            
            echo ""
            echo -e "${GREEN}✅ OTX feed setup complete!${NC}"
            
            # Show stats
            echo ""
            echo "Current statistics:"
            docker exec $CONTAINER_NAME python manage.py shell -c "
from core.models.models import ThreatFeed, Indicator
feeds = ThreatFeed.objects.filter(is_active=True).count()
indicators = Indicator.objects.count()
print(f'Active Feeds: {feeds}')
print(f'Total Indicators: {indicators}')
"
        fi
        ;;
        
    *)
        echo ""
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "Done!"
