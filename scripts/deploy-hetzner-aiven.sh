#!/bin/bash

# Hetzner Docker Deployment Script for Sensor API with Aiven Database
# This script deploys the Sensor API platform to a Hetzner server using Docker with external Aiven database

set -e

echo "🚀 Hetzner Docker Deployment - Sensor API Platform (Aiven Database)"
echo "=================================================================="
echo ""

# Configuration
DEPLOY_USER=${DEPLOY_USER:-"sensor"}
SERVER_IP=${SERVER_IP:-""}
DOMAIN=${DOMAIN:-""}
PROJECT_NAME="sensorapi"
DOCKER_COMPOSE_FILE="docker-compose.aiven.yml"

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
        echo "Usage: SERVER_IP=your.server.ip DOMAIN=your.domain.com ./scripts/deploy-hetzner-aiven.sh"
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
    
    if [ ! -f ".env.production" ]; then
        log_error ".env.production file not found"
        echo "Please create .env.production with your Aiven database configuration"
        exit 1
    fi
    
    log_info "Requirements check passed ✓"
}

# Setup server dependencies
setup_server() {
    log_info "Setting up server dependencies on $SERVER_IP (Docker CE App Image + Aiven DB)..."
    
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
        
        echo "✅ Server setup completed - Docker CE with Aiven database ready"
EOF
    
    log_info "Server setup completed ✓"
}

# Deploy application
deploy_application() {
    log_info "Deploying application to $SERVER_IP (using Aiven database)..."
    
    # Create deployment directory on server
    ssh $DEPLOY_USER@$SERVER_IP "mkdir -p ~/$PROJECT_NAME"
    
    # Copy application files
    log_info "Copying application files..."
    scp -r . $DEPLOY_USER@$SERVER_IP:~/$PROJECT_NAME/
    
    # Copy environment file
    if [ -f ".env.production" ]; then
        scp .env.production $DEPLOY_USER@$SERVER_IP:~/$PROJECT_NAME/.env.production
        log_info "Copied production environment with Aiven database configuration ✓"
    else
        log_error "No .env.production file found!"
        exit 1
    fi
    
    # Deploy on server
    ssh $DEPLOY_USER@$SERVER_IP << EOF
        cd ~/$PROJECT_NAME
        
        # Stop existing containers
        docker-compose -f $DOCKER_COMPOSE_FILE down || true
        
        # Pull latest images and build
        docker-compose -f $DOCKER_COMPOSE_FILE pull
        docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache
        
        # Start services (no local database needed - using Aiven)
        docker-compose -f $DOCKER_COMPOSE_FILE up -d
        
        # Show status
        docker-compose -f $DOCKER_COMPOSE_FILE ps
        
        # Test database connection
        echo "Testing Aiven database connection..."
        docker-compose -f $DOCKER_COMPOSE_FILE exec -T api python -c "
import asyncio
import os
import asyncpg

async def test_db():
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        result = await conn.fetchval('SELECT version()')
        print(f'✅ Aiven database connected: {result[:50]}...')
        await conn.close()
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        
asyncio.run(test_db())
        " || echo "⚠️ Database test failed - check your Aiven configuration"
        
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
            
            # Update ALLOWED_ORIGINS in .env.production
            sed -i "s|ALLOWED_ORIGINS=.*|ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN|" .env.production
            
            # Restart frontend with SSL
            docker-compose -f $DOCKER_COMPOSE_FILE up -d frontend
            
            echo "SSL setup completed ✓"
EOF
        
        log_info "SSL certificates configured ✓"
    else
        log_warn "No domain specified. Using HTTP only."
        log_warn "You can add SSL later by running: DOMAIN=your.domain.com $0"
    fi
}

# Main deployment process
main() {
    echo "Starting deployment with the following configuration:"
    echo "- Server IP: $SERVER_IP"
    echo "- Domain: ${DOMAIN:-'Not specified (HTTP only)'}"
    echo "- Deploy User: $DEPLOY_USER"
    echo "- Database: Aiven PostgreSQL (external)"
    echo "- Services: API + Frontend + Redis (no local database)"
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
        echo "- Health: https://$DOMAIN/health"
    else
        echo "- Frontend: http://$SERVER_IP"
        echo "- API: http://$SERVER_IP/api/"
        echo "- GraphQL: http://$SERVER_IP/graphql"
        echo "- Docs: http://$SERVER_IP/docs"
        echo "- Health: http://$SERVER_IP/health"
    fi
    echo ""
    echo "Database: Using your existing Aiven PostgreSQL instance ✅"
    echo ""
    echo "Useful commands:"
    echo "- Check status: ssh $DEPLOY_USER@$SERVER_IP 'cd $PROJECT_NAME && docker-compose -f $DOCKER_COMPOSE_FILE ps'"
    echo "- View logs: ssh $DEPLOY_USER@$SERVER_IP 'cd $PROJECT_NAME && docker-compose -f $DOCKER_COMPOSE_FILE logs -f'"
    echo "- Update: Re-run this script with the same parameters"
    echo ""
}

# Run main function
main