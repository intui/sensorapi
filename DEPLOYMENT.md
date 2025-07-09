# Deployment Guide

This guide covers deploying the Sensor API to both Vercel and Azure.

## 🚀 Vercel Deployment

Vercel is great for FastAPI applications and offers excellent performance with global CDN.

### Prerequisites
- Vercel account
- PostgreSQL database (Aiven, Supabase, or Vercel Postgres)
- GitHub repository

### Steps

1. **Prepare your database**:
   - Your existing Aiven PostgreSQL database will work perfectly
   - Make sure your database allows external connections
   - Note your connection string

2. **Configure environment variables**:
   Create these environment variables in Vercel dashboard:
   ```
   DATABASE_URL=postgresql://username:password@host:port/database
   SECRET_KEY=your-secret-key-here
   ENVIRONMENT=production
   DEBUG=false
   ```

3. **Deploy to Vercel**:
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Login to Vercel
   vercel login
   
   # Deploy
   vercel --prod
   ```

4. **Set up domain** (optional):
   - Configure custom domain in Vercel dashboard
   - Update CORS settings in main.py if needed

### Vercel-specific files created:
- `vercel.json` - Vercel configuration
- `requirements-vercel.txt` - Streamlined dependencies for Vercel

## ☁️ Azure Deployment

Azure offers more control and is excellent for enterprise applications.

### Option 1: Azure Container Apps (Recommended)

#### Prerequisites
- Azure account
- Azure CLI installed
- Docker installed

#### Steps

1. **Containerize the application**:
   ```bash
   # Build Docker image
   docker build -t sensorapi .
   
   # Test locally
   docker run -p 8000:8000 --env-file .env sensorapi
   ```

2. **Deploy to Azure Container Apps**:
   ```bash
   # Login to Azure
   az login
   
   # Create resource group
   az group create --name sensor-api-rg --location eastus
   
   # Create container app environment
   az containerapp env create \
     --name sensor-api-env \
     --resource-group sensor-api-rg \
     --location eastus
   
   # Create container app
   az containerapp create \
     --name sensor-api \
     --resource-group sensor-api-rg \
     --environment sensor-api-env \
     --image sensorapi \
     --target-port 8000 \
     --ingress external \
     --env-vars \
       DATABASE_URL="your-database-url" \
       SECRET_KEY="your-secret-key"
   ```

### Option 2: Azure App Service

1. **Create App Service**:
   ```bash
   # Create App Service plan
   az appservice plan create \
     --name sensor-api-plan \
     --resource-group sensor-api-rg \
     --sku B1 \
     --is-linux
   
   # Create web app
   az webapp create \
     --resource-group sensor-api-rg \
     --plan sensor-api-plan \
     --name sensor-api-webapp \
     --runtime "PYTHON|3.11"
   
   # Configure startup command
   az webapp config set \
     --resource-group sensor-api-rg \
     --name sensor-api-webapp \
     --startup-file "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
   ```

2. **Deploy code**:
   ```bash
   # Deploy from local Git
   az webapp deployment source config-local-git \
     --name sensor-api-webapp \
     --resource-group sensor-api-rg
   
   # Push code
   git remote add azure <deployment-url>
   git push azure main
   ```

## 🏁 Quick Start Recommendations

### For Development/Prototyping: **Vercel**
- ✅ Fastest deployment (2 minutes)
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Great developer experience
- ✅ Free tier available

### For Production/Enterprise: **Azure**
- ✅ More control and customization
- ✅ Better for complex enterprise needs
- ✅ Integration with Azure services
- ✅ More deployment options
- ✅ Better monitoring and logging

## 🔧 Post-Deployment Setup

1. **Run database migrations**:
   ```bash
   # For Vercel (via Vercel CLI)
   vercel env pull
   python -m alembic upgrade head
   
   # For Azure (via Azure CLI or portal)
   az webapp ssh --name sensor-api-webapp --resource-group sensor-api-rg
   python -m alembic upgrade head
   ```

2. **Create sample data** (optional):
   ```bash
   python scripts/create_sample_data.py
   ```

3. **Test the deployment**:
   - Visit `/docs` for FastAPI documentation
   - Visit `/graphql` for GraphQL playground
   - Test a simple query

## 🌍 Environment Variables

Make sure to set these in your deployment platform:

```env
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-super-secret-key-here
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=["https://yourdomain.com"]
```

## 📊 Monitoring

### Vercel
- Built-in analytics in Vercel dashboard
- Function logs available
- Performance monitoring included

### Azure
- Application Insights for monitoring
- Log Analytics for detailed logging
- Azure Monitor for alerts

Choose the platform that best fits your needs! Vercel is perfect for getting started quickly, while Azure offers more enterprise-grade features.
