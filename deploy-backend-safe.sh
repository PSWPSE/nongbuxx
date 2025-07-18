#!/bin/bash

# 🛡️ Railway 백엔드 안전 배포 스크립트
# Git 푸시, 배포, 검증까지 한 번에 처리

set -e

echo "🛡️ Railway 백엔드 안전 배포"
echo "==========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_color() {
    printf "${2}${1}${NC}\n"
}

# 1. 커밋 메시지 확인
if [ -z "$1" ]; then
    print_color "❌ 사용법: ./deploy-backend-safe.sh \"커밋 메시지\"" $RED
    exit 1
fi

COMMIT_MESSAGE="$1"

# 2. 로컬 테스트 확인
print_color "🧪 로컬 서버 테스트 중..." $BLUE
if curl -s http://localhost:8080/api/health | grep -q "healthy"; then
    print_color "✅ 로컬 서버 정상 작동 확인" $GREEN
else
    print_color "⚠️  로컬 서버가 실행되지 않았습니다. 테스트를 건너뜁니다." $YELLOW
fi

# 3. Git 상태 확인
print_color "📋 Git 상태 확인 중..." $BLUE
git status

# 4. Git 커밋 및 푸시
print_color "📤 Git 커밋 및 푸시 중..." $BLUE
git add .
git commit -m "$COMMIT_MESSAGE"
git push origin main

COMMIT_HASH=$(git rev-parse HEAD)
print_color "✅ 커밋 완료: $COMMIT_HASH" $GREEN

# 5. Railway 자동 배포 대기
print_color "⏳ Railway 자동 배포 대기 중 (2분)..." $YELLOW
print_color "   (Railway 대시보드에서 실시간 진행상황을 확인할 수 있습니다)" $NC

# 프로그레스 바 표시
for i in {1..24}; do
    printf "."
    sleep 5
done
echo ""

# 6. 배포 상태 확인
print_color "🔍 배포 상태 확인 중..." $BLUE

# 헬스체크
HEALTH_RESPONSE=$(curl -s https://nongbuxxbackend-production.up.railway.app/api/health || echo "Failed")

if [[ "$HEALTH_RESPONSE" == *"healthy"* ]]; then
    print_color "✅ 백엔드가 정상 작동 중입니다." $GREEN
else
    print_color "❌ 백엔드 헬스체크 실패!" $RED
    print_color "🔄 수동 배포를 시도합니다..." $YELLOW
    railway up --detach
    sleep 30
fi

# 7. 기능 테스트 (예: 최신 기능 확인)
print_color "🧪 배포된 기능 테스트 중..." $BLUE
TEST_RESPONSE=$(curl -s -X POST https://nongbuxxbackend-production.up.railway.app/api/generate \
    -H "Content-Type: application/json" \
    -d '{"url":"test","api_provider":"anthropic","api_key":"sk-ant-test","content_type":"x"}' \
    2>/dev/null || echo "{}")

if [[ "$TEST_RESPONSE" == *"INVALID_URL"* ]] || [[ "$TEST_RESPONSE" == *"INVALID_ANTHROPIC_KEY"* ]]; then
    print_color "✅ 최신 코드가 성공적으로 배포되었습니다!" $GREEN
    print_color "🎉 배포 완료!" $GREEN
    
    # 배포 요약
    echo ""
    print_color "📊 배포 요약:" $BLUE
    print_color "  • 커밋: $COMMIT_HASH" $NC
    print_color "  • 메시지: $COMMIT_MESSAGE" $NC
    print_color "  • 백엔드: https://nongbuxxbackend-production.up.railway.app" $NC
    print_color "  • 프론트엔드: https://nongbuxxfrontend.vercel.app" $NC
    
elif [[ "$TEST_RESPONSE" == *"INVALID_CONTENT_TYPE"* ]]; then
    print_color "❌ 배포는 되었지만 최신 코드가 반영되지 않았습니다!" $RED
    print_color "🔄 강제 재배포를 시도합니다..." $YELLOW
    railway up --force
    
    echo ""
    print_color "⏳ 재배포 대기 중 (1분)..." $YELLOW
    sleep 60
    
    # 재테스트
    TEST_RESPONSE2=$(curl -s -X POST https://nongbuxxbackend-production.up.railway.app/api/generate \
        -H "Content-Type: application/json" \
        -d '{"url":"test","api_provider":"anthropic","api_key":"sk-ant-test","content_type":"x"}' \
        2>/dev/null || echo "{}")
    
    if [[ "$TEST_RESPONSE2" != *"INVALID_CONTENT_TYPE"* ]]; then
        print_color "✅ 강제 재배포 성공!" $GREEN
    else
        print_color "❌ 재배포 실패. Railway 대시보드를 확인하세요." $RED
        print_color "   https://railway.app" $YELLOW
        exit 1
    fi
else
    print_color "⚠️  배포 상태를 확인할 수 없습니다." $YELLOW
    print_color "수동으로 확인이 필요합니다:" $NC
    print_color "  railway logs -n 50" $NC
fi

# 8. 최종 로그 확인
print_color "📜 최근 배포 로그 (마지막 10줄):" $BLUE
railway logs -n 10 | tail || true

echo ""
print_color "💡 추가 명령어:" $BLUE
print_color "  • 실시간 로그: railway logs -f" $NC
print_color "  • 상세 모니터링: ./railway-deploy-monitor.sh" $NC
print_color "  • 프론트엔드 배포: ./deploy-quick.sh" $NC 