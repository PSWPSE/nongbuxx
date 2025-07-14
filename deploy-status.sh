#!/bin/bash

# NONGBUXX 배포 상태 확인 스크립트

echo "📊 NONGBUXX 배포 상태 확인"
echo "========================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_color() {
    printf "${2}${1}${NC}\n"
}

cd frontend

print_color "🔍 현재 배포 상태:" $BLUE
vercel list

print_color "" $NC
print_color "📋 최근 배포 로그:" $BLUE
vercel logs --limit 10

print_color "" $NC
print_color "🌐 라이브 사이트:" $GREEN
print_color "   https://nongbuxxfrontend.vercel.app/" $GREEN

cd .. 