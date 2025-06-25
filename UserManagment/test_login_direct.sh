#!/bin/bash
# Direct login test script

echo "🔐 CRISP JWT Authentication Test"
echo "================================"

# Get credentials
read -p "Enter username: " USERNAME
read -s -p "Enter password: " PASSWORD
echo

echo "1. Testing login..."

# Test login
LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")

echo "Login response:"
echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"

# Extract access token
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if 'tokens' in data and 'access' in data['tokens']:
        print(data['tokens']['access'])
    else:
        print('NO_TOKEN')
except:
    print('PARSE_ERROR')
" 2>/dev/null)

if [ "$ACCESS_TOKEN" != "NO_TOKEN" ] && [ "$ACCESS_TOKEN" != "PARSE_ERROR" ] && [ ! -z "$ACCESS_TOKEN" ]; then
    echo ""
    echo "2. Testing profile access with token..."
    echo "Token (first 50 chars): ${ACCESS_TOKEN:0:50}..."
    
    PROFILE_RESPONSE=$(curl -s -X GET http://127.0.0.1:8000/api/auth/profile/ \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Content-Type: application/json")
    
    echo "Profile response:"
    echo "$PROFILE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$PROFILE_RESPONSE"
    
    echo ""
    echo "3. Testing other endpoints..."
    
    ENDPOINTS=(
        "/api/user/dashboard/"
        "/api/user/organization-users/"
        "/api/admin/users/"
    )
    
    for endpoint in "${ENDPOINTS[@]}"; do
        echo "Testing $endpoint..."
        RESPONSE=$(curl -s -w "HTTP_STATUS:%{http_code}" -X GET "http://127.0.0.1:8000$endpoint" \
          -H "Authorization: Bearer $ACCESS_TOKEN" \
          -H "Content-Type: application/json")
        
        HTTP_STATUS=$(echo "$RESPONSE" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
        BODY=$(echo "$RESPONSE" | sed 's/HTTP_STATUS:[0-9]*$//')
        
        if [ "$HTTP_STATUS" = "200" ]; then
            echo "  ✅ $endpoint: Success ($HTTP_STATUS)"
        else
            echo "  ❌ $endpoint: Failed ($HTTP_STATUS)"
        fi
        echo "  Response: $BODY"
        echo
    done
    
else
    echo "❌ Failed to extract access token from login response"
    echo "Debug info:"
    echo "ACCESS_TOKEN value: '$ACCESS_TOKEN'"
fi

echo "================================"
echo "💡 Next steps:"
echo "1. Go to: http://127.0.0.1:8000/api/auth/debug/"
echo "2. Go to: http://127.0.0.1:8000/api/auth/login-page/"
echo "3. Check browser console for JavaScript errors"