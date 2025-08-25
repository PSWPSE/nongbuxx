#!/bin/bash

# 🔄 NONGBUXX 롤백 스크립트
# 이전 안정 버전으로 빠르게 롤백

set -e

echo "🔄 NONGBUXX 롤백 시스템"
echo "======================"

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

print_step() {
    echo ""
    print_color "🔸 $1" $CYAN
    echo "----------------------------------------"
}

print_success() {
    print_color "✅ $1" $GREEN
}

print_error() {
    print_color "❌ $1" $RED
}

print_warning() {
    print_color "⚠️  $1" $YELLOW
}

print_info() {
    print_color "ℹ️  $1" $BLUE
}

# 롤백 타입 확인
ROLLBACK_TYPE=${1:-"auto"}

if [ "$ROLLBACK_TYPE" = "help" ] || [ "$ROLLBACK_TYPE" = "--help" ] || [ "$ROLLBACK_TYPE" = "-h" ]; then
    echo "사용법:"
    echo "  ./deploy-rollback.sh                  # 자동 롤백 (1개 커밋 되돌리기)"
    echo "  ./deploy-rollback.sh auto             # 자동 롤백 (1개 커밋 되돌리기)"
    echo "  ./deploy-rollback.sh 2                # 2개 커밋 되돌리기"
    echo "  ./deploy-rollback.sh abc123           # 특정 커밋으로 롤백"
    echo "  ./deploy-rollback.sh emergency        # 긴급 롤백 (최근 안정 버전)"
    exit 0
fi

print_step "1단계: 현재 상태 확인"

# 현재 커밋 정보
CURRENT_COMMIT=$(git rev-parse HEAD)
CURRENT_MESSAGE=$(git log -1 --pretty=format:"%s")
print_info "현재 커밋: $CURRENT_COMMIT"
print_info "현재 메시지: $CURRENT_MESSAGE"

# 최근 커밋 히스토리 표시
print_info "최근 커밋 히스토리:"
git log --oneline -n 5

print_step "2단계: 롤백 대상 결정"

TARGET_COMMIT=""

case "$ROLLBACK_TYPE" in
    "auto")
        # 1개 커밋 되돌리기
        TARGET_COMMIT=$(git rev-parse HEAD~1)
        TARGET_MESSAGE=$(git log -1 --pretty=format:"%s" $TARGET_COMMIT)
        print_info "자동 롤백: 1개 커밋 되돌리기"
        print_info "대상 커밋: $TARGET_COMMIT"
        print_info "대상 메시지: $TARGET_MESSAGE"
        ;;
        
    "emergency")
        # 최근 안정 버전 찾기 (fix: 또는 feat: 커밋 중 가장 최근)
        TARGET_COMMIT=$(git log --grep="^fix:" --grep="^feat:" --pretty=format:"%H" -n 1)
        if [ -z "$TARGET_COMMIT" ]; then
            TARGET_COMMIT=$(git rev-parse HEAD~2)
        fi
        TARGET_MESSAGE=$(git log -1 --pretty=format:"%s" $TARGET_COMMIT)
        print_warning "긴급 롤백: 최근 안정 버전으로 롤백"
        print_info "대상 커밋: $TARGET_COMMIT"
        print_info "대상 메시지: $TARGET_MESSAGE"
        ;;
        
    [0-9]*)
        # 숫자면 해당 개수만큼 되돌리기
        TARGET_COMMIT=$(git rev-parse HEAD~$ROLLBACK_TYPE)
        TARGET_MESSAGE=$(git log -1 --pretty=format:"%s" $TARGET_COMMIT)
        print_info "수동 롤백: $ROLLBACK_TYPE개 커밋 되돌리기"
        print_info "대상 커밋: $TARGET_COMMIT"
        print_info "대상 메시지: $TARGET_MESSAGE"
        ;;
        
    *)
        # 커밋 해시로 간주
        if git rev-parse --verify "$ROLLBACK_TYPE" >/dev/null 2>&1; then
            TARGET_COMMIT="$ROLLBACK_TYPE"
            TARGET_MESSAGE=$(git log -1 --pretty=format:"%s" $TARGET_COMMIT)
            print_info "특정 커밋으로 롤백"
            print_info "대상 커밋: $TARGET_COMMIT"
            print_info "대상 메시지: $TARGET_MESSAGE"
        else
            print_error "유효하지 않은 커밋 해시: $ROLLBACK_TYPE"
            exit 1
        fi
        ;;
esac

# 롤백 확인
echo ""
print_warning "⚠️  롤백을 진행하시겠습니까?"
print_color "현재: $CURRENT_COMMIT ($CURRENT_MESSAGE)" $YELLOW
print_color "대상: $TARGET_COMMIT ($TARGET_MESSAGE)" $GREEN
echo ""
read -p "계속하려면 'yes'를 입력하세요: " confirm

