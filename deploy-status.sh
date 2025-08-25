#!/bin/bash

# 🔍 NONGBUXX 배포 상태 확인 스크립트
# 현재 배포 상태를 한눈에 확인

set -e

echo "🔍 NONGBUXX 배포 상태 확인"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

print_color() {
    printf "${2}${1}${NC}\n"
}

print_section() {
    echo ""
    print_color "🔸 $1" $CYAN
    echo "----------------------------------------"
}

check_status() {
    local service=$1
    local url=$2
    local expected=$3
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected" ]; then
        print_color "✅ $service: 정상 작동 (HTTP $response)" $GREEN
        return 0
    else
        print_color "❌ $service: 응답 실패 (HTTP $response)" $RED
        return 1
    fi
}

check_api_function() {
    local response=$(curl -s -X POST https://nongbuxxbackend-production.up.railway.app/api/generate \
        -H "Content-Type: application/json" \
        -d '{"url":"test","api_provider":"anthropic","api_key":"sk-ant-test","content_type":"x"}' \
        2>/dev/null || echo "{}")
    
    if [[ "$response" == *"INVALID_URL"* ]] || [[ "$response" == *"INVALID_ANTHROPIC_KEY"* ]]; then
        print_color "✅ API 기능: 정상 작동 (최신 코드 반영)" $GREEN
        return 0
    elif [[ "$response" == *"INVALID_CONTENT_TYPE"* ]]; then
        print_color "❌ API 기능: 구버전 코드 (재배포 필요)" $RED
        return 1
    else
        print_color "⚠️  API 기능: 상태 불명 - 응답: ${response:0:100}..." $YELLOW
        return 1
    fi
}

# 현재 시간
print_color "📅 확인 시각: $(date '+%Y-%m-%d %H:%M:%S')" $BLUE

# Git 정보
print_section "Git 상태"
CURRENT_COMMIT=$(git rev-parse HEAD)
COMMIT_MESSAGE=$(git log -1 --pretty=format:"%s")
print_color "📌 현재 커밋: $CURRENT_COMMIT" $BLUE
print_color "💬 커밋 메시지: $COMMIT_MESSAGE" $NC

# 서비스 상태 확인
print_section "서비스 상태"

BACKEND_OK=false
FRONTEND_OK=false
API_FUNCTION_OK=false

# 백엔드 상태 확인
if check_status "백엔드" "https://nongbuxxbackend-production.up.railway.app/api/health" "200"; then
    BACKEND_OK=true
fi

# 프론트엔드 상태 확인  
if check_status "프론트엔드" "https://nongbuxxfrontend.vercel.app/" "200"; then
    FRONTEND_OK=true
fi

# API 기능 확인
if check_api_function; then
    API_FUNCTION_OK=true
fi

# Railway 상세 정보
print_section "Railway 백엔드 상세 정보"
if command -v railway >/dev/null 2>&1; then
    railway status 2>/dev/null || print_color "⚠️  Railway CLI 연결 실패" $YELLOW
    
    echo ""
    print_color "📋 최근 배포 로그:" $BLUE
    railway logs -n 10 | grep -E "(Deploy|Build|Success|Error|Failed)" || true
else
    print_color "⚠️  Railway CLI가 설치되지 않음" $YELLOW
fi

# Vercel 상세 정보
print_section "Vercel 프론트엔드 상세 정보"
if command -v vercel >/dev/null 2>&1; then
    cd frontend 2>/dev/null || echo "frontend 디렉토리 없음"
    vercel ls 2>/dev/null | head -5 || print_color "⚠️  Vercel CLI 연결 실패" $YELLOW
    cd .. 2>/dev/null || true
else
    print_color "⚠️  Vercel CLI가 설치되지 않음" $YELLOW
fi

# 전체 상태 요약
print_section "전체 상태 요약"

ALL_OK=true

if [ "$BACKEND_OK" = true ]; then
    print_color "🟢 백엔드: 정상" $GREEN
else
    print_color "🔴 백엔드: 문제" $RED
    ALL_OK=false
fi

if [ "$FRONTEND_OK" = true ]; then
    print_color "🟢 프론트엔드: 정상" $GREEN
else
    print_color "🔴 프론트엔드: 문제" $RED
    ALL_OK=false
fi

if [ "$API_FUNCTION_OK" = true ]; then
    print_color "🟢 API 기능: 정상" $GREEN
else
    print_color "🔴 API 기능: 문제" $RED
    ALL_OK=false
fi

echo ""
if [ "$ALL_OK" = true ]; then
    print_color "🎉 모든 서비스가 정상 작동 중입니다!" $BOLD$GREEN
else
    print_color "⚠️  일부 서비스에 문제가 있습니다." $BOLD$YELLOW
    echo ""
    print_color "🔧 문제 해결 방법:" $BLUE
    print_color "  1. ./deploy-all.sh \"fix: 배포 문제 해결\" (전체 재배포)" $NC
    print_color "  2. railway up --force (백엔드만 재배포)" $NC
    print_color "  3. ./deploy-quick.sh (프론트엔드만 재배포)" $NC
    print_color "  4. ./deploy-rollback.sh (이전 버전으로 롤백)" $NC
fi

echo ""
print_color "🌐 서비스 URL:" $BLUE
print_color "  • 프론트엔드: https://nongbuxxfrontend.vercel.app/" $NC
print_color "  • 백엔드 API: https://nongbuxxbackend-production.up.railway.app" $NC
print_color "  • API 헬스체크: https://nongbuxxbackend-production.up.railway.app/api/health" $NC
