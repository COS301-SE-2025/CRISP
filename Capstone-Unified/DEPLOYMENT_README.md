# CRISP Production Deployment Guide

## Domain Configuration: data-defenders.co.za

### Overview
This guide explains how to deploy CRISP on your production server with the `data-defenders.co.za` domain.

### Files in this deployment:
- `docker-compose.production.yml` - Production Docker Compose configuration
- `auto-deploy.sh` - Automated deployment script

### Server Setup Instructions

1. **Copy deployment files to your server:**
   ```bash
   # On your server (206.81.22.242)
   cd /root
   wget https://raw.githubusercontent.com/YOUR_USERNAME/CRISP/Dev/Capstone-Unified/docker-compose.production.yml
   wget https://raw.githubusercontent.com/YOUR_USERNAME/CRISP/Dev/Capstone-Unified/auto-deploy.sh
   chmod +x auto-deploy.sh
   ```

2. **Replace your current docker-compose.yml:**
   ```bash
   # Backup current config
   cp docker-compose.yml docker-compose.yml.old

   # Use production config
   cp docker-compose.production.yml docker-compose.yml
   ```

3. **Deploy with the new configuration:**
   ```bash
   ./auto-deploy.sh
   ```

### Configuration Details

**Environment Variables Set:**
- `ALLOWED_HOSTS`: Includes `data-defenders.co.za` and `www.data-defenders.co.za`
- `REACT_APP_API_BASE_URL`: Points to `http://data-defenders.co.za`
- All other production settings maintained

**Domain Access:**
- Primary: http://data-defenders.co.za
- Alternative: http://www.data-defenders.co.za
- IP Access: http://206.81.22.242 (fallback)

### DNS Configuration Required
Ensure your DNS has these A records pointing to `206.81.22.242`:
- `data-defenders.co.za`
- `www.data-defenders.co.za`

### Auto-Deployment Features
The `auto-deploy.sh` script includes:
- ✅ Database backup before deployment
- ✅ Health checks after deployment
- ✅ Automatic rollback on failure
- ✅ Service status reporting

### Continuous Deployment
When you push to the `Dev` branch:
1. GitHub Actions builds the Docker image
2. Image is pushed to Docker Hub as `datadefenders/crisp:Dev`
3. Your server can pull and deploy automatically using the watcher script

### Manual Deployment
```bash
# Pull latest image and deploy
./auto-deploy.sh

# Check deployment status
docker-compose ps
docker-compose logs app

# View application logs
docker-compose logs -f app
```

### Troubleshooting

**If the domain doesn't work:**
1. Check DNS resolution: `nslookup data-defenders.co.za`
2. Verify it points to your server IP: `206.81.22.242`
3. Check Django ALLOWED_HOSTS in the logs
4. Ensure port 80 is accessible

**If containers fail to start:**
1. Check logs: `docker-compose logs`
2. Verify Docker Hub image exists: `docker pull datadefenders/crisp:Dev`
3. Check system resources: `docker system df`

**Access the application:**
- Once deployed, visit http://data-defenders.co.za
- Admin access via your configured superuser account
- Database accessible on port 5432 (internal to Docker network)

### Security Notes
- Database credentials are set in the compose file
- Consider using Docker secrets for production passwords
- HTTPS setup recommended for production (add reverse proxy like nginx)
- Regular database backups are created automatically