if [ "$confirm" != "yes" ]; then
    print_info "롤백이 취소되었습니다."
    exit 0
fi

print_step "3단계: Git 롤백 실행"

# Git 롤백 실행
print_info "Git 롤백 실행 중..."
git reset --hard $TARGET_COMMIT
git push origin main --force

print_success "Git 롤백 완료"

print_step "4단계: 백엔드 롤백 (Railway)"

print_info "Railway 자동 배포 트리거 중..."
print_info "또는 수동 배포를 실행합니다..."

# 수동 배포로 확실하게 롤백
railway up --force

print_info "백엔드 롤백 대기 중 (1분)..."
for i in {1..12}; do
    printf "."
    sleep 5
done
echo ""

# 백엔드 상태 확인
print_info "백엔드 롤백 상태 확인 중..."
HEALTH_RESPONSE=$(curl -s https://nongbuxxbackend-production.up.railway.app/api/health || echo "Failed")

if [[ "$HEALTH_RESPONSE" == *"healthy"* ]]; then
    print_success "백엔드 롤백 완료 및 정상 작동 확인"
else
    print_warning "백엔드 롤백 후 상태 확인 실패 - 수동 확인 필요"
fi

print_step "5단계: 프론트엔드 롤백 (Vercel)"

print_info "Vercel 프론트엔드 롤백 시작..."
cd frontend

# 프론트엔드 재배포
DEPLOYMENT_OUTPUT=$(vercel --prod --yes 2>&1)
echo "$DEPLOYMENT_OUTPUT"

# 도메인 연결
DEPLOYMENT_URL=$(echo "$DEPLOYMENT_OUTPUT" | grep "Production:" | awk '{print $2}')
if [ ! -z "$DEPLOYMENT_URL" ]; then
    print_info "도메인 연결 중..."
    vercel alias $DEPLOYMENT_URL nongbuxxfrontend.vercel.app 2>/dev/null || true
    sleep 10
    
    # 프론트엔드 확인
    FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://nongbuxxfrontend.vercel.app/ || echo "000")
    if [ "$FRONTEND_RESPONSE" = "200" ]; then
        print_success "프론트엔드 롤백 완료 및 정상 작동 확인"
    else
        print_warning "프론트엔드 롤백 후 접속 확인 실패 (HTTP: $FRONTEND_RESPONSE)"
    fi
else
    print_error "프론트엔드 롤백 URL을 찾을 수 없습니다."
fi

cd ..

print_step "6단계: 롤백 검증"

print_info "전체 시스템 롤백 검증 중..."

# API 기능 테스트
TEST_RESPONSE=$(curl -s -X POST https://nongbuxxbackend-production.up.railway.app/api/generate \
    -H "Content-Type: application/json" \
    -d '{"url":"test","api_provider":"anthropic","api_key":"sk-ant-test","content_type":"x"}' \
    2>/dev/null || echo "{}")

if [[ "$TEST_RESPONSE" == *"INVALID_URL"* ]] || [[ "$TEST_RESPONSE" == *"INVALID_ANTHROPIC_KEY"* ]]; then
    print_success "API 기능 검증 통과"
else
    print_warning "API 기능 검증 실패 - 추가 확인 필요"
fi

print_step "7단계: 롤백 완료 리포트"

echo ""
print_color "🔄 NONGBUXX 롤백 완료!" $BOLD$GREEN
print_color "========================" $GREEN
echo ""

print_color "📊 롤백 요약:" $BLUE
print_color "  • 롤백 시각: $(date '+%Y-%m-%d %H:%M:%S')" $NC
print_color "  • 이전 커밋: $CURRENT_COMMIT" $NC
print_color "  • 현재 커밋: $TARGET_COMMIT" $NC
print_color "  • 타겟 메시지: $TARGET_MESSAGE" $NC
echo ""

print_color "🌐 서비스 URL:" $BLUE
print_color "  • 프론트엔드: https://nongbuxxfrontend.vercel.app/" $NC
print_color "  • 백엔드 API: https://nongbuxxbackend-production.up.railway.app" $NC
print_color "  • 헬스체크: https://nongbuxxbackend-production.up.railway.app/api/health" $NC
echo ""

print_color "💡 다음 단계:" $BLUE
print_color "  • 서비스 상태 확인: ./deploy-status.sh" $NC
print_color "  • 문제 원인 분석: git log --oneline -n 10" $NC
print_color "  • 수정 후 재배포: ./deploy-all.sh \"fix: 문제 해결\"" $NC
echo ""

print_color "🎉 롤백이 완료되었습니다. 서비스를 확인해보세요!" $BOLD$GREEN
