# Security Guidelines for CRISP

## 🔐 Credential Management

### CRITICAL: Never Commit Secrets to Git

The following files contain sensitive information and must **NEVER** be committed to version control:

- `.env`
- `.env.production`
- `.env.local`
- `docker-compose.prod.yml` (when containing real credentials)
- `nginx-production.conf` (when containing real domain/cert paths)
- Any file containing API keys, passwords, or secret keys

### Protected Files

These files are already in `.gitignore` and should remain there:
```
.env
.env.local
.env.production
.env.development.local
.env.test.local
.env.production.local
docker-compose.prod.yml
nginx-production.conf
secrets/
.secrets
*.key
*.pem
```

## 📋 Setting Up Secrets Properly

### For Development

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Update with your development credentials:**
   ```bash
   # Safe defaults for local development
   DB_PASSWORD=crisp_dev_password
   DJANGO_SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
   ```

3. **Frontend environment:**
   ```bash
   cd frontend/crisp-react
   cp .env.example .env
   ```

### For Production

1. **Copy example files:**
   ```bash
   cp .env.production.example .env.production
   cp docker-compose.prod.example.yml docker-compose.prod.yml
   ```

2. **Generate strong secrets:**
   ```bash
   # Django secret key (50+ characters)
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   
   # Database password (use a password manager)
   # Example: openssl rand -base64 32
   ```

3. **Update production environment variables:**
   ```bash
   # Edit .env.production
   DJANGO_SECRET_KEY=your-generated-secret-key-here
   POSTGRES_PASSWORD=your-strong-database-password
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   CSRF_TRUSTED_ORIGINS=https://yourdomain.com
   ```

4. **Frontend production config:**
   ```bash
   cd frontend/crisp-react
   cp .env.production.example .env.production
   # Edit and set: VITE_API_BASE_URL=https://yourdomain.com
   ```

## 🚨 If Secrets Were Accidentally Committed

If you've already committed secrets to git, **you must**:

1. **Immediately rotate all exposed credentials:**
   - Change all passwords
   - Regenerate all API keys
   - Generate new Django SECRET_KEY

2. **Remove from git history:**
   ```bash
   # WARNING: This rewrites git history
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env .env.production" \
     --prune-empty --tag-name-filter cat -- --all
   
   # Force push (coordinate with team first!)
   git push origin --force --all
   ```

3. **Better alternative - use BFG Repo-Cleaner:**
   ```bash
   # Install BFG: https://rtyley.github.io/bfg-repo-cleaner/
   bfg --delete-files .env
   bfg --delete-files .env.production
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```

## 🔑 Managing Production Secrets

### Recommended Approaches

1. **Environment Variables on Server:**
   ```bash
   # On production server, create .env file
   export DJANGO_SECRET_KEY="your-secret"
   export POSTGRES_PASSWORD="your-password"
   ```

2. **Docker Secrets (Docker Swarm):**
   ```bash
   echo "my-secret-key" | docker secret create django_secret -
   ```

3. **External Secret Managers:**
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault
   - Google Cloud Secret Manager

4. **For Demo/Testing Only:**
   - Current `docker-compose.prod.yml` uses environment variables
   - Copy from `.env.production.example` and customize
   - Never commit the real production file

## 🎯 Test Data Credentials

The following credentials are **ONLY** for demo/testing purposes and are safe to document:

### Demo Users (Created by `populate_database` command)
- **Admin:** `admin` / `AdminPass123!`
- **Publisher:** `publisher` / `PublisherPass123!`
- **Viewer:** `viewer` / `ViewerPass123!`
- **Super Admins:** `demo` / `AdminPass123!`, `test` / `AdminPass123!`
- **Regular Users:** Various users with `UserPass123!`

⚠️ **These passwords are hardcoded in `populate_database.py` for demo purposes only. In production, ensure:**
- The populate_database command is never run
- Or use `--skip-password-generation` if implemented
- Or immediately change passwords after population

## 📝 Audit Checklist

Before committing, always verify:

- [ ] No `.env` files in git staging area
- [ ] No hardcoded passwords in code (except demo data)
- [ ] No API keys in source files
- [ ] No database credentials in docker-compose files
- [ ] All sensitive configs use `.example` templates
- [ ] Production configs are in `.gitignore`

### Quick Check Command
```bash
# Check for accidentally staged secrets
git status | grep -E "\.env|docker-compose\.prod|nginx-production"

# Search for potential hardcoded secrets
git diff --cached | grep -iE "password|secret_key|api_key" | grep -v "example"
```

## 🛡️ Additional Security Best Practices

### 1. Rotate Secrets Regularly
- Database passwords: Every 90 days
- API keys: Every 180 days
- Django SECRET_KEY: Annually or after suspected compromise

### 2. Use Strong Passwords
- Minimum 16 characters
- Mix of uppercase, lowercase, numbers, symbols
- Use a password manager (1Password, Bitwarden, LastPass)

### 3. Principle of Least Privilege
- Database users should only have necessary permissions
- API keys should be scoped to minimum required access
- Service accounts should be role-specific

### 4. Monitor for Exposed Secrets
- Enable GitHub secret scanning
- Use tools like `truffleHog` or `git-secrets`
- Set up alerts for exposed credentials

### 5. Secure Secret Transmission
- Never send secrets via email or Slack
- Use encrypted channels (Signal, encrypted email)
- Better: Use shared password managers

## 📚 Resources

- [Django Security Best Practices](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [12-Factor App: Config](https://12factor.net/config)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)

## 🆘 Incident Response

If credentials are compromised:

1. **Immediate Actions:**
   - Rotate all affected credentials immediately
   - Review access logs for unauthorized access
   - Notify team and stakeholders

2. **Investigation:**
   - Determine scope of exposure
   - Check for unauthorized access
   - Review audit logs

3. **Remediation:**
   - Update all systems with new credentials
   - Document incident
   - Update security procedures

4. **Prevention:**
   - Review and improve secret management practices
   - Add additional security controls
   - Train team on secure practices

## 📞 Contact

For security concerns or questions:
- Email: security@crisp-project.example.com
- Create a private security advisory on GitHub
- Contact project maintainers directly
