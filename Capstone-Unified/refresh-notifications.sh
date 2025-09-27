#!/bin/bash

# Quick script to generate a new alert and test the notification system

echo "🚀 Generating new asset alert for testing..."

# Run the asset monitoring test to generate new alerts
python3 manage.py test_asset_monitoring --hours-back=1 > /dev/null 2>&1

echo "✅ Alert generated! Check your browser notifications panel."
echo ""
echo "🔍 Expected results:"
echo "  • New notifications should appear in the Notifications tab"
echo "  • Toast notifications should pop up (if you're logged in)"
echo "  • Browser notifications should appear (if permission granted)"
echo "  • Unread count badge should update"
echo ""
echo "📊 Current alert status:"
python3 test_notifications_api.py | grep -E "(Custom alerts|📢|Most recent)"

echo ""
echo "🔄 The system monitors every 5 minutes automatically."
echo "💡 Refresh the notifications page to see the latest alerts!"