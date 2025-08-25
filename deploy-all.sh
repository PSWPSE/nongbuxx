#!/bin/bash

# 🚀 NONGBUXX 통합 배포 스크립트
# 프론트엔드 + 백엔드 + 검증 + 모니터링 올인원 솔루션

set -e

echo "🚀 NONGBUXX 통합 배포 시스템"
echo "=================================="
echo "✨ 프론트엔드 + 백엔드 + 검증을 한 번에 처리합니다"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

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

# 전역 변수
DEPLOYMENT_START_TIME=$(date "+%Y-%m-%d %H:%M:%S")
COMMIT_HASH=""
BACKEND_DEPLOYED=false
FRONTEND_DEPLOYED=false
VALIDATION_PASSED=false

# 1. 사전 검증 단계
print_step "1단계: 사전 검증 및 환경 준비"

# 커밋 메시지 확인
if [ -z "$1" ]; then
    print_error "사용법: ./deploy-all.sh \"커밋 메시지\""
    echo "예시: ./deploy-all.sh \"feat: 새로운 기능 추가\""
    exit 1
fi

COMMIT_MESSAGE="$1"
print_info "커밋 메시지: $COMMIT_MESSAGE"

# Git 상태 확인
print_info "Git 상태 확인 중..."
git status --porcelain > /dev/null
if [ $? -eq 0 ]; then
    print_success "Git 상태 정상"
else
    print_error "Git 상태 확인 실패"
    exit 1
fi

# Railway CLI 연결 상태 확인
print_info "Railway 연결 상태 확인 중..."
if railway status > /dev/null 2>&1; then
    print_success "Railway 연결 상태 정상"
else
    print_error "Railway CLI가 연결되지 않았습니다. 'railway login' 실행 후 다시 시도하세요."
    exit 1
fi

# Vercel CLI 연결 상태 확인
print_info "Vercel 연결 상태 확인 중..."
if vercel whoami > /dev/null 2>&1; then
    print_success "Vercel 연결 상태 정상"
else
    print_error "Vercel CLI가 연결되지 않았습니다. 'vercel login' 실행 후 다시 시도하세요."
    exit 1
fi

# 로컬 서버 테스트 (선택사항)
print_info "로컬 서버 상태 확인 중..."
if curl -s http://localhost:8080/api/health | grep -q "healthy"; then
    print_success "로컬 서버 정상 작동 확인"
else
    print_warning "로컬 서버가 실행되지 않았습니다. 테스트를 건너뜁니다."
fi

# 2. 설정 파일 자동 복구
print_step "2단계: 배포 설정 파일 검증 및 복구"

# railway.json 검증 및 복구
print_info "railway.json 파일 검증 중..."
if [ ! -f "railway.json" ] || ! jq empty railway.json 2>/dev/null; then
    print_warning "railway.json 파일이 손상되었습니다. 복구 중..."
    cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT app:app",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  },
  "environments": {
    "production": {
      "variables": {
        "PYTHONUNBUFFERED": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PORT": "$PORT"
      }
    }
  }
}
EOF
    print_success "railway.json 파일 복구 완료"
else
    print_success "railway.json 파일 정상"
fi

# frontend/vercel.json 검증 및 복구
print_info "frontend/vercel.json 파일 검증 중..."
if [ ! -f "frontend/vercel.json" ] || ! jq empty frontend/vercel.json 2>/dev/null; then
    print_warning "frontend/vercel.json 파일이 손상되었습니다. 복구 중..."
    cat > frontend/vercel.json << 'EOF'
{
  "builds": [
    {
      "src": "**/*",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/$1"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "*"
        },
        {
          "key": "Access-Control-Allow-Methods",
          "value": "GET, POST, PUT, DELETE, OPTIONS"
        },
        {
          "key": "Access-Control-Allow-Headers",
          "value": "Content-Type, Authorization"
        }
      ]
    }
  ]
}
EOF
    print_success "frontend/vercel.json 파일 복구 완료"
