#!/bin/bash

# 🚀 Railway 배포 모니터링 스크립트
# 배포 후 상태를 확인하고 문제 발생 시 수동 배포 안내

set -e

echo "🔍 Railway 배포 모니터링"
echo "======================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_color() {
    printf "${2}${1}${NC}\n"
}

# 1. 현재 Git 커밋 해시 확인
CURRENT_COMMIT=$(git rev-parse HEAD)
print_color "📌 현재 Git 커밋: $CURRENT_COMMIT" $BLUE

# 2. Railway 상태 확인
print_color "🚂 Railway 상태 확인 중..." $BLUE
railway status

# 3. 최근 배포 정보 확인
print_color "📋 최근 배포 로그 확인..." $BLUE
railway logs -n 20 | grep -E "(Deploy|Build|Success|Error|Failed)" || true

# 4. 배포된 버전과 로컬 버전 비교를 위한 헬스체크
print_color "🏥 백엔드 헬스체크..." $BLUE
HEALTH_RESPONSE=$(curl -s https://nongbuxxbackend-production.up.railway.app/api/health || echo "Failed")

if [[ "$HEALTH_RESPONSE" == *"healthy"* ]]; then
    print_color "✅ 백엔드가 정상 작동 중입니다." $GREEN
else
    print_color "❌ 백엔드 응답 실패!" $RED
    print_color "🔧 수동 배포가 필요할 수 있습니다." $YELLOW
fi

# 5. 최신 코드 반영 여부 테스트 (예: X 타입 지원 확인)
print_color "🧪 기능 테스트 중..." $BLUE
TEST_RESPONSE=$(curl -s -X POST https://nongbuxxbackend-production.up.railway.app/api/generate \
    -H "Content-Type: application/json" \
    -d '{"url":"test","api_provider":"anthropic","api_key":"sk-ant-test","content_type":"x"}' \
    2>/dev/null || echo "{}")

if [[ "$TEST_RESPONSE" == *"INVALID_CONTENT_TYPE"* ]]; then
    print_color "❌ 최신 코드가 배포되지 않았습니다!" $RED
    print_color "🔄 수동 재배포가 필요합니다:" $YELLOW
    print_color "   railway up --detach" $YELLOW
elif [[ "$TEST_RESPONSE" == *"INVALID_ANTHROPIC_KEY"* ]] || [[ "$TEST_RESPONSE" == *"INVALID_URL"* ]]; then
    print_color "✅ 최신 코드가 정상 배포되었습니다." $GREEN
else
    print_color "⚠️  배포 상태를 확인할 수 없습니다." $YELLOW
fi

# 6. 배포 체크리스트
echo ""
print_color "📋 배포 체크리스트:" $BLUE
print_color "  □ Git 커밋 및 푸시 완료" $NC
print_color "  □ Railway 자동 배포 트리거 확인" $NC
print_color "  □ 빌드 로그에 에러 없음" $NC
print_color "  □ 헬스체크 정상 응답" $NC
print_color "  □ 새 기능 테스트 통과" $NC

echo ""
print_color "💡 문제 발생 시 해결 방법:" $YELLOW
print_color "  1. railway up --detach (수동 배포)" $NC
print_color "  2. railway logs -n 100 (상세 로그 확인)" $NC
print_color "  3. railway restart (서비스 재시작)" $NC
print_color "  4. GitHub 웹훅 재연결 (Railway 대시보드)" $NC 