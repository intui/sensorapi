#!/bin/bash

# Hetzner Server Management Script
# Provides common management commands for the deployed Sensor API

set -e

SERVER_IP=${SERVER_IP:-""}
DEPLOY_USER=${DEPLOY_USER:-"sensor"}
PROJECT_NAME="sensorapi"
DOCKER_COMPOSE_FILE="docker-compose.production.yml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if server IP is provided
check_server() {
    if [ -z "$SERVER_IP" ]; then
        log_error "SERVER_IP environment variable is required"
        echo "Usage: SERVER_IP=your.server.ip ./scripts/manage-hetzner.sh [command]"
        exit 1
    fi
}

# Show deployment status
status() {
    log_info "Checking deployment status on $SERVER_IP..."
    ssh $DEPLOY_USER@$SERVER_IP "cd $PROJECT_NAME && docker-compose -f $DOCKER_COMPOSE_FILE ps"
}

# Show logs
logs() {
    local service=${1:-""}
    if [ -n "$service" ]; then
        log_info "Showing logs for service: $service"
        ssh $DEPLOY_USER@$SERVER_IP "cd $PROJECT_NAME && docker-compose -f $DOCKER_COMPOSE_FILE logs -f $service"
    else
        log_info "Showing logs for all services (use Ctrl+C to exit)"
        ssh $DEPLOY_USER@$SERVER_IP "cd $PROJECT_NAME && docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
    fi
}

# Restart services
restart() {
    local service=${1:-""}
    if [ -n "$service" ]; then
        log_info "Restarting service: $service"
        ssh $DEPLOY_USER@$SERVER_IP "cd $PROJECT_NAME && docker-compose -f $DOCKER_COMPOSE_FILE restart $service"
    else
        log_info "Restarting all services..."
        ssh $DEPLOY_USER@$SERVER_IP "cd $PROJECT_NAME && docker-compose -f $DOCKER_COMPOSE_FILE restart"
    fi
}

# Update deployment
update() {
    log_info "Updating deployment on $SERVER_IP..."
    ssh $DEPLOY_USER@$SERVER_IP << EOF
        cd $PROJECT_NAME
        git pull
        docker-compose -f $DOCKER_COMPOSE_FILE pull
        docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache
        docker-compose -f $DOCKER_COMPOSE_FILE up -d
        docker system prune -f
EOF
    log_info "Update completed ✓"
}

# Backup database
backup() {
    local backup_name="sensorapi_backup_$(date +%Y%m%d_%H%M%S).sql"
    log_info "Creating database backup: $backup_name"
    ssh $DEPLOY_USER@$SERVER_IP << EOF
        cd $PROJECT_NAME
        docker-compose -f $DOCKER_COMPOSE_FILE exec -T db pg_dump -U sensorapi sensorapi > backups/$backup_name
        echo "Backup created: backups/$backup_name"
EOF
}

# Restore database from backup
restore() {
    local backup_file=${1:-""}
    if [ -z "$backup_file" ]; then
        log_error "Backup file name is required"
        echo "Usage: ./manage-hetzner.sh restore backup_file.sql"
        exit 1
    fi
    
    log_warn "This will replace the current database. Are you sure? (y/N)"
    read -r response
    if [[ ! $response =~ ^[Yy]$ ]]; then
        log_info "Restore cancelled."
        exit 0
    fi
    
    log_info "Restoring database from: $backup_file"
    ssh $DEPLOY_USER@$SERVER_IP << EOF
        cd $PROJECT_NAME
        docker-compose -f $DOCKER_COMPOSE_FILE exec -T db dropdb -U sensorapi sensorapi || true
        docker-compose -f $DOCKER_COMPOSE_FILE exec -T db createdb -U sensorapi sensorapi
        docker-compose -f $DOCKER_COMPOSE_FILE exec -T db psql -U sensorapi sensorapi < backups/$backup_file
EOF
    log_info "Restore completed ✓"
}

# Monitor system resources
monitor() {
    log_info "System monitoring for $SERVER_IP"
    ssh $DEPLOY_USER@$SERVER_IP << 'EOF'
        echo "=== System Resources ==="
        echo "CPU and Memory:"
        top -bn1 | head -5
        echo ""
        echo "Disk Usage:"
        df -h
        echo ""
        echo "=== Docker Resources ==="
        docker stats --no-stream
        echo ""
        echo "=== Service Health ==="
        cd sensorapi
        docker-compose -f docker-compose.production.yml ps
EOF
}

# Shell access
shell() {
    local service=${1:-"api"}
    log_info "Opening shell in $service container..."
    ssh -t $DEPLOY_USER@$SERVER_IP "cd $PROJECT_NAME && docker-compose -f $DOCKER_COMPOSE_FILE exec $service /bin/bash"
}

# Show help
help() {
    echo "Hetzner Server Management Script"
    echo "================================"
    echo ""
    echo "Usage: SERVER_IP=your.server.ip ./scripts/manage-hetzner.sh [command]"
    echo ""
    echo "Commands:"
    echo "  status              Show deployment status"
    echo "  logs [service]      Show logs (all services or specific service)"
    echo "  restart [service]   Restart services (all or specific service)"
    echo "  update              Update deployment from git"
    echo "  backup              Create database backup"
    echo "  restore <file>      Restore database from backup"
    echo "  monitor             Show system resources and health"
    echo "  shell [service]     Open shell in container (default: api)"
    echo "  help                Show this help message"
    echo ""
    echo "Services: api, frontend, db, redis"
    echo ""
    echo "Examples:"
    echo "  SERVER_IP=1.2.3.4 ./scripts/manage-hetzner.sh status"
    echo "  SERVER_IP=1.2.3.4 ./scripts/manage-hetzner.sh logs api"
    echo "  SERVER_IP=1.2.3.4 ./scripts/manage-hetzner.sh restart frontend"
    echo "  SERVER_IP=1.2.3.4 ./scripts/manage-hetzner.sh backup"
}

# Main command dispatcher
main() {
    local command=${1:-"help"}
    
    case $command in
        status)
            check_server
            status
            ;;
        logs)
            check_server
            logs $2
            ;;
        restart)
            check_server
            restart $2
            ;;
        update)
            check_server
            update
            ;;
        backup)
            check_server
            backup
            ;;
        restore)
            check_server
            restore $2
            ;;
        monitor)
            check_server
            monitor
            ;;
        shell)
            check_server
            shell $2
            ;;
        help|--help|-h)
            help
            ;;
        *)
            log_error "Unknown command: $command"
            echo ""
            help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"