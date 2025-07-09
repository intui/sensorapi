#!/bin/bash

# Vercel Deployment Script
echo "🚀 Deploying Sensor API to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Login to Vercel (if not already logged in)
echo "🔑 Checking Vercel authentication..."
vercel whoami || vercel login

# Set up environment variables (if not already set)
echo "⚙️ Setting up environment variables..."
echo "Please make sure you have set the following environment variables in Vercel:"
echo "- DATABASE_URL"
echo "- SECRET_KEY"
echo "- ENVIRONMENT=production"
echo "- DEBUG=false"
echo ""
echo "You can set them via:"
echo "vercel env add DATABASE_URL"
echo "vercel env add SECRET_KEY"
echo "etc."
echo ""

read -p "Have you set up the environment variables? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please set up environment variables first."
    exit 1
fi

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

echo "✅ Deployment completed!"
echo "🌐 Your API should be available at the URL shown above"
echo "📚 Visit /docs for API documentation"
echo "🔍 Visit /graphql for GraphQL playground"
