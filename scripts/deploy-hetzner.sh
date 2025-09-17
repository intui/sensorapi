#!/bin/bash

# Hetzner Docker Deployment Script for Sensor API
# This script deploys the Sensor API platform to a Hetzner server using Docker

set -e

echo "🚀 Hetzner Docker Deployment - Sensor API Platform"
echo "=================================================="
echo ""

# Configuration
DEPLOY_USER=${DEPLOY_USER:-"sensor"}
SERVER_IP=${SERVER_IP:-""}
DOMAIN=${DOMAIN:-""}
PROJECT_NAME="sensorapi"
DOCKER_COMPOSE_FILE="docker-compose.production.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check requirements
check_requirements() {
    log_info "Checking deployment requirements..."
    
    if [ -z "$SERVER_IP" ]; then
        log_error "SERVER_IP environment variable is required"
        echo "Usage: SERVER_IP=your.server.ip DOMAIN=your.domain.com ./scripts/deploy-hetzner.sh"
        exit 1
    fi
    
    if ! command -v ssh &> /dev/null; then
        log_error "SSH is required but not installed"
        exit 1
    fi
    
    if ! command -v scp &> /dev/null; then
        log_error "SCP is required but not installed"
        exit 1
    fi
    
    log_info "Requirements check passed ✓"
}

# Setup server dependencies
setup_server() {
    log_info "Setting up server dependencies on $SERVER_IP (Docker CE App Image)..."
    
    ssh root@$SERVER_IP << 'EOF'
        # Update system packages
        apt-get update && apt-get upgrade -y
        
        # Docker and Docker Compose should already be installed with Docker CE app image
        # Let's verify and ensure they're working
        if ! command -v docker &> /dev/null; then
            echo "ERROR: Docker not found. Please ensure you used the Docker CE app image."
            exit 1
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            echo "Installing Docker Compose..."
            curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            chmod +x /usr/local/bin/docker-compose
        fi
        
        # Verify Docker is running
        systemctl enable docker
        systemctl start docker
        
        # Test Docker installation
        docker --version
        docker-compose --version
        
        # Create deployment user
        if ! id "sensor" &>/dev/null; then
            useradd -m -s /bin/bash sensor
            usermod -aG docker sensor
            echo "Created sensor user and added to docker group"
        fi
        
        # Install additional useful tools
        apt-get install -y nginx-utils htop curl wget git ufw
        
        # Setup firewall (if not already configured)
        ufw --force reset
        ufw default deny incoming
        ufw default allow outgoing
        ufw allow ssh
        ufw allow 80
        ufw allow 443
        ufw --force enable
        
        # Ensure Docker service is accessible to sensor user
        newgrp docker
        
        echo "✅ Server setup completed - Docker CE app image optimized"
EOF
    
    log_info "Server setup completed ✓"
}

# Deploy application
deploy_application() {
    log_info "Deploying application to $SERVER_IP..."
    
    # Create deployment directory on server
    ssh $DEPLOY_USER@$SERVER_IP "mkdir -p ~/$PROJECT_NAME"
    
    # Copy application files
    log_info "Copying application files..."
    scp -r . $DEPLOY_USER@$SERVER_IP:~/$PROJECT_NAME/
    
    # Copy environment file
    if [ -f ".env.production" ]; then
        scp .env.production $DEPLOY_USER@$SERVER_IP:~/$PROJECT_NAME/.env.production
    else
        log_warn "No .env.production file found. You'll need to create it on the server."
    fi
    
    # Deploy on server
    ssh $DEPLOY_USER@$SERVER_IP << EOF
        cd ~/$PROJECT_NAME
        
        # Stop existing containers
        docker-compose -f $DOCKER_COMPOSE_FILE down || true
        
        # Pull latest images and build
        docker-compose -f $DOCKER_COMPOSE_FILE pull
        docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache
        
        # Start services
        docker-compose -f $DOCKER_COMPOSE_FILE up -d
        
        # Show status
        docker-compose -f $DOCKER_COMPOSE_FILE ps
        
        echo "Deployment completed ✓"
EOF
    
    log_info "Application deployment completed ✓"
}

# Setup SSL certificates
setup_ssl() {
    if [ -n "$DOMAIN" ]; then
        log_info "Setting up SSL certificates for $DOMAIN..."
        
        ssh $DEPLOY_USER@$SERVER_IP << EOF
            cd ~/$PROJECT_NAME
            
            # Install certbot
            sudo apt-get update
            sudo apt-get install -y certbot
            
            # Stop nginx temporarily
            docker-compose -f $DOCKER_COMPOSE_FILE stop frontend
            
            # Get SSL certificate
            sudo certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
            
            # Copy certificates to nginx directory
            sudo mkdir -p nginx/ssl
            sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/cert.pem
            sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/key.pem
            sudo chown -R $DEPLOY_USER:$DEPLOY_USER nginx/ssl
            
            # Restart frontend with SSL
            docker-compose -f $DOCKER_COMPOSE_FILE up -d frontend
            
            echo "SSL setup completed ✓"
EOF
        
        log_info "SSL certificates configured ✓"
    else
        log_warn "No domain specified. Skipping SSL setup."
        log_warn "You can set up SSL later by running: DOMAIN=your.domain.com ./scripts/deploy-hetzner.sh"
    fi
}

# Main deployment process
main() {
    echo "Starting deployment with the following configuration:"
    echo "- Server IP: $SERVER_IP"
    echo "- Domain: ${DOMAIN:-'Not specified (HTTP only)'}"
    echo "- Deploy User: $DEPLOY_USER"
    echo ""
    
    read -p "Continue with deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Deployment cancelled."
        exit 0
    fi
    
    check_requirements
    setup_server
    deploy_application
    setup_ssl
    
    echo ""
    log_info "🎉 Deployment completed successfully!"
    echo ""
    echo "Your Sensor API platform is now running at:"
    if [ -n "$DOMAIN" ]; then
        echo "- Frontend: https://$DOMAIN"
        echo "- API: https://$DOMAIN/api/"
        echo "- GraphQL: https://$DOMAIN/graphql"
        echo "- Docs: https://$DOMAIN/docs"
    else
        echo "- Frontend: http://$SERVER_IP"
        echo "- API: http://$SERVER_IP/api/"
        echo "- GraphQL: http://$SERVER_IP/graphql"
        echo "- Docs: http://$SERVER_IP/docs"
    fi
    echo ""
    echo "Useful commands:"
    echo "- Check status: ssh $DEPLOY_USER@$SERVER_IP 'cd $PROJECT_NAME && docker-compose -f $DOCKER_COMPOSE_FILE ps'"
    echo "- View logs: ssh $DEPLOY_USER@$SERVER_IP 'cd $PROJECT_NAME && docker-compose -f $DOCKER_COMPOSE_FILE logs -f'"
    echo "- Update: Re-run this script with the same parameters"
    echo ""
}

# Run main function
main