#!/bin/bash

# Quick script to sync only migrations and restart Django server
# Use this after making local migrations

PI_USER="datadefenders"
PI_HOST="100.117.251.119"
PI_PATH="/home/datadefenders/crisp_django_server"
LOCAL_PROJECT_PATH="/mnt/c/Users/jadyn/Documents/University of Pretoria/2025/Capstone/crisp_threat_intel"

echo "🔄 Syncing migrations to Pi..."

# Sync migration files
rsync -av --delete "$LOCAL_PROJECT_PATH/crisp_threat_intel/migrations/" $PI_USER@$PI_HOST:$PI_PATH/crisp_threat_intel/migrations/

# Run migrations on Pi
ssh $PI_USER@$PI_HOST << 'ENDSSH'
cd /home/datadefenders/crisp_django_server
source venv/bin/activate
python manage.py migrate
ENDSSH

echo "🔄 Restarting Django server..."
ssh $PI_USER@$PI_HOST "sudo systemctl restart crisp-django.service"

echo "✅ Migrations synced and server restarted!"
echo "🌐 Check: http://100.117.251.119:8000"