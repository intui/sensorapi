#!/bin/bash

# Azure Container Apps Deployment Script
echo "☁️ Deploying Sensor API to Azure Container Apps..."

# Configuration
RESOURCE_GROUP="sensor-api-rg"
LOCATION="eastus"
ENVIRONMENT_NAME="sensor-api-env"
APP_NAME="sensor-api"
CONTAINER_IMAGE="sensorapi:latest"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install it first."
    echo "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Login to Azure (if not already logged in)
echo "🔑 Checking Azure authentication..."
az account show || az login

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t $CONTAINER_IMAGE .

# Create resource group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create container app environment
echo "🌍 Creating container app environment..."
az containerapp env create \
    --name $ENVIRONMENT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

# Get environment variables
echo "⚙️ Please provide the following environment variables:"
read -p "DATABASE_URL: " DATABASE_URL
read -p "SECRET_KEY: " SECRET_KEY

# Create container app
echo "🚀 Creating container app..."
az containerapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $ENVIRONMENT_NAME \
    --image $CONTAINER_IMAGE \
    --target-port 8000 \
    --ingress external \
    --env-vars \
        DATABASE_URL="$DATABASE_URL" \
        SECRET_KEY="$SECRET_KEY" \
        ENVIRONMENT=production \
        DEBUG=false

# Get the application URL
echo "✅ Deployment completed!"
APP_URL=$(az containerapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" -o tsv)
echo "🌐 Your API is available at: https://$APP_URL"
echo "📚 Visit https://$APP_URL/docs for API documentation"
echo "🔍 Visit https://$APP_URL/graphql for GraphQL playground"
