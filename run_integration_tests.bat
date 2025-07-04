@echo off
echo 🔗 CRISP Integration Test Suite
echo ================================
echo Testing UserManagement and TrustManagement Integration
echo.

REM Set environment variables
set DJANGO_SETTINGS_MODULE=crisp.settings.integrated

echo 📋 Step 1: System Checks
echo --------------------------
python manage_unified.py check
if %errorlevel% neq 0 (
    echo ❌ System checks failed
    pause
    exit /b 1
)
echo ✅ System checks passed
echo.

echo 📋 Step 2: Database Setup
echo --------------------------
echo Creating migrations...
python manage_unified.py makemigrations user_management
python manage_unified.py makemigrations trust_management
python manage_unified.py makemigrations core

echo Applying migrations...
python manage_unified.py migrate
if %errorlevel% neq 0 (
    echo ❌ Database setup failed
    pause
    exit /b 1
)
echo ✅ Database setup completed
echo.

echo 📋 Step 3: Running Integration Tests
echo -------------------------------------
python manage_unified.py test apps.core.tests_integration --verbosity=2
if %errorlevel% neq 0 (
    echo ❌ Integration tests failed
    pause
    exit /b 1
)
echo ✅ Integration tests passed
echo.

echo 📋 Step 4: Running Integration Script
echo --------------------------------------
python run_integration_tests.py
if %errorlevel% neq 0 (
    echo ❌ Integration script failed
    pause
    exit /b 1
)
echo ✅ Integration script completed
echo.

echo 🎉 INTEGRATION COMPLETE!
echo ========================
echo ✅ UserManagement and TrustManagement successfully integrated
echo ✅ All tests passed
echo ✅ System ready for development
echo.
echo You can now run: python manage_unified.py runserver
pause
