#!/bin/bash

# NONGBUXX 빠른 배포 스크립트
# 현재 변경사항을 Vercel에 즉시 배포

set -e

echo "🚀 NONGBUXX 빠른 배포 시작"
echo "=========================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_color() {
    printf "${2}${1}${NC}\n"
}

# 프론트엔드 디렉토리로 이동
cd frontend

# 현재 시간 출력
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
print_color "📅 배포 시각: $TIMESTAMP" $BLUE

# Vercel로 배포 (프로덕션)
print_color "🌐 Vercel 프로덕션 배포 중..." $BLUE
DEPLOYMENT_OUTPUT=$(vercel --prod --yes 2>&1)
echo "$DEPLOYMENT_OUTPUT"

# 배포 URL 추출 및 도메인 연결
DEPLOYMENT_URL=$(echo "$DEPLOYMENT_OUTPUT" | grep "Production:" | awk '{print $2}')
if [ ! -z "$DEPLOYMENT_URL" ]; then
    print_color "📌 도메인 연결 중..." $YELLOW
    vercel alias $DEPLOYMENT_URL nongbuxxfrontend.vercel.app 2>/dev/null || true
fi

# 배포 완료 메시지
print_color "✅ 배포 완료!" $GREEN
print_color "🔗 사이트: https://nongbuxxfrontend.vercel.app/" $GREEN
print_color "📱 모바일에서도 확인해보세요!" $YELLOW

# 루트 디렉토리로 돌아가기
cd ..

print_color "" $NC
print_color "💡 팁: 다음에도 이 스크립트를 사용하세요!" $BLUE
print_color "   ./deploy-quick.sh" $YELLOW 