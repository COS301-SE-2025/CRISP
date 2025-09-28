# CRISP Production Deployment Guide

## 🚀 Quick Deploy

For immediate production deployment on your server (206.81.22.242):

```bash
# 1. Clone repository
git clone https://github.com/COS301-SE-2025/CRISP.git
cd CRISP/Capstone-Unified

# 2. Setup production configuration (creates .env.production and docker-compose files)
./setup-production-config.sh

# 3. Deploy to production
sudo ./deploy-production.sh
```

## 📋 Prerequisites

- Ubuntu/Debian server with Docker and Docker Compose installed
- Domain: `data-defenders.co.za` pointing to `206.81.22.242`
- Ports 80, 443, and 22 open in firewall
- Root or sudo access

## 🔧 Manual Deployment Steps

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

### 2. Application Deployment

```bash
# Clone repository
git clone https://github.com/COS301-SE-2025/CRISP.git
cd CRISP/Capstone-Unified

# Generate secure secret keys
python3 -c "
import secrets, string
alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
django_secret = ''.join(secrets.choice(alphabet) for i in range(50))
trust_secret = ''.join(secrets.choice(alphabet) for i in range(50))
print(f'DJANGO_SECRET_KEY={django_secret}')
print(f'TRUST_MANAGEMENT_SECRET_KEY={trust_secret}')
"

# Update .env.production with generated secrets
# Replace REPLACE_WITH_SECURE_* placeholders with actual secrets

# Deploy application
docker-compose -f docker-compose.production.yml up -d
```

### 3. SSL Configuration

```bash
# Wait for services to start
sleep 30

# Setup SSL certificates
docker-compose -f docker-compose.production.yml exec certbot certbot certonly \
  --webroot --webroot-path=/var/www/certbot \
  --email your-email@example.com --agree-tos --no-eff-email \
  -d data-defenders.co.za -d www.data-defenders.co.za

# Update nginx to use SSL configuration
docker cp nginx-ssl.conf $(docker-compose -f docker-compose.production.yml ps -q nginx):/etc/nginx/conf.d/default.conf
docker-compose -f docker-compose.production.yml exec nginx nginx -s reload
```

## 🔒 Security Configuration

### Environment Variables

Critical production environment variables in `.env.production`:

```bash
# Security
DEBUG=false
DJANGO_SECRET_KEY=your-secure-50-character-secret-key
TRUST_MANAGEMENT_SECRET_KEY=your-secure-trust-secret-key

# Domain Configuration
ALLOWED_HOSTS=data-defenders.co.za,www.data-defenders.co.za,206.81.22.242,localhost,127.0.0.1

# CORS for production
CORS_ALLOWED_ORIGINS=https://data-defenders.co.za,https://www.data-defenders.co.za,http://data-defenders.co.za

# SSL Configuration
ENABLE_SSL_REDIRECT=true
```

### Database Security

```bash
# Change default passwords in production
DB_PASSWORD=your-secure-database-password

# For enhanced security, use external managed database:
DATABASE_URL=postgresql://user:password@external-db-host:5432/dbname
```

### Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw deny 5432/tcp  # Block external PostgreSQL access
sudo ufw deny 6379/tcp  # Block external Redis access
```

## 📊 Monitoring and Maintenance

### Health Checks

```bash
# Check application health
curl http://data-defenders.co.za/health/

# Monitor services
docker-compose -f docker-compose.production.yml ps
docker-compose -f docker-compose.production.yml logs -f app
```

### Log Management

```bash
# View application logs
docker-compose -f docker-compose.production.yml logs app

# View nginx logs
docker-compose -f docker-compose.production.yml logs nginx

# System logs location
docker volume inspect capstone-unified_app_logs
```

### Backup Strategy

```bash
# Database backup
docker-compose -f docker-compose.production.yml exec db pg_dump -U postgres crisp > backup_$(date +%Y%m%d).sql

# Media files backup
docker cp $(docker-compose -f docker-compose.production.yml ps -q app):/app/media ./media_backup_$(date +%Y%m%d)
```

## 🔄 CI/CD Integration

The application automatically builds and pushes to Docker Hub when code is pushed to the `Dev` branch:

1. **GitHub Actions** builds the Docker image
2. **Image pushed** to `datadefenders/crisp:Dev`
3. **Production deployment** pulls latest image:

```bash
# Update to latest version
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d
```

## 🐛 Troubleshooting

### Common Issues

1. **SSL Certificate Issues**
   ```bash
   # Check certificate status
   docker-compose -f docker-compose.production.yml exec certbot certbot certificates

   # Renew certificates
   docker-compose -f docker-compose.production.yml exec certbot certbot renew
   ```

2. **Database Connection Issues**
   ```bash
   # Check database health
   docker-compose -f docker-compose.production.yml exec db pg_isready -U postgres

   # Reset database
   docker-compose -f docker-compose.production.yml exec app python manage.py migrate
   ```

3. **Permission Issues**
   ```bash
   # Fix volume permissions
   sudo chown -R 1000:1000 logs/ media/
   ```

### Service Management

```bash
# Restart all services
docker-compose -f docker-compose.production.yml restart

# Restart specific service
docker-compose -f docker-compose.production.yml restart app

# View service status
docker-compose -f docker-compose.production.yml ps

# Scale workers
docker-compose -f docker-compose.production.yml up -d --scale celery=3
```

## 🌐 Access Points

After successful deployment:

- **Main Application**: http://data-defenders.co.za (or https:// if SSL configured)
- **Admin Interface**: http://data-defenders.co.za/admin/
- **API Documentation**: http://data-defenders.co.za/api/
- **Health Check**: http://data-defenders.co.za/health/

## 📞 Support

For deployment issues:
- Check application logs: `docker-compose -f docker-compose.production.yml logs app`
- Review health status: `curl http://data-defenders.co.za/health/`
- Monitor system resources: `docker stats`

## 🔐 Production Checklist

- [ ] ✅ Secure secret keys generated and configured
- [ ] ✅ DEBUG=false in production
- [ ] ✅ Database passwords changed from defaults
- [ ] ✅ ALLOWED_HOSTS configured for domain
- [ ] ✅ CORS configured for production URLs
- [ ] ✅ SSL certificates configured (optional but recommended)
- [ ] ✅ Firewall configured to allow only necessary ports
- [ ] ✅ Health checks working
- [ ] ✅ Monitoring and logging configured
- [ ] ✅ Backup strategy implemented