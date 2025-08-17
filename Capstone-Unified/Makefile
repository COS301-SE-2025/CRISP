# CRISP Unified Docker Management
# Usage: make [target]

.PHONY: help build up down restart logs shell test clean dev prod

# Default target
help:
	@echo "CRISP Unified Docker Management"
	@echo ""
	@echo "Available targets:"
	@echo "  build      - Build Docker images"
	@echo "  up         - Start all services"
	@echo "  down       - Stop all services"
	@echo "  restart    - Restart all services"
	@echo "  logs       - Show logs"
	@echo "  shell      - Access web container shell"
	@echo "  test       - Run test suite"
	@echo "  test-unit  - Run unit tests only"
	@echo "  test-integration - Run integration tests"
	@echo "  coverage   - Generate coverage report"
	@echo "  clean      - Remove containers and volumes"
	@echo "  dev        - Start development environment"
	@echo "  prod       - Start production environment"
	@echo "  migrate    - Run database migrations"
	@echo "  superuser  - Create Django superuser"
	@echo "  collectstatic - Collect static files"
	@echo "  backup-db  - Backup database"
	@echo "  restore-db - Restore database from backup"
	@echo ""

# Build images
build:
	docker-compose build

# Start services
up:
	docker-compose up -d

# Stop services
down:
	docker-compose down

# Restart services
restart:
	docker-compose restart

# Show logs
logs:
	docker-compose logs -f

# Access web container shell
shell:
	docker-compose exec web bash

# Database shell
db-shell:
	docker-compose exec db psql -U crisp_user -d crisp

# Redis shell
redis-shell:
	docker-compose exec redis redis-cli

# Run all tests
test:
	docker-compose -f docker-compose.test.yml up --build test-runner

# Run unit tests only
test-unit:
	docker-compose exec web python manage.py test --exclude-tag=integration

# Run integration tests
test-integration:
	docker-compose exec web python manage.py test --tag=integration

# Generate coverage report
coverage:
	docker-compose exec web coverage run --source='.' manage.py test
	docker-compose exec web coverage report
	docker-compose exec web coverage html

# Performance tests
performance:
	docker-compose exec web locust -f performance_tests/locustfile.py --host=http://localhost:8000

# Clean up containers and volumes
clean:
	docker-compose down -v
	docker system prune -f

# Development environment (DB + Redis only)
dev:
	docker-compose up -d db redis

# Production environment
prod:
	docker-compose -f docker-compose.yml up -d --build

# Database operations
migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

superuser:
	docker-compose exec web python manage.py createsuperuser

# Static files
collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

# Database backup
backup-db:
	docker-compose exec db pg_dump -U crisp_user crisp > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Database backed up to backup_$(shell date +%Y%m%d_%H%M%S).sql"

# Database restore (usage: make restore-db BACKUP=backup_file.sql)
restore-db:
	@if [ -z "$(BACKUP)" ]; then echo "Usage: make restore-db BACKUP=backup_file.sql"; exit 1; fi
	docker-compose exec -T db psql -U crisp_user crisp < $(BACKUP)

# Health checks
health:
	@echo "Checking service health..."
	@docker-compose ps
	@echo ""
	@echo "Application health:"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/admin/ || echo "Service not responding"
	@echo ""

# View service status
status:
	docker-compose ps

# Follow logs for specific service (usage: make logs-service SERVICE=web)
logs-service:
	@if [ -z "$(SERVICE)" ]; then echo "Usage: make logs-service SERVICE=service_name"; exit 1; fi
	docker-compose logs -f $(SERVICE)

# Rebuild and restart specific service (usage: make rebuild SERVICE=web)
rebuild:
	@if [ -z "$(SERVICE)" ]; then echo "Usage: make rebuild SERVICE=service_name"; exit 1; fi
	docker-compose build $(SERVICE)
	docker-compose up -d $(SERVICE)

# Setup environment for first time
setup:
	./setup.sh

# Quick deployment (build, migrate, collectstatic, start)
deploy:
	docker-compose build
	docker-compose run --rm web python manage.py migrate
	docker-compose run --rm web python manage.py collectstatic --noinput
	docker-compose up -d

# Security scan
security-scan:
	docker run --rm -v $(PWD):/app aquasec/trivy fs /app

# Lint code
lint:
	docker-compose exec web flake8 .
	docker-compose exec web black --check .
	docker-compose exec web isort --check-only .

# Format code
format:
	docker-compose exec web black .
	docker-compose exec web isort .

# Show Docker resource usage
resources:
	docker stats --no-stream

# Remove unused Docker resources
docker-clean:
	docker system prune -a -f
	docker volume prune -f

# Show application URLs
urls:
	@echo "Application URLs:"
	@echo "  Main app:     http://localhost:8000"
	@echo "  Admin:        http://localhost:8000/admin/"
	@echo "  API docs:     http://localhost:8000/api/docs/"
	@echo "  Nginx:        http://localhost:80"
	@echo ""
	@echo "Development URLs:"
	@echo "  Test app:     http://localhost:8001"
	@echo ""
	@echo "Database connections:"
	@echo "  PostgreSQL:   localhost:5432"
	@echo "  Redis:        localhost:6379"

# Emergency stop (force stop all containers)
emergency-stop:
	docker stop $(shell docker ps -q) 2>/dev/null || true

# Full reset (WARNING: destroys all data)
reset:
	@echo "WARNING: This will destroy all data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	docker-compose down -v
	docker system prune -a -f
	docker volume prune -f
	@echo "Full reset completed"