#!/bin/bash

# CRISP Unified System Deployment Script
# This script deploys the unified CRISP threat intelligence platform

set -e  # Exit on any error

echo "🚀 Starting CRISP Unified System Deployment..."

# Check if required tools are installed
check_requirements() {
    echo "📋 Checking system requirements..."
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not installed."
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is required but not installed."
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo "❌ npm is required but not installed."
        exit 1
    fi
    
    echo "✅ System requirements satisfied"
}

# Set up environment variables
setup_environment() {
    echo "🔧 Setting up environment..."
    
    if [ ! -f .env ]; then
        echo "📝 Creating .env file from template..."
        cp .env.example .env
        echo "⚠️  Please edit .env file with your specific configuration before running the system"
    fi
    
    export DJANGO_SETTINGS_MODULE=crisp_unified.settings
}

# Install Python dependencies
install_python_deps() {
    echo "🐍 Installing Python dependencies..."
    
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate || source venv/Scripts/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✅ Python dependencies installed"
}

# Install Node.js dependencies for React frontend
install_node_deps() {
    echo "⚛️  Installing Node.js dependencies..."
    
    cd crisp-react
    npm install
    cd ..
    
    echo "✅ Node.js dependencies installed"
}

# Run database migrations
setup_database() {
    echo "🗄️  Setting up database..."
    
    source venv/bin/activate || source venv/Scripts/activate
    
    echo "🔄 Running database migrations..."
    python manage.py makemigrations
    python manage.py migrate
    
    echo "👤 Setting up initial system data..."
    python manage.py initialize_system --skip-superuser
    
    echo "✅ Database setup complete"
}

# Build React frontend
build_frontend() {
    echo "🏗️  Building React frontend..."
    
    cd crisp-react
    npm run build
    cd ..
    
    echo "✅ Frontend build complete"
}

# Collect static files
collect_static() {
    echo "📁 Collecting static files..."
    
    source venv/bin/activate || source venv/Scripts/activate
    python manage.py collectstatic --noinput
    
    echo "✅ Static files collected"
}

# Run system health check
health_check() {
    echo "🔍 Running system health check..."
    
    source venv/bin/activate || source venv/Scripts/activate
    python manage.py system_health_check --verbose
    
    if [ $? -eq 0 ]; then
        echo "✅ System health check passed"
    else
        echo "⚠️  System health check found issues - review output above"
    fi
}

# Main deployment flow
main() {
    echo "🎯 CRISP Unified System Deployment Starting..."
    echo "📂 Working directory: $(pwd)"
    echo "⏰ Started at: $(date)"
    echo ""
    
    check_requirements
    setup_environment
    install_python_deps
    install_node_deps
    setup_database
    build_frontend
    collect_static
    health_check
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo "📋 Next steps:"
    echo "   1. Review and update .env file with your configuration"
    echo "   2. Configure your web server (nginx/apache) to serve the application"
    echo "   3. Set up SSL certificates for production"
    echo "   4. Configure email settings for notifications"
    echo "   5. Set up backup procedures for the database"
    echo ""
    echo "🚀 To start the development server:"
    echo "   Backend:  python manage.py runserver"
    echo "   Frontend: cd crisp-react && npm run dev"
    echo ""
    echo "📖 For more information, see the documentation in Readme.md"
}

# Run main function
main "$@"