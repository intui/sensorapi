# Hetzner Docker Deployment Guide

This guide explains how to deploy the Sensor API platform to a Hetzner server using Docker containers.

## Overview

The deployment includes:

- **Frontend**: React application served by Nginx with SSL
- **Backend API**: FastAPI application with GraphQL
- **Database**: PostgreSQL 15 with optimizations
- **Cache**: Redis for session management and caching
- **Reverse Proxy**: Nginx with SSL termination and load balancing

## Prerequisites

### Local Requirements

- SSH access to your Hetzner server
- SSH key-based authentication configured
- Git repository access

### Server Requirements

- Ubuntu 20.04+ or Debian 11+ (recommended)
- At least 2GB RAM, 2 CPU cores
- 20GB+ storage space
- Root access for initial setup

## Quick Deployment

### 1. Environment Setup

Copy the production environment template:

```bash
cp .env.production.example .env.production
```

Edit `.env.production` with your actual values:

```bash
# Database Configuration
DATABASE_URL=postgresql://sensorapi:your_secure_db_password@db:5432/sensorapi
DB_PASSWORD=your_secure_db_password

# Application Security
SECRET_KEY=your_very_secure_secret_key_here_at_least_32_characters

# CORS Configuration
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. Deploy to Server

Run the deployment script:

```bash
# Basic deployment (HTTP only)
SERVER_IP=your.server.ip ./scripts/deploy-hetzner.sh

# With SSL certificate
SERVER_IP=your.server.ip DOMAIN=yourdomain.com ./scripts/deploy-hetzner.sh
```

The script will:

1. Setup Docker and dependencies on the server
2. Create deployment user and configure security
3. Copy application files to the server
4. Build and start all containers
5. Configure SSL certificates (if domain provided)

## Manual Deployment Steps

If you prefer manual deployment or need to customize the process:

### Server Requirements

**Recommended: Use Hetzner's Docker CE App Image**

- Faster deployment (Docker pre-installed)
- Optimized Docker configuration
- Better stability and performance

**Alternative: Ubuntu/Debian Base Image**

- More control over system configuration
- Requires manual Docker installation

### 1. Server Preparation

**Option A: Docker CE App Image (Recommended)**

If you used Hetzner's Docker CE app image, connect to your server and run:

```bash
# Update system (Docker already installed)
apt-get update && apt-get upgrade -y

# Verify Docker installation
docker --version
docker-compose --version

# Create deployment user
useradd -m -s /bin/bash sensor
usermod -aG docker sensor

# Install additional tools
apt-get install -y nginx-utils htop curl wget git ufw

# Setup firewall
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable
```

**Option B: Ubuntu/Debian Base Image**

If you used a base OS image, connect to your server and run:

```bash
# Update system
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create deployment user
useradd -m -s /bin/bash sensor
usermod -aG docker sensor

# Setup firewall
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable
```

### 2. Application Deployment

Copy files to server:

```bash
# Copy application files
scp -r . sensor@your.server.ip:~/sensorapi/

# Copy environment configuration
scp .env.production sensor@your.server.ip:~/sensorapi/.env.production
```

Deploy on server:

```bash
ssh sensor@your.server.ip
cd sensorapi

# Start services
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps
```

### 3. SSL Certificate Setup

For HTTPS support with Let's Encrypt:

```bash
# Install certbot
sudo apt-get install -y certbot

# Stop nginx temporarily
docker-compose -f docker-compose.production.yml stop frontend

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
sudo chown -R sensor:sensor nginx/ssl

# Restart frontend with SSL
docker-compose -f docker-compose.production.yml up -d frontend
```

## Management Commands

Use the management script for common operations:

```bash
# Check deployment status
SERVER_IP=your.server.ip ./scripts/manage-hetzner.sh status

# View logs
SERVER_IP=your.server.ip ./scripts/manage-hetzner.sh logs
SERVER_IP=your.server.ip ./scripts/manage-hetzner.sh logs api

# Restart services
SERVER_IP=your.server.ip ./scripts/manage-hetzner.sh restart
SERVER_IP=your.server.ip ./scripts/manage-hetzner.sh restart frontend

# Update deployment
SERVER_IP=your.server.ip ./scripts/manage-hetzner.sh update

