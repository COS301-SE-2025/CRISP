#!/bin/bash
# Test script to verify viewer login functionality

echo "🔐 Testing CRISP User Management Login"
echo "======================================"

# Test 1: Check if server is running
echo "1. Checking if server is running..."
if curl -s http://127.0.0.1:8000/admin/ > /dev/null 2>&1; then
    echo "   ✅ Server is running"
else
    echo "   ❌ Server is not running"
    echo "   💡 Start server with: python3 manage.py runserver"
    exit 1
fi

# Test 2: Test API endpoint (should get Method Not Allowed for GET)
echo ""
echo "2. Testing API endpoint..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/auth/login/)
if [ "$RESPONSE" = "405" ]; then
    echo "   ✅ API endpoint is accessible (Method Not Allowed for GET as expected)"
else
    echo "   ❌ Unexpected response: $RESPONSE"
fi

# Test 3: Test login page
echo ""
echo "3. Testing login page..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/api/auth/login-page/)
if [ "$RESPONSE" = "200" ]; then
    echo "   ✅ Login page is accessible"
else
    echo "   ❌ Login page not accessible: $RESPONSE"
fi

# Test 4: Attempt login with test credentials
echo ""
echo "4. Testing login with sample credentials..."
echo "   (This will fail if no test user exists, which is expected)"

LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_viewer",
    "password": "ViewerTestPass123!"
  }')

echo "   Response: $LOGIN_RESPONSE"

if echo "$LOGIN_RESPONSE" | grep -q "access"; then
    echo "   ✅ Login successful with test credentials!"
    
    # Extract access token for further testing
    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access":"[^"]*"' | cut -d'"' -f4)
    
    if [ ! -z "$ACCESS_TOKEN" ]; then
        echo ""
        echo "5. Testing profile access with token..."
        PROFILE_RESPONSE=$(curl -s -X GET http://127.0.0.1:8000/api/auth/profile/ \
          -H "Authorization: Bearer $ACCESS_TOKEN")
        
        echo "   Profile Response: $PROFILE_RESPONSE"
        
        if echo "$PROFILE_RESPONSE" | grep -q "username"; then
            echo "   ✅ Profile access successful!"
        else
            echo "   ❌ Profile access failed"
        fi
    fi
    
elif echo "$LOGIN_RESPONSE" | grep -q "authentication_failed\|invalid_credentials"; then
    echo "   ℹ️  Expected failure - test user doesn't exist or wrong password"
else
    echo "   ❌ Unexpected login response"
fi

echo ""
echo "======================================"
echo "📋 INSTRUCTIONS:"
echo "1. Create a viewer user through Django admin:"
echo "   - Go to http://127.0.0.1:8000/admin/"
echo "   - Login as superuser"
echo "   - Create a user with role 'viewer'"
echo ""
echo "2. Test login via web interface:"
echo "   - Go to http://127.0.0.1:8000/api/auth/login-page/"
echo "   - Enter your credentials"
echo ""
echo "3. Test login via curl:"
echo 'curl -X POST http://127.0.0.1:8000/api/auth/login/ \'
echo '  -H "Content-Type: application/json" \'
echo '  -d "{"username": "your_username", "password": "your_password"}"'
echo ""
echo "4. The API endpoint /api/auth/login/ only accepts POST requests"
echo "   That's why GET requests return 'Method Not Allowed'"