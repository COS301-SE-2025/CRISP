# TTP Analysis Data Population

This document explains how to populate the TTP Analysis system with realistic test data for development and testing purposes.

## Overview

The TTP (Tactics, Techniques, Procedures) Analysis system requires realistic data to demonstrate its capabilities. We provide two methods to populate the system with comprehensive test data based on the MITRE ATT&CK framework.

## Method 1: Django Management Command (Recommended)

### Usage

```bash
# Navigate to the Capstone-Unified directory
cd Capstone-Unified

# Basic usage - create 100 TTP records
python manage.py populate_ttp_data

# Custom options
python manage.py populate_ttp_data --count 150 --days-back 120 --clear-existing

# Help
python manage.py populate_ttp_data --help
```

### Options

- `--count N`: Number of TTP records to create (default: 100)
- `--days-back N`: Spread creation dates over N days (default: 90)
- `--clear-existing`: Delete existing TTP data before populating

### Example Output

```
Starting TTP data population...
✓ Created threat feed: APT Intelligence Feed
- Using existing feed: MITRE ATT&CK Techniques
Generated 10/100 TTP records...
Generated 20/100 TTP records...
...
Successfully created 100 TTP records

==================================================
TTP DATA STATISTICS
==================================================
Total TTP Records: 100
Anonymized Records: 18 (18.0%)

TTPs by MITRE Tactic:
  discovery: 22
  defense_evasion: 19
  execution: 15
  initial_access: 12
  ...

TTPs by Threat Feed:
  APT Intelligence Feed: 23
  MITRE ATT&CK Techniques: 21
  Cybercrime TTP Feed: 19
  ...
==================================================
```

## Method 2: Standalone Python Script

### Usage

```bash
# Navigate to the Capstone-Unified directory
cd Capstone-Unified

# Basic usage
python scripts/populate_ttp_data.py

# Custom options
python scripts/populate_ttp_data.py --count 200 --days-back 180 --clear

# Help
python scripts/populate_ttp_data.py --help
```

### Options

- `--count N`: Number of TTP records to create (default: 100)
- `--days-back N`: Spread creation dates over N days (default: 90)
- `--clear`: Clear existing TTP data before populating

## What Data is Created

### 1. Threat Feeds
The script creates 5 realistic threat feeds:
- **APT Intelligence Feed** - Advanced Persistent Threat intelligence
- **MITRE ATT&CK Techniques** - Official MITRE framework techniques
- **Cybercrime TTP Feed** - Cybercriminal tactics and techniques
- **Nation State Indicators** - Nation-state sponsored techniques
- **Ransomware Tactics Feed** - Ransomware-specific TTPs

### 2. TTP Records
Each TTP record includes:
- **MITRE Technique ID** (e.g., T1566.001)
- **Technique Name** (e.g., "Spearphishing Attachment")
- **MITRE Tactic** (e.g., "initial_access")
- **Realistic Description** - Generated using templates and context
- **STIX ID** - Unique STIX identifier
- **Metadata** - Confidence levels, severity, TLP markings, tags
- **Temporal Distribution** - Spread across specified time range
- **Anonymization Status** - ~15-20% marked as anonymized

### 3. MITRE ATT&CK Coverage
The generated data covers all 14 MITRE ATT&CK tactics:
- **Reconnaissance** - Information gathering
- **Resource Development** - Establishing resources
- **Initial Access** - Getting into your network
- **Execution** - Running malicious code
- **Persistence** - Maintaining foothold
- **Privilege Escalation** - Getting higher-level permissions
- **Defense Evasion** - Avoiding detection
- **Credential Access** - Stealing account names/passwords
- **Discovery** - Figuring out your environment
- **Lateral Movement** - Moving through your environment
- **Collection** - Gathering data of interest
- **Command and Control** - Communicating with compromised systems
- **Exfiltration** - Stealing data
- **Impact** - Manipulate, interrupt, or destroy systems

## Data Characteristics

