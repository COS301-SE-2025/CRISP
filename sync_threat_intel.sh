#!/bin/bash

echo "🔄 Syncing threat intelligence to Pi..."

# Check Pi server status first
echo "Checking Pi server..."
if ! python check_pi_status.py; then
    echo "❌ Pi server check failed"
    exit 1
fi

echo ""
echo "Running migration..."
if python publish_to_pi.py; then
    echo "✅ Threat intelligence sync completed successfully"
    echo "   Pi Admin: http://100.117.251.119:8001/admin/"
    echo "   Login: datadefenders / DataDefenders123!"
else
    echo "❌ Threat intelligence sync failed"
    exit 1
fi
