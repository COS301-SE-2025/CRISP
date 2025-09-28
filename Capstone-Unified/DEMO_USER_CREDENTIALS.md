# CRISP Demo User Credentials

This document contains the login credentials for all demo users created by the asset alert system population script.

## How to Use

1. Run the population script: `python manage.py populate_asset_demo_data`
2. Use any of the credentials below to log into the system
3. Navigate to the Asset Management section to see the enhanced alert system in action

## Demo Organizations and Users

### 1. TechCorp University (Educational)
**Domain:** techcorp.edu
**Type:** Educational Institution

| Username | Password | Role | Email | Description |
|----------|----------|------|-------|-------------|
| `techcorp_admin` | `demo123!` | BlueVisionAdmin | admin@techcorp.edu | Full admin access |
| `techcorp_publisher` | `demo123!` | Publisher | publisher@techcorp.edu | Can publish threat intel |
| `techcorp_viewer` | `demo123!` | Viewer | viewer@techcorp.edu | Read-only access |

**Sample Assets:**
- Student Portal (portal.techcorp.edu)
- Research Database (research.techcorp.edu) - CRITICAL
- Campus Network (10.1.0.0/16)
- Library System (library.techcorp.edu)
- Learning Management System (lms.techcorp.edu)

---

### 2. StateGov Department (Government)
**Domain:** stategov.gov
**Type:** Government Agency

| Username | Password | Role | Email | Description |
|----------|----------|------|-------|-------------|
| `stategov_admin` | `demo123!` | BlueVisionAdmin | admin@stategov.gov | Full admin access |
| `stategov_publisher` | `demo123!` | Publisher | publisher@stategov.gov | Can publish threat intel |
| `stategov_viewer` | `demo123!` | Viewer | viewer@stategov.gov | Read-only access |

**Sample Assets:**
- Citizen Portal (portal.stategov.gov) - CRITICAL
- Emergency Services (emergency.stategov.gov) - CRITICAL
- Public Website (www.stategov.gov)
- Records System (records.stategov.gov) - CRITICAL
- Payment Gateway (payments.stategov.gov) - CRITICAL

---

### 3. SecureFinance Corp (Private/Financial)
**Domain:** securefinance.com
**Type:** Private Financial Services

| Username | Password | Role | Email | Description |
|----------|----------|------|-------|-------------|
| `securefinance_admin` | `demo123!` | BlueVisionAdmin | admin@securefinance.com | Full admin access |
| `securefinance_publisher` | `demo123!` | Publisher | publisher@securefinance.com | Can publish threat intel |
| `securefinance_viewer` | `demo123!` | Viewer | viewer@securefinance.com | Read-only access |

**Sample Assets:**
- Customer Portal (portal.securefinance.com) - CRITICAL
- API Gateway (api.securefinance.com) - CRITICAL
- Database Cluster (172.16.1.0/24) - CRITICAL
- Mobile App Backend (mobile-api.securefinance.com)
- Analytics Platform (analytics.securefinance.com)

---

## Quick Start Guide

### 1. Login Process
1. Navigate to the CRISP login page
2. Use any username/password combination from above
3. You'll be logged in as that specific user with their role permissions

### 2. Asset Management Features
After logging in, go to the Asset Management section to explore:

- **Asset Inventory**: View and manage organizational assets
- **Custom Alerts**: See IoC-based alerts targeting your assets
- **Smart Correlation**: Trigger manual correlation between threats and assets
- **Real-time Monitoring**: Auto-refreshing alert feed
- **Multi-channel Notifications**: Email, SMS, Slack integration

### 3. Testing Alert Generation
1. Login as an admin user
2. Go to Asset Management
3. Click "Trigger Correlation" to generate new alerts
4. View the generated alerts in the Alerts tab
5. Click on alerts to see detailed information
6. Use alert actions (Acknowledge, Resolve, Dismiss, Escalate)

### 4. Demo Data Overview
The population script creates:
- **50+ realistic assets** across all organizations
- **50 threat indicators** (domains, IPs, file hashes)
- **Automatically generated alerts** based on IoC correlation
- **Manual demo alerts** showing various scenarios
- **Proper asset criticality levels** (Critical, High, Medium, Low)

## System Features Demonstrated

### WOW Factor #1: Asset-Based Alert System
- ✅ **IoC Correlation**: Automatic matching of threat indicators with organizational assets
- ✅ **Custom Alert Generation**: Smart alerts based on asset criticality and threat relevance
- ✅ **Multi-channel Notifications**: Email, SMS, Slack, webhooks, ticketing systems
- ✅ **Real-time Monitoring**: Live alert feeds and auto-refresh capabilities
- ✅ **Advanced UI**: Modern, responsive design with proper icons and styling
- ✅ **Asset Management**: Full CRUD operations for asset inventory
- ✅ **Bulk Operations**: Bulk asset upload via JSON files
- ✅ **Search & Filtering**: Advanced search and filtering for assets and alerts
- ✅ **Alert Actions**: Acknowledge, resolve, dismiss, escalate alerts
- ✅ **Audit Trail**: Complete history of alert status changes

### Enhanced Features (Beyond Requirements)
- 🚀 **Smart Correlation Accuracy**: AI-powered relevance scoring
- 🚀 **Real-time Statistics**: Live dashboards with metrics and trends
- 🚀 **Advanced Asset Types**: Support for domains, IP ranges, software, services
- 🚀 **Notification Preferences**: Customizable alert channels per organization
- 🚀 **Response Actions**: Automated recommended actions for each alert
- 🚀 **Threat Intelligence Integration**: Seamless integration with existing STIX/TAXII feeds
- 🚀 **Performance Optimization**: Efficient querying and caching for large datasets

## Troubleshooting

### Common Issues
1. **Login Failed**: Ensure you're using the exact username and password from the tables above
2. **No Assets Visible**: Make sure the population script ran successfully
3. **No Alerts Generated**: Click "Trigger Correlation" to generate alerts manually
4. **Permission Denied**: Admin users have full access, Publishers can modify data, Viewers are read-only

### Reset Demo Data
To reset all demo data:
```bash
python manage.py populate_asset_demo_data --clean
```

### Population Script Options
```bash
# Create more organizations
python manage.py populate_asset_demo_data --organizations 5

# Create more assets per organization
python manage.py populate_asset_demo_data --assets-per-org 25

# Create more threat indicators
python manage.py populate_asset_demo_data --indicators 100

# Clean and recreate everything
python manage.py populate_asset_demo_data --clean --organizations 3 --assets-per-org 20 --indicators 75
```

## Security Notes

⚠️ **IMPORTANT**: These are demo credentials only!
- All passwords are `demo123!`
- These accounts should only be used for demonstration purposes
- In production, use strong, unique passwords and proper authentication
- All demo data is clearly marked in the database with `metadata.demo = true`

## Support

If you encounter any issues with the demo system:
1. Check the Django logs for error messages
2. Ensure all database migrations have been applied
3. Verify that the AssetBasedAlertService is properly configured
4. Contact the development team for technical support

---

**Last Updated:** September 2024
**Version:** 1.0.0
**System:** CRISP Unified Platform - Asset Alert System Demo