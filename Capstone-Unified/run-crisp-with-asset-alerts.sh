#!/bin/bash
"""
CRISP Asset-Based Alert System - One-Click Deployment
Launches CRISP with the complete Asset-Based Alert System (WOW Factor #1)
"""

echo "🎯 CRISP Asset-Based Alert System Deployment"
echo "============================================="
echo ""
echo "🚀 Starting CRISP with Asset-Based Alert System..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose down > /dev/null 2>&1

# Build and start the services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if backend is ready
echo "🔍 Checking backend status..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/ > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    echo "   Attempt $i/30: Backend not ready yet, waiting..."
    sleep 5
done

# Check if frontend is ready
echo "🔍 Checking frontend status..."
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo "✅ Frontend is ready!"
        break
    fi
    echo "   Attempt $i/30: Frontend not ready yet, waiting..."
    sleep 3
done

echo ""
echo "🎉 CRISP Asset-Based Alert System is now running!"
echo "================================================="
echo ""
echo "📱 Access Points:"
echo "   🌐 Main Application: http://localhost:5173"
echo "   🎯 Asset Management: http://localhost:5173/assets"
echo "   🔗 Backend API: http://localhost:8000/api/"
echo "   📊 Admin Interface: http://localhost:8000/admin/"
echo ""
echo "🔐 Demo Credentials:"
echo "   👤 Username: demo_security_admin"
echo "   🔑 Password: demo123"
echo "   🎭 Role: Publisher (can access Asset Management)"
echo ""
echo "🎯 WOW Factor #1 Features:"
echo "   ✅ Asset inventory management"
echo "   ✅ Custom threat correlation"
echo "   ✅ Multi-channel alert delivery"
echo "   ✅ Real-time asset-based alerts"
echo "   ✅ Demo data pre-loaded"
echo ""
echo "📋 Demo Assets Available:"
echo "   • Demo University organization"
echo "   • 8 sample assets (web servers, domains, software)"
echo "   • Pre-configured threat indicators"
echo "   • Generated custom alerts"
echo ""
echo "🛠️ To view logs:"
echo "   docker-compose logs -f backend"
echo "   docker-compose logs -f frontend"
echo ""
echo "🛑 To stop:"
echo "   docker-compose down"
echo ""
echo "📖 Navigate to http://localhost:5173 and login to get started!"
echo "   Then go to Management > Asset-Based Alerts to see the WOW Factor!"