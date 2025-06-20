#!/bin/bash

PI_IP="100.117.251.119"  # Use Tailscale IP
PI_USER="datadefenders"
PI_PATH="/home/datadefenders/crisp_project"
LOCAL_PATH="."

echo "🚀 Syncing to Pi at $PI_IP..."

# First, test connectivity
if ! ping -c 1 "$PI_IP" >/dev/null 2>&1; then
    echo "❌ Cannot reach Pi at $PI_IP"
    exit 1
fi

echo "🔄 Syncing files..."

# Sync your local crisp_backend to Pi
rsync -avz --delete \
    --exclude='venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.git/' \
    --exclude='node_modules/' \
    --exclude='db.sqlite3' \
    --exclude='*.log' \
    "crisp_backend/" "$PI_USER@$PI_IP:$PI_PATH/"

echo "✅ Files synced!"

# Run migrations and restart server on Pi
echo "🔄 Running migrations and restarting server..."
ssh "$PI_USER@$PI_IP" << 'REMOTE_COMMANDS'
cd ~/crisp_project
source ~/venv/bin/activate

echo "Making migrations..."
python manage.py makemigrations

echo "Applying migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Kill any existing Django processes
pkill -f "python manage.py runserver" 2>/dev/null || true

echo "Starting Django server..."
nohup python manage.py runserver 0.0.0.0:8001 > server.log 2>&1 &

sleep 2

# Check if server started
if pgrep -f "python manage.py runserver" > /dev/null; then
    echo "✅ Django server started successfully"
else
    echo "❌ Failed to start Django server"
    cat server.log
fi
REMOTE_COMMANDS

echo "🎉 Sync complete!"
echo "   Server: http://$PI_IP:8001"
echo "   Admin: http://$PI_IP:8001/admin/"
echo "   API: http://$PI_IP:8001/api/auth/"

# Test if server is responding
echo "🧪 Testing server response..."
sleep 3
if curl -s -I "http://$PI_IP:8001/admin/" | head -1 | grep -q "200\|302"; then
    echo "✅ Server is responding!"
    echo "🔑 Login credentials:"
    echo "   Admin: admin / admin123"
    echo "   Analyst: analyst@test.com / test123"
    echo "   Researcher: researcher@up.ac.za / research123"
else
    echo "❌ Server not responding"
fi