# Database backup
SERVER_IP=your.server.ip ./scripts/manage-hetzner.sh backup

# System monitoring
SERVER_IP=your.server.ip ./scripts/manage-hetzner.sh monitor

# Access container shell
SERVER_IP=your.server.ip ./scripts/manage-hetzner.sh shell api
```

## Architecture Details

### Container Services

| Service | Port | Description |
|---------|------|-------------|
| frontend | 80, 443 | Nginx serving React app with SSL |
| api | 8000 | FastAPI backend with GraphQL |
| db | 5432 | PostgreSQL database |
| redis | 6379 | Redis cache and sessions |

### Data Persistence

- **PostgreSQL Data**: `postgres_data` volume
- **Redis Data**: `redis_data` volume
- **SSL Certificates**: `nginx/ssl/` directory

### Network Configuration

All services communicate through a dedicated `sensor_network` bridge network for isolation and security.

## Security Features

### Application Security

- Non-root container users
- Secret management via environment variables
- CORS protection
- Security headers in Nginx

### Server Security

- UFW firewall configured
- SSL/TLS encryption
- Database password protection
- Container isolation

### Monitoring

- Health checks for all services
- Container resource monitoring
- Log aggregation

## Troubleshooting

### Common Issues

**Container fails to start:**

```bash
# Check logs
docker-compose -f docker-compose.production.yml logs service_name

# Check resource usage
docker stats
```

**Database connection issues:**

```bash
# Test database connectivity
docker-compose -f docker-compose.production.yml exec api python -c "
import asyncpg
import asyncio
async def test():
    conn = await asyncpg.connect('postgresql://sensorapi:password@db:5432/sensorapi')
    print('Database connected successfully')
    await conn.close()
asyncio.run(test())
"
```

**SSL certificate issues:**

```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew

# Update nginx certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/*.pem nginx/ssl/
docker-compose -f docker-compose.production.yml restart frontend
```

### Performance Tuning

**Increase worker processes:**
Update `docker-compose.production.yml`:

```yaml
api:
  command: python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 8
```

**Database optimization:**

```sql
-- Connect to database and run
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
SELECT pg_reload_conf();
```

## Backup and Recovery

### Automated Backups

Create a cron job for regular backups:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /home/sensor/sensorapi && /usr/local/bin/docker-compose -f docker-compose.production.yml exec -T db pg_dump -U sensorapi sensorapi > backups/daily_$(date +\%Y\%m\%d).sql
```

### Recovery Process

```bash
# Stop API to prevent writes
docker-compose -f docker-compose.production.yml stop api

# Restore database
docker-compose -f docker-compose.production.yml exec -T db psql -U sensorapi sensorapi < backups/backup_file.sql

# Restart API
docker-compose -f docker-compose.production.yml start api
```

## Cost Optimization

### Hetzner Server Recommendations

| Use Case | Server Type | Monthly Cost |
|----------|-------------|--------------|
| Development | CX11 (1vCPU, 2GB) | €3.29 |
| Small Production | CX21 (2vCPU, 4GB) | €5.83 |
| Medium Production | CX31 (2vCPU, 8GB) | €10.52 |
| High Traffic | CX41 (4vCPU, 16GB) | €20.16 |

### Resource Monitoring

Monitor resource usage and scale appropriately:

```bash
# Check server resources
htop
df -h
docker stats

# Monitor application metrics
curl http://localhost:8000/health
```

## Updating the Deployment

### Code Updates

```bash
# Pull latest code and redeploy
SERVER_IP=your.server.ip ./scripts/manage-hetzner.sh update
```

### Configuration Updates

```bash
# Update environment variables
scp .env.production sensor@your.server.ip:~/sensorapi/
ssh sensor@your.server.ip "cd sensorapi && docker-compose -f docker-compose.production.yml restart"
```

### Database Migrations

```bash
# Run database migrations
ssh sensor@your.server.ip "cd sensorapi && docker-compose -f docker-compose.production.yml exec api alembic upgrade head"
```

## Support

For issues specific to this deployment:

1. Check service logs: `./scripts/manage-hetzner.sh logs`
2. Monitor system resources: `./scripts/manage-hetzner.sh monitor`
3. Review container health: `./scripts/manage-hetzner.sh status`

For application issues, refer to the main project documentation.
