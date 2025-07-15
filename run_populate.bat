@echo off
echo 🚀 CRISP Database Population Setup
echo ==================================

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please create one first:
    echo    python -m venv venv
    echo    venv\Scripts\activate
    echo    pip install -r requirements.txt
    pause
    exit /b 1
)

REM Install faker if not present
echo 📦 Installing required dependencies...
pip install faker

REM Check if database is accessible
echo 🔍 Checking database connection...
python -c "import os; import django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.TrustManagement.settings'); django.setup(); from django.db import connection; connection.cursor().execute('SELECT 1'); print('✅ Database connection successful')"

if %errorlevel% == 0 (
    echo.
    echo 🎯 Starting database population...
    python populate_database.py
) else (
    echo ❌ Database check failed. Please fix database connection before running population script.
    pause
)

pause