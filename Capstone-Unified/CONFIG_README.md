# Environment Configuration Templates

This directory contains example/template configuration files for the CRISP application. These files show the structure and required variables but **do not contain real secrets**.

## 📁 Template Files

### Development
- `.env.example` - Template for local development environment variables
- `frontend/crisp-react/.env.example` - Frontend development configuration

### Production  
- `.env.production.example` - Template for production environment variables
- `docker-compose.prod.example.yml` - Template for production Docker Compose
- `frontend/crisp-react/.env.production.example` - Frontend production configuration

## 🚀 Quick Start

### For Local Development

1. **Backend setup:**
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

2. **Frontend setup:**
   ```bash
   cd frontend/crisp-react
   cp .env.example .env
   # Edit if needed (default: http://localhost:8000)
   ```

### For Production Deployment

1. **Backend setup:**
   ```bash
   cp .env.production.example .env.production
   cp docker-compose.prod.example.yml docker-compose.prod.yml
   ```

2. **Generate secrets:**
   ```bash
   # Django SECRET_KEY
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   
   # Database password
   openssl rand -base64 32
   ```

3. **Edit production files:**
   ```bash
   nano .env.production
   # Update: DJANGO_SECRET_KEY, POSTGRES_PASSWORD, ALLOWED_HOSTS, etc.
   
   nano docker-compose.prod.yml
   # Verify environment variable references match .env.production
   ```

4. **Frontend setup:**
   ```bash
   cd frontend/crisp-react
   cp .env.production.example .env.production
   # Update VITE_API_BASE_URL with your domain
   ```

## ⚠️ IMPORTANT SECURITY NOTES

### Files You Should NEVER Commit to Git:
- `.env`
- `.env.production`
- `.env.local`
- `docker-compose.prod.yml` (when containing real credentials)
- `frontend/crisp-react/.env*` (except .example files)

These files are already in `.gitignore` to prevent accidental commits.

### What IS Safe to Commit:
- `.env.example`
- `.env.production.example`
- `docker-compose.prod.example.yml`
- `frontend/crisp-react/.env.example`
- `frontend/crisp-react/.env.production.example`

## 📋 Required Environment Variables

### Critical (Must Set for Production):
- `DJANGO_SECRET_KEY` - Django security key (50+ random characters)
- `POSTGRES_PASSWORD` - Database password (strong password)
- `ALLOWED_HOSTS` - Your domain(s)
- `CSRF_TRUSTED_ORIGINS` - Your HTTPS domain(s)

### Optional (But Recommended):
- `OTX_API_KEY` - AlienVault OTX threat intelligence
- `VIRUSTOTAL_API_KEY` - VirusTotal malware scanning
- `EMAIL_HOST_PASSWORD` - For email notifications

### Frontend:
- `VITE_API_BASE_URL` - Backend API URL (HTTP for dev, HTTPS for prod)

## 🔍 Verifying Your Setup

Before deploying, check:

```bash
# Ensure no secrets in git
git status | grep -E "\.env|docker-compose\.prod"

# Should show NO results - if files appear, they're not properly ignored!

# Check for hardcoded secrets
grep -r "AdminPass123\|CrispProd2024" . --exclude-dir=node_modules --exclude-dir=.git

# Should only find demo/test references, not in production configs
```

## 📖 Additional Documentation

- See `SECURITY.md` for comprehensive security guidelines
- See `DEPLOYMENT_README.md` for production deployment steps
- See `SETUP.md` for local development setup

## 🆘 If You Accidentally Committed Secrets

1. **Immediately rotate all exposed credentials**
2. **See `SECURITY.md` section "If Secrets Were Accidentally Committed"**
3. **Contact project maintainers**

## ✅ Checklist Before Deployment

- [ ] Copied all `.example` files and filled in real values
- [ ] Generated strong, unique SECRET_KEY
- [ ] Set strong database password (16+ characters)
- [ ] Updated ALLOWED_HOSTS with production domain
- [ ] Updated CSRF_TRUSTED_ORIGINS with HTTPS domain
- [ ] Set frontend VITE_API_BASE_URL to production domain
- [ ] Verified `.env*` files are NOT in git status
- [ ] Tested configuration locally first
- [ ] Documented secrets in team password manager

---

**Remember:** When in doubt, check if a file is in `.gitignore` before committing!
