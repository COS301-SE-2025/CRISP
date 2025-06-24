#!/bin/bash

# Stop SSH Tunnels Script
# This script stops all SSH tunnels to the Raspberry Pi

PI_HOST="100.117.251.119"

echo "🛑 Stopping SSH tunnels to Raspberry Pi..."

# Find and kill SSH tunnel processes
TUNNEL_PIDS=$(pgrep -f "ssh.*$PI_HOST.*localhost:")

if [ -n "$TUNNEL_PIDS" ]; then
    echo "🔍 Found tunnel processes: $TUNNEL_PIDS"
    echo "$TUNNEL_PIDS" | xargs kill
    echo "✅ SSH tunnels stopped"
else
    echo "ℹ️  No active SSH tunnels found"
fi

echo "🏁 Done!"