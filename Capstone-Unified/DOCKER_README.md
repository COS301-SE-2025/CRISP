# CRISP Docker Setup

This document explains how to run the CRISP application with different configurations for development and testing.

## Standard Development Setup

The default setup includes basic test data for development:

```bash
# Start the development environment
docker-compose up -d

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# Database: localhost:5432
```

This setup automatically:
- Runs database migrations
- Creates base users (admin, publisher, viewer)
- Populates the database with sample data using `populate_database` command
- Starts the Django backend and React frontend

### Default Login Credentials
- **Admin**: `admin` / `AdminPass123!`
- **Publisher**: `publisher` / `PublisherPass123!`
- **Viewer**: `viewer` / `ViewerPass123!`
- **Demo**: `demo` / `AdminPass123!`
- **Test**: `test` / `AdminPass123!`

## Testing Environment with Large Dataset

For testing with a larger dataset, use the test profile:

```bash
# Start the testing environment
docker-compose --profile test up -d

# Access the testing environment
# Frontend: http://localhost:5174
# Backend API: http://localhost:8001
# Database: localhost:5433
```

The test environment runs on separate ports and includes:
- All standard features
- Larger sample dataset (50+ organizations, hundreds of trust relationships)
- Separate database and Redis instances
- Same user credentials as development

## Available Services

### Development Environment
- **frontend**: React/Vite frontend (port 5173)
- **backend**: Django backend (port 8000)
- **db**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)

### Testing Environment
- **frontend-test**: React/Vite frontend (port 5174)
- **backend-test**: Django backend (port 8001)
- **db-test**: PostgreSQL database (port 5433)
- **redis-test**: Redis cache (port 6380)

## Useful Commands

### Start specific services
```bash
# Start only the database and backend
docker-compose up -d db redis backend

# Start the test environment
docker-compose --profile test up -d
```

### Database management
```bash
# Reset and repopulate database
docker-compose exec backend python manage.py flush --noinput
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py setup_base_users
docker-compose exec backend python manage.py populate_database --no-input

# Access database directly
docker-compose exec db psql -U crisp_user -d crisp
```

### View logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop services
```bash
# Stop development environment
docker-compose down

# Stop test environment
docker-compose --profile test down

# Stop and remove volumes (data will be lost)
docker-compose down -v
```

## Population Script Details

The `populate_database` management command creates:
- 50 sample organizations of various types
- 10-30 users per organization
- 200+ trust relationships
- 20 trust groups
- 1000+ user sessions
- 100+ threat feeds
- 5000+ audit logs

The script uses parallel processing for faster execution and includes realistic data such as:
- Company names and types
- Trust relationship networks
- User roles and permissions
- Activity timelines
- Organization metadata

## Troubleshooting

### Database connection issues
If you get database connection errors:
```bash
# Check database health
docker-compose exec db pg_isready -U crisp_user -d crisp

# Restart services in order
docker-compose restart db
docker-compose restart redis
docker-compose restart backend
```

### Port conflicts
If ports are already in use, you can modify the ports in `docker-compose.yml` or stop conflicting services.

### Population script fails
The population script is designed to be idempotent and will skip existing data. If it fails:
```bash
# Manual execution
docker-compose exec backend python manage.py populate_database --no-input
```