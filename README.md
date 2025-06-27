# CRISP - Cyber Risk Information Sharing Platform

🔒 **A comprehensive threat intelligence sharing platform with trust-based anonymization**

## Project Structure

```
.
├── core/                    # Django application
│   ├── models/             # Database models (STIX, indicators, trust)
│   ├── services/           # Business logic services  
│   ├── strategies/         # Anonymization and trust strategies
│   ├── api/               # REST API endpoints
│   ├── docs/              # Documentation
│   ├── scripts/           # Utility scripts
│   ├── static/            # Static files
│   ├── tests/             # Application tests
│   └── manage.py          # Django management
├── crisp/                  # Django project settings
│   ├── settings.py        # Main settings
│   ├── urls.py            # URL configuration
│   ├── wsgi.py            # WSGI application
│   └── ...                # Other Django project files
├── backup/                # Archived files
├── .venv/                 # Virtual environment
└── README.md              # This file
```

## 🚀 Quick Start

```bash
cd core
python3 manage.py runserver
```

## 🌐 Access

- **URL:** http://127.0.0.1:8000/admin/
- **Username:** admin
- **Password:** admin

## 📊 System Features

- ✅ **9,292 STIX Objects** - Real threat intelligence from AlienVault OTX
- ✅ **37 Organizations** - Government, commercial, academic entities
- ✅ **32 Users** - Multiple roles (admin, analyst, publisher, viewer)
- ✅ **9 Anonymized Indicators** - Privacy-preserving threat sharing
- ✅ **Trust-based Anonymization** - Multiple anonymization levels
- ✅ **STIX/TAXII Compliance** - Full STIX 2.1 support
- ✅ **Role-based Access Control** - Secure multi-organization access

## 🔒 Anonymization Examples

View anonymized data in Django Admin → Indicators:
- IP: `203.0.113.100` → `203.0.113.0/24`
- Domain: `evil-malware.com` → `[REDACTED].com`  
- Email: `attacker@phishing.com` → `[REDACTED]@phishing.com`

## 🏆 Status: PRODUCTION READY ✅

The CRISP system is fully functional with:
- Complete threat intelligence database
- Working anonymization system
- Established trust relationships
- Comprehensive audit logging
