#!/bin/bash

# CRISP Unified Docker Setup Script
# This script sets up the CRISP Unified application using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Docker installation
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p media
    mkdir -p staticfiles
    mkdir -p test_results
    mkdir -p coverage_reports
    mkdir -p scripts
    mkdir -p nginx/conf.d
    
    print_success "Directories created"
}

# Function to set up environment variables
setup_environment() {
    print_status "Setting up environment variables..."
    
    if [ ! -f .env ]; then
        print_status "Creating .env file..."
        cat > .env << EOL
# CRISP Unified Environment Configuration
# WARNING: Change these values in production!

# Security
SECRET_KEY=change-this-secret-key-in-production-$(date +%s)
DEBUG=False

# Database
DB_NAME=crisp
DB_USER=crisp_user
DB_PASSWORD=crisp_password_$(date +%s | tail -c 6)
DB_HOST=db
DB_PORT=5432

# Redis
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Application
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (configure for production)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# TAXII/OTX Configuration
OTX_API_KEY=your_otx_api_key_here
EOL
        print_success "Created .env file with default values"
        print_warning "Please review and update .env file with your specific configuration"
    else
        print_warning ".env file already exists, skipping creation"
    fi
}

# Function to validate Docker Compose configuration
validate_config() {
    print_status "Validating Docker Compose configuration..."
    
    if docker-compose config >/dev/null 2>&1; then
        print_success "Docker Compose configuration is valid"
    else
        print_error "Docker Compose configuration is invalid"
        docker-compose config
        exit 1
    fi
}

# Function to build and start services
start_services() {
    print_status "Building and starting services..."
    
    # Build images
    print_status "Building Docker images..."
    docker-compose build
    
    # Start services
    print_status "Starting services..."
    docker-compose up -d db redis
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    while ! docker-compose exec db pg_isready -U crisp_user -d crisp >/dev/null 2>&1; do
        sleep 2
        echo -n "."
    done
    echo
    
    # Run migrations
    print_status "Running database migrations..."
    docker-compose run --rm web python manage.py migrate
    
    # Collect static files
    print_status "Collecting static files..."
    docker-compose run --rm web python manage.py collectstatic --noinput
    
    # Start all services
    print_status "Starting all services..."
    docker-compose up -d
    
    print_success "All services started successfully"
}

# Function to create superuser
create_superuser() {
    echo
    read -p "Do you want to create a Django superuser? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Creating Django superuser..."
        docker-compose exec web python manage.py createsuperuser
    fi
}

# Function to run tests
run_tests() {
    echo
    read -p "Do you want to run the test suite? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Running test suite..."
        docker-compose -f docker-compose.test.yml up --build test-runner
        print_success "Tests completed"
    fi
}

# Function to display status
show_status() {
    print_status "Checking service status..."
    docker-compose ps
    
    echo
    print_success "Setup completed successfully!"
    echo
    echo "Services are available at:"
    echo "  - Main application: http://localhost:8000"
    echo "  - Admin interface: http://localhost:8000/admin/"
    echo "  - Nginx proxy: http://localhost:80"
    echo "  - PostgreSQL: localhost:5432"
    echo "  - Redis: localhost:6379"
    echo
    echo "Useful commands:"
    echo "  - View logs: docker-compose logs -f web"
    echo "  - Stop services: docker-compose down"
    echo "  - Restart services: docker-compose restart"
    echo "  - Access shell: docker-compose exec web bash"
    echo
    echo "Documentation:"
    echo "  - Docker setup: README.Docker.md"
    echo "  - Main documentation: README.md"
}

# Function to cleanup on error
cleanup_on_error() {
    print_error "Setup failed. Cleaning up..."
    docker-compose down -v 2>/dev/null || true
    exit 1
}

# Main setup function
main() {
    echo "=================================================="
    echo "      CRISP Unified Docker Setup Script          "
    echo "=================================================="
    echo
    
    # Set up error handling
    trap cleanup_on_error ERR
    
    # Check prerequisites
    check_docker
    
    # Setup environment
    create_directories
    setup_environment
    validate_config
    
    # Start services
    start_services
    
    # Optional setup
    create_superuser
    run_tests
    
    # Show final status
    show_status
}

# Script options
case "${1:-}" in
    --help|-h)
        echo "CRISP Unified Docker Setup Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h      Show this help message"
        echo "  --test-only     Run tests only"
        echo "  --dev           Setup for development"
        echo "  --clean         Clean up all containers and volumes"
        echo ""
        exit 0
        ;;
    --test-only)
        print_status "Running tests only..."
        docker-compose -f docker-compose.test.yml up --build test-runner
        exit 0
        ;;
    --dev)
        print_status "Setting up development environment..."
        docker-compose up -d db redis
        print_success "Database and Redis started for development"
        print_status "Install dependencies locally: pip install -r requirements.txt"
        print_status "Run development server: python manage.py runserver"
        exit 0
        ;;
    --clean)
        print_warning "This will remove all containers, volumes, and data!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v
            docker system prune -f
            print_success "Cleanup completed"
        fi
        exit 0
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac