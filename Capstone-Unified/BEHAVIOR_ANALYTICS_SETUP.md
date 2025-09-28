# User Behavior Analytics Setup

## Overview
The CRISP User Behavior Analytics system is **production ready** and provides two levels of functionality:

1. **Basic Analytics** (Python stdlib only) - Production-ready statistical analysis using built-in functions
2. **Enhanced Analytics** (with ML dependencies) - Advanced machine learning-based anomaly detection

## Production Readiness ✅
The system is fully production ready with the basic installation. The enhanced analytics provide additional capabilities but are not required for production deployment.

## Installation Options

### Option 1: Basic Installation (Default)
The system works out-of-the-box with Python's standard library:
```bash
pip install -r requirements.txt
```

### Option 2: Enhanced Analytics Installation
For advanced ML-based anomaly detection, install the additional dependencies:
```bash
# Install all dependencies including ML libraries
pip install -r requirements.txt

# Or install just the enhanced analytics packages
pip install numpy>=1.24.0 scipy>=1.10.0 scikit-learn>=1.3.0 pandas>=2.0.0
```

## Features by Installation Type

### Basic Analytics (Always Available)
- ✅ Statistical threshold-based anomaly detection
- ✅ Baseline behavioral pattern learning
- ✅ Login frequency analysis
- ✅ Time pattern detection
- ✅ Session duration analysis
- ✅ API usage monitoring
- ✅ System logs export (CSV/JSON)
- ✅ Real-time behavior alerts

### Enhanced Analytics (With ML Dependencies)
- ✅ All basic features PLUS:
- 🚀 Machine learning-based anomaly detection using Isolation Forest
- 🚀 Advanced statistical tests using SciPy
- 🚀 Efficient data processing with Pandas
- 🚀 High-performance numerical computations with NumPy
- 🚀 Feature engineering and normalization
- 🚀 Unsupervised anomaly detection

## Checking Available Features
You can check which analytics capabilities are available in your installation:

```python
from core.services.user_behavior_analytics_service import UserBehaviorAnalyticsService

service = UserBehaviorAnalyticsService()
capabilities = service.get_analytics_capabilities()
print(capabilities)
```

## Production Recommendations

### For Development/Testing
- Basic installation is sufficient for most development and testing scenarios
- Faster installation and fewer dependencies

### For Production Environments
- Enhanced installation recommended for:
  - High-security environments
  - Large user bases (>100 users)
  - Advanced threat detection requirements
  - Compliance environments requiring ML-based anomaly detection

### Performance Considerations
- **Basic Analytics**: Minimal memory usage, fast startup
- **Enhanced Analytics**: Higher memory usage (~100-200MB additional), longer startup time, more accurate anomaly detection

## Dependencies Overview

### Core Dependencies (Always Required)
- Django 4.2.10
- djangorestframework 3.14.0
- psycopg2-binary 2.9.9
- celery 5.3.4
- redis 5.0.1

### Enhanced Analytics Dependencies (Optional)
- numpy>=1.24.0 - Numerical computations
- scipy>=1.10.0 - Statistical functions
- scikit-learn>=1.3.0 - Machine learning algorithms
- pandas>=2.0.0 - Data manipulation and analysis

## Troubleshooting

### Import Errors
If you see import errors related to numpy, scipy, etc., the system will automatically fall back to basic analytics mode.

### Memory Issues
If you experience memory issues with enhanced analytics, consider:
1. Reducing the analysis timeframe
2. Using basic analytics mode
3. Increasing available system memory

### Installation Issues
For installation issues with ML dependencies:
```bash
# On Ubuntu/Debian
sudo apt-get install python3-dev build-essential

# On CentOS/RHEL
sudo yum install python3-devel gcc gcc-c++

# Then retry pip install
pip install numpy scipy scikit-learn pandas
```

## API Endpoints
Regardless of installation type, all API endpoints remain the same:
- `GET /api/behavior-analytics/dashboard/` - Main dashboard
- `GET /api/behavior-analytics/logs/` - System activity logs
- `GET /api/behavior-analytics/logs/download/` - Download logs
- `GET /api/behavior-analytics/anomalies/` - Detected anomalies
- `GET /api/behavior-analytics/alerts/` - Active alerts

The enhanced features are automatically available when dependencies are installed, with no configuration changes required.