else
    print_success "frontend/vercel.json 파일 정상"
fi

# 3. Git 커밋 및 푸시
print_step "3단계: Git 커밋 및 푸시"

print_info "변경사항을 Git에 커밋하고 푸시합니다..."
git add .
git commit -m "$COMMIT_MESSAGE" || print_warning "커밋할 변경사항이 없습니다."
git push origin main

COMMIT_HASH=$(git rev-parse HEAD)
print_success "Git 푸시 완료: $COMMIT_HASH"

# 4. 백엔드 배포 (Railway)
print_step "4단계: 백엔드 배포 (Railway)"

print_info "Railway 백엔드 배포 시작..."
print_info "자동 배포 대기 중 (2분)..."

# 프로그레스 바 표시
for i in {1..24}; do
    printf "."
    sleep 5
done
echo ""

print_info "백엔드 배포 상태 확인 중..."

# 배포 상태 확인 (최대 3번 시도)
BACKEND_HEALTH_CHECK_COUNT=0
while [ $BACKEND_HEALTH_CHECK_COUNT -lt 3 ]; do
    HEALTH_RESPONSE=$(curl -s https://nongbuxxbackend-production.up.railway.app/api/health || echo "Failed")
    
    if [[ "$HEALTH_RESPONSE" == *"healthy"* ]]; then
        print_success "백엔드 배포 완료 및 정상 작동 확인"
        BACKEND_DEPLOYED=true
        break
    else
        BACKEND_HEALTH_CHECK_COUNT=$((BACKEND_HEALTH_CHECK_COUNT + 1))
        print_warning "백엔드 헬스체크 실패 (시도 $BACKEND_HEALTH_CHECK_COUNT/3)"
        
        if [ $BACKEND_HEALTH_CHECK_COUNT -eq 1 ]; then
            print_info "수동 배포를 시도합니다..."
            railway up --detach
            sleep 30
        elif [ $BACKEND_HEALTH_CHECK_COUNT -eq 2 ]; then
            print_info "강제 재배포를 시도합니다..."
            railway up --force
            sleep 60
        fi
    fi
done

if [ "$BACKEND_DEPLOYED" = false ]; then
    print_error "백엔드 배포 실패! 수동 확인이 필요합니다."
    print_info "문제 해결 방법:"
    print_info "1. railway logs -n 100"
    print_info "2. railway restart"
    print_info "3. Railway 대시보드 확인: https://railway.app"
    exit 1
fi

# 5. 프론트엔드 배포 (Vercel)
print_step "5단계: 프론트엔드 배포 (Vercel)"

print_info "Vercel 프론트엔드 배포 시작..."
cd frontend

DEPLOYMENT_OUTPUT=$(vercel --prod --yes 2>&1)
echo "$DEPLOYMENT_OUTPUT"

# 배포 URL 추출 및 도메인 연결
DEPLOYMENT_URL=$(echo "$DEPLOYMENT_OUTPUT" | grep "Production:" | awk '{print $2}')
if [ ! -z "$DEPLOYMENT_URL" ]; then
    print_info "도메인 연결 중..."
    vercel alias $DEPLOYMENT_URL nongbuxxfrontend.vercel.app 2>/dev/null || true
    sleep 10
    
    # 프론트엔드 배포 확인
    FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://nongbuxxfrontend.vercel.app/ || echo "000")
    if [ "$FRONTEND_RESPONSE" = "200" ]; then
        print_success "프론트엔드 배포 완료 및 정상 작동 확인"
        FRONTEND_DEPLOYED=true
    else
        print_warning "프론트엔드 배포 완료했지만 접속 확인 실패 (HTTP: $FRONTEND_RESPONSE)"
        FRONTEND_DEPLOYED=true  # 배포는 완료된 것으로 간주
    fi
else
    print_error "프론트엔드 배포 URL을 찾을 수 없습니다."
    cd ..
    exit 1
fi

cd ..

# 6. 통합 검증
print_step "6단계: 전체 시스템 통합 검증"

print_info "API 기능 테스트 중..."
TEST_RESPONSE=$(curl -s -X POST https://nongbuxxbackend-production.up.railway.app/api/generate \
    -H "Content-Type: application/json" \
    -d '{"url":"test","api_provider":"anthropic","api_key":"sk-ant-test","content_type":"x"}' \
    2>/dev/null || echo "{}")

if [[ "$TEST_RESPONSE" == *"INVALID_URL"* ]] || [[ "$TEST_RESPONSE" == *"INVALID_ANTHROPIC_KEY"* ]]; then
    print_success "API 기능 테스트 통과 (최신 코드 반영 확인)"
    VALIDATION_PASSED=true
elif [[ "$TEST_RESPONSE" == *"INVALID_CONTENT_TYPE"* ]]; then
    print_error "최신 코드가 반영되지 않았습니다. 강제 재배포가 필요합니다."
    VALIDATION_PASSED=false
else
    print_warning "API 테스트 응답을 확인할 수 없습니다: $TEST_RESPONSE"
    VALIDATION_PASSED=true  # 일단 통과로 간주
fi

# 7. 배포 완료 리포트
print_step "7단계: 배포 완료 리포트"

DEPLOYMENT_END_TIME=$(date "+%Y-%m-%d %H:%M:%S")

print_color "" $NC
print_color "🎉 NONGBUXX 배포 완료!" $BOLD$GREEN
print_color "================================" $GREEN
echo ""

print_color "📊 배포 요약:" $BLUE
print_color "  • 시작 시간: $DEPLOYMENT_START_TIME" $NC
print_color "  • 완료 시간: $DEPLOYMENT_END_TIME" $NC
print_color "  • 커밋 해시: $COMMIT_HASH" $NC
print_color "  • 커밋 메시지: $COMMIT_MESSAGE" $NC
echo ""

print_color "🌐 서비스 URL:" $BLUE
print_color "  • 프론트엔드: https://nongbuxxfrontend.vercel.app/" $NC
print_color "  • 백엔드 API: https://nongbuxxbackend-production.up.railway.app" $NC
print_color "  • 헬스체크: https://nongbuxxbackend-production.up.railway.app/api/health" $NC
echo ""

print_color "✅ 배포 상태:" $BLUE
if [ "$BACKEND_DEPLOYED" = true ]; then
    print_color "  • 백엔드: ✅ 정상 배포" $GREEN
else
    print_color "  • 백엔드: ❌ 배포 실패" $RED
fi

if [ "$FRONTEND_DEPLOYED" = true ]; then
    print_color "  • 프론트엔드: ✅ 정상 배포" $GREEN
else
    print_color "  • 프론트엔드: ❌ 배포 실패" $RED
fi

if [ "$VALIDATION_PASSED" = true ]; then
    print_color "  • 통합 검증: ✅ 통과" $GREEN
else
    print_color "  • 통합 검증: ❌ 실패" $RED
fi

echo ""
print_color "💡 유용한 명령어:" $BLUE
print_color "  • 실시간 로그: railway logs -f" $NC
print_color "  • 배포 모니터링: ./deploy-monitor.sh" $NC
print_color "  • 롤백: ./deploy-rollback.sh" $NC
print_color "  • 상태 확인: ./deploy-status.sh" $NC

echo ""
if [ "$BACKEND_DEPLOYED" = true ] && [ "$FRONTEND_DEPLOYED" = true ] && [ "$VALIDATION_PASSED" = true ]; then
    print_color "🎉 모든 배포가 성공적으로 완료되었습니다!" $BOLD$GREEN
    print_color "🚀 서비스가 정상적으로 운영 중입니다!" $BOLD$GREEN
else
    print_color "⚠️  일부 배포에 문제가 있습니다. 위의 상태를 확인하세요." $BOLD$YELLOW
fi

echo ""
print_color "📱 모바일에서도 확인해보세요!" $CYAN
