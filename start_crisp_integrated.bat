@echo off
echo 🚀 CRISP Integrated Server Startup
echo ==================================
echo Starting UserManagement + TrustManagement Integration
echo.

REM Set environment variables
set DJANGO_SETTINGS_MODULE=crisp.settings.integrated

echo 📋 Checking system...
python manage_unified.py check --deploy
if %errorlevel% neq 0 (
    echo ❌ System check failed
    pause
    exit /b 1
)

echo 📋 Applying any pending migrations...
python manage_unified.py migrate --run-syncdb

echo 📋 Collecting static files...
python manage_unified.py collectstatic --noinput

echo.
echo 🌐 Starting CRISP server on http://127.0.0.1:8000
echo ================================================
echo Admin interface: http://127.0.0.1:8000/admin/
echo API endpoints: http://127.0.0.1:8000/api/
echo.
echo Press Ctrl+C to stop the server
echo.

python manage_unified.py runserver 127.0.0.1:8000
