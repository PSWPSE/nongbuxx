#!/bin/bash

# NONGBUXX Vercel Frontend Deployment Script
# Vercel 프론트엔드 배포를 위한 자동화 스크립트

set -e

echo "🌐 NONGBUXX Vercel Frontend Deployment"
echo "======================================"

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

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    print_color "❌ Vercel CLI is not installed." $RED
    print_color "📦 Installing Vercel CLI..." $BLUE
    npm install -g vercel
fi

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    print_color "❌ Frontend directory not found." $RED
    print_color "Please run this script from the project root directory." $RED
    exit 1
fi

# Move to frontend directory
cd frontend

# Check if user is logged in to Vercel
print_color "🔑 Checking Vercel authentication..." $BLUE
if ! vercel whoami &> /dev/null; then
    print_color "Please login to Vercel:" $YELLOW
    vercel login
fi

# Get Railway backend URL for configuration
print_color "🔧 Configuring API connection..." $BLUE

RAILWAY_URL=""
if [ -f "../.railway" ]; then
    print_color "Detecting Railway backend URL..." $BLUE
    cd ..
    RAILWAY_URL=$(railway url 2>/dev/null || echo "")
    cd frontend
fi

if [ -z "$RAILWAY_URL" ]; then
    print_color "⚠️  Railway backend URL not detected." $YELLOW
    read -p "Enter your Railway backend URL (e.g., https://your-app.railway.app): " RAILWAY_URL
fi

# Update config.js with Railway URL
if [ ! -z "$RAILWAY_URL" ]; then
    print_color "📝 Updating frontend configuration..." $BLUE
    cat > config.js << EOF
// Configuration for environment variables
window.ENV = {
  API_BASE_URL: window.location.hostname === 'localhost' 
    ? 'http://localhost:8080' 
    : '$RAILWAY_URL'
};
EOF
    print_color "✅ Configuration updated with backend URL: $RAILWAY_URL" $GREEN
fi

# Deploy to Vercel
print_color "🚀 Deploying to Vercel..." $BLUE

# Check if this is the first deployment
if [ ! -f ".vercel/project.json" ]; then
    print_color "🆕 First-time deployment detected." $BLUE
    print_color "📋 Please configure your project:" $YELLOW
    print_color "   - Project name: nongbuxx-frontend" $BLUE
    print_color "   - Framework: Other (or skip)" $BLUE
    print_color "   - Root directory: . (current)" $BLUE
    print_color "" $NC
fi

# Deploy to production
vercel --prod

# Get deployment URL
print_color "📡 Getting deployment information..." $BLUE
VERCEL_URL=$(vercel ls | grep "nongbuxx" | head -n 1 | awk '{print $2}' || echo "Check Vercel dashboard")

print_color "✅ Frontend deployment completed!" $GREEN
print_color "" $NC
print_color "🌐 Your frontend is deployed at:" $BLUE
print_color "   https://$VERCEL_URL" $GREEN
print_color "" $NC
print_color "🔗 Full application URLs:" $BLUE
print_color "   Frontend: https://$VERCEL_URL" $GREEN
print_color "   Backend:  $RAILWAY_URL" $GREEN
print_color "" $NC
print_color "🔍 Test your deployment:" $BLUE
print_color "   1. Open https://$VERCEL_URL in browser" $YELLOW
print_color "   2. Enter a news URL and test content generation" $YELLOW
print_color "" $NC
print_color "📊 Monitor your deployment:" $BLUE
print_color "   vercel logs" $YELLOW
print_color "   vercel status" $YELLOW
print_color "" $NC
print_color "🎉 Complete deployment finished!" $GREEN
print_color "🚀 Your NONGBUXX service is now live!" $GREEN

# Return to root directory
cd ..

print_color "" $NC
print_color "📋 Next steps:" $BLUE
print_color "   1. Set up custom domain (optional)" $YELLOW
print_color "   2. Configure monitoring and analytics" $YELLOW
print_color "   3. Set up CI/CD for automatic deployments" $YELLOW 