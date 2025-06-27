# Security Configuration

This directory contains sensitive configuration files for the CRISP platform.

## Files

- **`.env`** - Production environment variables (NEVER commit this file)
- **`.env.template`** - Template for environment configuration

## Setup Instructions

1. Copy `.env.template` to `.env`
2. Fill in your actual values in `.env`
3. Never commit `.env` files to version control

## Security Notes

⚠️ **CRITICAL**: The `.env` file contains sensitive information including:
- Database passwords
- API keys
- Secret keys for cryptographic operations
- Email service credentials

These files are automatically excluded from git via `.gitignore` patterns.

## Environment Variables

All environment variables are loaded automatically by Django settings from this location:
```
crisp/config/security/.env
```

If you need to add new environment variables:
1. Add them to `.env.template` with placeholder values
2. Add them to your local `.env` with real values
3. Update the Django settings to use the new variables