#!/bin/bash

# CRISP Security Testing Toolkit Setup Script
# This script installs and configures security testing tools for local assessment only

set -e

echo "=================================================="
echo "   CRISP Security Testing Toolkit Setup"
echo "=================================================="
echo "WARNING: These tools are for LOCAL TESTING ONLY"
echo "Never use against production or external systems"
echo "=================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on supported OS
check_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        PACKAGE_MANAGER="apt"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="mac"
        PACKAGE_MANAGER="brew"
    else
        print_error "Unsupported OS. This script supports Linux and macOS only."
        exit 1
    fi
    print_status "Detected OS: $OS"
}

# Update package manager
update_packages() {
    print_status "Updating package manager..."
    if [[ "$OS" == "linux" ]]; then
        sudo apt update -y
    elif [[ "$OS" == "mac" ]]; then
        brew update
    fi
    print_success "Package manager updated"
}

# Install Python and pip if not present
install_python() {
    print_status "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        print_status "Installing Python 3..."
        if [[ "$OS" == "linux" ]]; then
            sudo apt install -y python3 python3-pip python3-venv
        elif [[ "$OS" == "mac" ]]; then
            brew install python
        fi
    fi
    
    if ! command -v pip3 &> /dev/null; then
        print_status "Installing pip..."
        if [[ "$OS" == "linux" ]]; then
            sudo apt install -y python3-pip
        fi
    fi
    print_success "Python and pip are available"
}

# Install OWASP ZAP
install_zap() {
    print_status "Installing OWASP ZAP..."
    
    if [[ "$OS" == "linux" ]]; then
        # Check if ZAP is already installed
        if ! command -v zap.sh &> /dev/null; then
            # Install Java (required for ZAP)
            sudo apt install -y openjdk-11-jdk wget
            
            # Download and install ZAP
            cd /tmp
            wget https://github.com/zaproxy/zaproxy/releases/download/v2.14.0/ZAP_2.14.0_Linux.tar.gz
            tar -xzf ZAP_2.14.0_Linux.tar.gz
            sudo mv ZAP_2.14.0 /opt/zaproxy
            sudo ln -sf /opt/zaproxy/zap.sh /usr/local/bin/zap.sh
            sudo chmod +x /usr/local/bin/zap.sh
        fi
    elif [[ "$OS" == "mac" ]]; then
        if ! command -v zap.sh &> /dev/null; then
            brew install --cask owasp-zap
        fi
    fi
    
    print_success "OWASP ZAP installed"
}

# Install Nikto
install_nikto() {
    print_status "Installing Nikto..."
    
    if [[ "$OS" == "linux" ]]; then
        sudo apt install -y nikto
    elif [[ "$OS" == "mac" ]]; then
        brew install nikto
    fi
    
    print_success "Nikto installed"
}

# Install Bandit
install_bandit() {
    print_status "Installing Bandit..."
    pip3 install --user bandit[toml]
    
    # Add user bin to PATH if not already there
    echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
    export PATH=$PATH:~/.local/bin
    
    print_success "Bandit installed"
}

# Install sqlmap
install_sqlmap() {
    print_status "Installing sqlmap..."
    
    if [[ "$OS" == "linux" ]]; then
        sudo apt install -y sqlmap
    elif [[ "$OS" == "mac" ]]; then
        brew install sqlmap
    fi
    
    print_success "sqlmap installed"
}

# Install Hydra
install_hydra() {
    print_status "Installing Hydra..."
    
    if [[ "$OS" == "linux" ]]; then
        sudo apt install -y hydra
    elif [[ "$OS" == "mac" ]]; then
        brew install hydra
    fi
    
    print_success "Hydra installed"
}

# Create security testing directory structure
create_directory_structure() {
    print_status "Creating security testing directory structure..."
    
    mkdir -p security-testing/{reports,configs,wordlists,scripts}
    
    print_success "Directory structure created"
}

# Download common wordlists
download_wordlists() {
    print_status "Downloading common wordlists..."
    
    cd security-testing/wordlists
    
    # Common usernames
    cat > common_usernames.txt << 'EOF'
admin
administrator
root
user
test
guest
demo
service
default
crisp
system
api
EOF

    # Common passwords
    cat > common_passwords.txt << 'EOF'
password
123456
admin
password123
crisp
default
test
guest
demo
12345
qwerty
letmein
changeme
EOF

    # API endpoints for CRISP project
    cat > api_endpoints.txt << 'EOF'
/api/auth/login/
/api/auth/register/
/api/auth/logout/
/api/users/
/api/organizations/
/api/threat-feeds/
/api/indicators/
/api/trust/
/api/admin/
/admin/
/taxii/
EOF

    print_success "Wordlists downloaded"
}

# Main installation function
main() {
    check_os
    update_packages
    install_python
    install_zap
    install_nikto
    install_bandit
    install_sqlmap
    install_hydra
    create_directory_structure
    download_wordlists
    
    print_success "All security testing tools installed successfully!"
    echo ""
    print_warning "IMPORTANT REMINDERS:"
    echo "1. These tools are for LOCAL TESTING ONLY"
    echo "2. Never run these against production systems"
    echo "3. Always get proper authorization before testing"
    echo "4. Review and understand each tool before using"
    echo ""
    print_status "Next steps:"
    echo "1. Run: source ~/.bashrc (to update PATH)"
    echo "2. Use the security-testing-guide.md for detailed usage instructions"
    echo "3. Execute: ./run-security-tests.sh to start automated testing"
}

# Run main function
main