### Realistic Distribution
- **Weighted Technique Selection** - Some techniques appear more frequently
- **Temporal Spread** - Events distributed naturally over time
- **Feed Attribution** - TTPs attributed to different threat feeds
- **Anonymization** - Realistic percentage of anonymized data
- **Confidence Levels** - Mixed confidence ratings (high/medium/low)
- **Severity Levels** - Distributed severity ratings
- **TLP Markings** - Traffic Light Protocol markings for sharing

### Metadata Fields
Each TTP includes rich metadata:
```json
{
  "source": "Intelligence feed: APT Intelligence Feed",
  "confidence": "high",
  "severity": "medium",
  "tlp": "amber",
  "tags": ["apt", "lateral-movement", "persistence"],
  "mitre_version": "14.1",
  "kill_chain_phases": [
    {
      "kill_chain_name": "mitre-attack",
      "phase_name": "initial_access"
    }
  ]
}
```

## Verification

After running the population script, you can verify the data:

### 1. Database Check
```bash
python manage.py shell
>>> from core.models.models import TTPData
>>> TTPData.objects.count()
100
>>> TTPData.objects.values('mitre_tactic').distinct().count()
14
```

### 2. Web Interface
1. Start the development server: `python manage.py runserver`
2. Navigate to the TTP Analysis page
3. Verify data appears in:
   - Overview dashboard
   - MITRE ATT&CK matrix
   - Trends analysis
   - Feed comparison charts
   - Filtering and search functionality

### 3. API Endpoints
Test the API endpoints directly:
```bash
# Get all TTPs
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/ttps/

# Get MITRE matrix data
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/ttps/mitre-matrix/

# Get feed comparison
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/ttps/feed-comparison/?days=30
```

## Cleanup

To remove all TTP data:

```bash
# Using Django shell
python manage.py shell
>>> from core.models.models import TTPData
>>> TTPData.objects.all().delete()

# Or use the script with --clear flag
python manage.py populate_ttp_data --count 0 --clear-existing
```

## Troubleshooting

### Common Issues

1. **Django Setup Error**
   ```
   django.core.exceptions.ImproperlyConfigured: Requested setting ...
   ```
   **Solution**: Ensure `DJANGO_SETTINGS_MODULE` is set correctly

2. **Database Connection Error**
   ```
   django.db.utils.OperationalError: ...
   ```
   **Solution**: Ensure database is running and migrations are applied

3. **Unique Constraint Violation**
   ```
   IntegrityError: duplicate key value violates unique constraint "ttp_data_mitre_technique_id_threat_feed_id_..."
   ```
   **Solution**: The TTPData model has a unique constraint on (mitre_technique_id, threat_feed_id). Use `--clear-existing` flag to remove old data first, or the scripts will automatically skip duplicate combinations.

4. **Invalid Field Names**
   ```
   FieldError: Invalid field name(s) for model ThreatFeed: 'feed_type', 'url'
   ```
   **Solution**: Use correct field names: `taxii_server_url` instead of `url`, and include feed type in `description`

5. **Permission Error**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   **Solution**: Check file permissions or run with appropriate privileges

6. **Import Error**
   ```
   ModuleNotFoundError: No module named 'core'
   ```
   **Solution**: Run from the correct directory (Capstone-Unified root)

### Validation

After population, verify the data integrity:

```python
# Check for required fields
from core.models.models import TTPData
ttps_missing_data = TTPData.objects.filter(
    mitre_technique_id__isnull=True
).count()
print(f"TTPs missing MITRE ID: {ttps_missing_data}")

# Check tactic distribution
from collections import Counter
tactics = TTPData.objects.values_list('mitre_tactic', flat=True)
distribution = Counter(tactics)
print(f"Tactic distribution: {dict(distribution)}")
```

## Performance Notes

- **Bulk Operations**: Scripts use bulk_create() for better performance
- **Transaction Safety**: All operations wrapped in database transactions  
- **Memory Usage**: Processes data in batches to manage memory consumption
- **Index Usage**: Takes advantage of database indexes for efficient queries

## Customization

You can modify the scripts to:
- Add new MITRE techniques
- Adjust temporal distribution patterns
- Modify confidence/severity distributions
- Add custom threat feeds
- Change anonymization rates
- Include additional metadata fields

---

For additional support or customization requests, refer to the main project documentation or contact the development team.