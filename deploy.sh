#!/bin/bash

# Quick Deployment Guide
echo "🚀 Sensor API - Quick Deployment Guide"
echo "======================================"
echo ""

echo "Choose your deployment platform:"
echo "1) Vercel (Fast, easy, great for prototypes)"
echo "2) Azure Container Apps (Production-ready, more control)"
echo "3) Hetzner Docker (Self-hosted, full control, cost-effective)"
echo "4) Local Docker testing"
echo "5) Exit"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🔄 Starting Vercel deployment..."
        ./scripts/deploy-vercel.sh
        ;;
    2)
        echo ""
        echo "☁️ Starting Azure deployment..."
        ./scripts/deploy-azure.sh
        ;;
    3)
        echo ""
        echo "🏗️ Starting Hetzner Docker deployment..."
        ./scripts/deploy-hetzner.sh
        ;;
    4)
        echo ""
        echo "🐳 Starting local Docker setup..."
        echo "Building and running with Docker Compose..."
        docker-compose up --build
        ;;
    5)
        echo "Goodbye! 👋"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac
