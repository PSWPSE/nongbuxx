#!/bin/bash

# NONGBUXX Railway Backend Deployment Script
# Railway 백엔드 배포를 위한 자동화 스크립트

set -e

echo "🚀 NONGBUXX Railway Backend Deployment"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    printf "${2}${1}${NC}\n"
}

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    print_color "❌ Railway CLI is not installed." $RED
    print_color "📦 Installing Railway CLI..." $BLUE
    npm install -g @railway/cli
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    print_color "🔑 Please login to Railway:" $YELLOW
    railway login
fi

# Check required environment variables
print_color "🔍 Checking API keys..." $BLUE

if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    print_color "⚠️  API keys not found in environment." $YELLOW
    print_color "🔧 You'll need to set them in Railway dashboard:" $BLUE
    print_color "   1. Go to your Railway project dashboard" $BLUE
    print_color "   2. Navigate to Variables tab" $BLUE
    print_color "   3. Add ANTHROPIC_API_KEY or OPENAI_API_KEY" $BLUE
    print_color "" $NC
    read -p "Press Enter when you've set the API keys in Railway dashboard..."
fi

# Create new Railway project or link existing
print_color "🔗 Setting up Railway project..." $BLUE

if [ ! -f "railway.json" ]; then
    print_color "Creating new Railway project..." $BLUE
    railway init
else
    print_color "Using existing Railway project..." $GREEN
fi

# Set environment variables in Railway
print_color "⚙️  Setting production environment variables..." $BLUE

railway variables --set "FLASK_ENV=production"
railway variables --set "PYTHONUNBUFFERED=1"
railway variables --set "DEBUG=False"

if [ ! -z "$ANTHROPIC_API_KEY" ]; then
    print_color "Setting ANTHROPIC_API_KEY..." $BLUE
    railway variables --set "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY"
fi

if [ ! -z "$OPENAI_API_KEY" ]; then
    print_color "Setting OPENAI_API_KEY..." $BLUE
    railway variables --set "OPENAI_API_KEY=$OPENAI_API_KEY"
fi

# Deploy to Railway
print_color "🚀 Deploying to Railway..." $BLUE
railway up

# Get the deployment URL
print_color "📡 Getting deployment URL..." $BLUE
RAILWAY_URL=$(railway url 2>/dev/null || echo "URL will be available after deployment")

print_color "✅ Deployment completed!" $GREEN
print_color "" $NC
print_color "🌐 Your backend is deployed at:" $BLUE
print_color "   $RAILWAY_URL" $GREEN
print_color "" $NC
print_color "🔍 Test your deployment:" $BLUE
print_color "   curl $RAILWAY_URL/api/health" $YELLOW
print_color "" $NC
print_color "📊 Monitor your deployment:" $BLUE
print_color "   railway logs" $YELLOW
print_color "   railway status" $YELLOW
print_color "" $NC
print_color "🎉 Backend deployment complete!" $GREEN
print_color "💡 Next: Deploy frontend to Vercel using ./deploy-vercel.sh" $BLUE 