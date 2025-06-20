#!/bin/bash

PI_IP="100.117.251.119"
PI_USER="datadefenders"

echo "🔄 Quick development sync..."

# Only sync the specific files that change frequently
rsync -avz \
    --include='*.py' \
    --include='*.js' \
    --include='*.jsx' \
    --exclude='*' \
    "crisp_backend/" "$PI_USER@$PI_IP:/home/datadefenders/crisp_project/"

# Restart only the server
ssh "$PI_USER@$PI_IP" << 'REMOTE_COMMANDS'
cd ~/crisp_project
source ~/venv/bin/activate
pkill -f "python manage.py runserver" 2>/dev/null || true
nohup python manage.py runserver 0.0.0.0:8001 > server.log 2>&1 &
echo "🚀 Server restarted"
REMOTE_COMMANDS

echo "✅ Quick sync complete!"
