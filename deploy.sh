#!/bin/bash

# NONGBUXX Web Application Deployment Script
# This script helps you deploy the NONGBUXX web application using Docker

set -e

echo "🚀 NONGBUXX Web Application Deployment Script"
echo "=============================================="

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_color "Checking prerequisites..." $BLUE

if ! command_exists docker; then
    print_color "❌ Docker is not installed. Please install Docker first." $RED
    exit 1
fi

if ! command_exists docker-compose; then
    print_color "❌ Docker Compose is not installed. Please install Docker Compose first." $RED
    exit 1
fi

print_color "✅ Docker and Docker Compose are installed." $GREEN

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_color "⚠️  .env file not found. Creating from template..." $YELLOW
    
    if [ -f "env.example" ]; then
        cp env.example .env
        print_color "📋 .env file created from template." $GREEN
        print_color "🔧 Please edit .env file and add your API keys:" $YELLOW
        print_color "   - ANTHROPIC_API_KEY" $YELLOW
        print_color "   - OPENAI_API_KEY" $YELLOW
        print_color "" $NC
        read -p "Press Enter after editing .env file..."
    else
        print_color "❌ env.example file not found. Please create .env file manually." $RED
        exit 1
    fi
fi

# Validate API keys
print_color "Validating API keys..." $BLUE

source .env

if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    print_color "❌ No API keys found. Please set either ANTHROPIC_API_KEY or OPENAI_API_KEY in .env file." $RED
    exit 1
fi

if [ "$ANTHROPIC_API_KEY" = "your_anthropic_api_key_here" ] && [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    print_color "❌ Please replace placeholder API keys with actual keys in .env file." $RED
    exit 1
fi

print_color "✅ API keys validated." $GREEN

# Create necessary directories
print_color "Creating necessary directories..." $BLUE
mkdir -p generated_content uploads
print_color "✅ Directories created." $GREEN

# Build and start the application
print_color "Building and starting the application..." $BLUE

# Stop existing containers if any
docker-compose down 2>/dev/null || true

# Build and start
docker-compose up --build -d

print_color "✅ Application started successfully!" $GREEN

# Wait for application to be ready
print_color "Waiting for application to be ready..." $BLUE
sleep 10

# Check if application is running
if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
    print_color "✅ Application is running and healthy!" $GREEN
    print_color "" $NC
    print_color "🎉 NONGBUXX Web Application is now running!" $GREEN
    print_color "🌐 Access the application at: http://localhost:5000" $BLUE
    print_color "📊 API health check: http://localhost:5000/api/health" $BLUE
    print_color "" $NC
    print_color "📝 To stop the application, run: docker-compose down" $YELLOW
    print_color "🔧 To view logs, run: docker-compose logs -f" $YELLOW
else
    print_color "❌ Application failed to start properly." $RED
    print_color "🔍 Check logs with: docker-compose logs" $YELLOW
    exit 1
fi

print_color "" $NC
print_color "Deployment completed successfully! 🚀" $GREEN 