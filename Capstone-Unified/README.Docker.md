# CRISP Unified - Docker Setup Guide

This guide explains how to set up and run the CRISP Unified application using Docker.

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose V2
- Git

### 1. Build and Run (Production Mode)

```bash
# Clone and navigate to the repository
cd Capstone-Unified

# Build and start all services
docker-compose up --build -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f web
```

The application will be available at:
- Main application: http://localhost:8000
- Nginx proxy: http://localhost:80
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### 2. Development Mode

For development with hot reloading:

```bash
# Start only database and Redis
docker-compose up db redis -d

# Install Python dependencies locally
pip install -r requirements.txt

# Run Django development server
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 3. Testing Mode

```bash
# Run all tests in Docker
docker-compose -f docker-compose.test.yml up --build test-runner

# Run specific tests
docker-compose -f docker-compose.test.yml run --rm test-runner python manage.py test core.tests.test_integration

# Generate coverage reports
docker-compose -f docker-compose.test.yml run --rm test-runner coverage run --source='.' manage.py test
docker-compose -f docker-compose.test.yml run --rm test-runner coverage html
```

## Services Overview

### Core Services
- **web**: Django application server (port 8000)
- **db**: PostgreSQL database (port 5432)
- **redis**: Redis cache/broker (port 6379)
- **celery-worker**: Background task processor
- **celery-beat**: Task scheduler
- **nginx**: Reverse proxy and static file server (ports 80/443)

### Development Services
- **web-test**: Test instance (port 8001)
- **db-test**: Test database (port 5433)
- **redis-test**: Test Redis (port 6380)
- **test-runner**: Automated test execution

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Security
SECRET_KEY=your-very-secret-key-change-this-in-production
DEBUG=False

# Database
DB_NAME=crisp
DB_USER=crisp_user
DB_PASSWORD=crisp_password
DB_HOST=db
DB_PORT=5432

# Redis
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Application
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
```

### Production Configuration

For production deployment:

1. **Security**: Change all default passwords and secrets
2. **SSL**: Configure SSL certificates in nginx/ssl/
3. **Environment**: Set `DEBUG=False`
4. **Backup**: Set up database backup strategy
5. **Monitoring**: Configure logging and monitoring

## Commands

### Application Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart a service
docker-compose restart web

# View service logs
docker-compose logs -f web

# Execute commands in running containers
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic

# Access container shell
docker-compose exec web bash
docker-compose exec db psql -U crisp_user -d crisp
```

### Database Operations

```bash
# Create database migration
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load test data
docker-compose exec web python manage.py loaddata fixtures/test_data.json

# Database backup
docker-compose exec db pg_dump -U crisp_user crisp > backup.sql

# Database restore
docker-compose exec -T db psql -U crisp_user crisp < backup.sql
```

### Testing Commands

```bash
# Run all tests
docker-compose -f docker-compose.test.yml up --build test-runner

# Run specific test module
docker-compose exec web python manage.py test core.tests.test_integration

# Run tests with coverage
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
docker-compose exec web coverage html

# Performance testing (requires services to be running)
docker-compose exec web locust -f performance_tests/locustfile.py --host=http://web:8000
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Change port mappings in docker-compose.yml
2. **Permission errors**: Ensure Docker has access to project directory
3. **Build failures**: Clear Docker cache with `docker system prune`
4. **Database connection errors**: Check database health with `docker-compose ps`

### Debug Commands

```bash
# Check service health
docker-compose ps

# View all logs
docker-compose logs

# Check resource usage
docker stats

# Inspect container configuration
docker-compose config

# Remove all data (DESTRUCTIVE)
docker-compose down -v
docker system prune -a
```

### Performance Optimization

1. **Resources**: Adjust worker count in docker-compose.yml
2. **Caching**: Configure Redis caching appropriately
3. **Database**: Tune PostgreSQL settings for your workload
4. **Static files**: Use CDN for static files in production

## CI/CD Integration

The project includes GitHub Actions workflows:

- **ci.yml**: Continuous integration testing
- **docker-publish.yml**: Docker image publishing
- **performance-tests.yml**: Performance testing

### GitHub Actions Setup

1. Enable GitHub Actions in your repository
2. Configure secrets for production deployment
3. Adjust workflow triggers as needed

## Security Considerations

1. **Secrets**: Never commit secrets to version control
2. **Network**: Use internal networks for service communication
3. **Images**: Keep base images updated
4. **Access**: Limit container capabilities and user permissions
5. **Monitoring**: Enable security logging and monitoring

## Monitoring and Logging

### Log Locations

- Application logs: `./logs/crisp_unified.log`
- Audit logs: `./logs/audit.log`
- Security logs: `./logs/security.log`
- Container logs: `docker-compose logs`

### Health Checks

```bash
# Application health
curl http://localhost:8000/admin/

# Database health
docker-compose exec db pg_isready -U crisp_user -d crisp

# Redis health
docker-compose exec redis redis-cli ping
```

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify configuration: `docker-compose config`
3. Check service status: `docker-compose ps`
4. Review this documentation
5. Check GitHub Issues

## License

This project is licensed under the terms specified in the main repository.