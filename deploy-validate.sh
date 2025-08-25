#!/bin/bash

# 🔍 NONGBUXX 배포 전 검증 스크립트
# 배포 전 모든 요구사항과 설정을 자동으로 검증하고 수정

set -e

echo "🔍 NONGBUXX 배포 전 검증 시스템"
echo "=============================="

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

# 검증 결과 추적
VALIDATION_ERRORS=0
VALIDATION_WARNINGS=0
FIXES_APPLIED=0

add_error() {
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    print_error "$1"
}

add_warning() {
    VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
    print_warning "$1"
}

apply_fix() {
    FIXES_APPLIED=$((FIXES_APPLIED + 1))
    print_success "$1"
}

print_section "1단계: Git 상태 검증"

# Git 상태 확인
if git diff --quiet; then
    print_success "작업 디렉토리가 깨끗합니다"
else
    add_warning "커밋되지 않은 변경사항이 있습니다"
    git status --porcelain
fi

# 원격 저장소와 동기화 확인
git fetch origin main >/dev/null 2>&1
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main)

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    print_success "로컬과 원격 저장소가 동기화되어 있습니다"
else
    add_warning "로컬과 원격 저장소가 다릅니다. 푸시 또는 풀이 필요할 수 있습니다"
fi

print_section "2단계: 필수 파일 검증 및 복구"

# requirements.txt 검증
if [ -f "requirements.txt" ]; then
    print_success "requirements.txt 파일 존재"
    
    # 필수 패키지 확인
    REQUIRED_PACKAGES="flask gunicorn requests beautifulsoup4 anthropic openai"
    for package in $REQUIRED_PACKAGES; do
        if grep -q "$package" requirements.txt; then
            print_success "$package 패키지 포함됨"
        else
            add_warning "$package 패키지가 requirements.txt에 없습니다"
        fi
    done
else
    add_error "requirements.txt 파일이 없습니다"
fi

# railway.json 검증 및 복구
print_info "railway.json 파일 검증 중..."
if [ ! -f "railway.json" ] || ! jq empty railway.json 2>/dev/null; then
    print_warning "railway.json 파일이 손상되었거나 없습니다. 복구 중..."
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
    apply_fix "railway.json 파일 복구 완료"
else
    print_success "railway.json 파일 정상"
fi

# Procfile 검증 및 생성
if [ ! -f "Procfile" ]; then
    print_warning "Procfile이 없습니다. 생성 중..."
    echo "web: gunicorn --bind 0.0.0.0:\$PORT app:app" > Procfile
    apply_fix "Procfile 생성 완료"
else
    print_success "Procfile 존재"
    
    # Procfile 내용 검증
    if grep -q "gunicorn.*app:app" Procfile; then
        print_success "Procfile 내용 정상"
    else
        add_warning "Procfile 내용이 올바르지 않을 수 있습니다"
    fi
fi

# frontend/vercel.json 검증 및 복구
print_info "frontend/vercel.json 파일 검증 중..."
if [ ! -f "frontend/vercel.json" ] || ! jq empty frontend/vercel.json 2>/dev/null; then
    print_warning "frontend/vercel.json 파일이 손상되었거나 없습니다. 복구 중..."
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
    apply_fix "frontend/vercel.json 파일 복구 완료"
else
    print_success "frontend/vercel.json 파일 정상"
fi

print_section "3단계: CLI 도구 연결 확인"

# Railway CLI 확인
if command -v railway >/dev/null 2>&1; then
    print_success "Railway CLI 설치됨"
    
    if railway status >/dev/null 2>&1; then
        print_success "Railway 프로젝트 연결됨"
    else
        add_error "Railway 프로젝트가 연결되지 않았습니다. 'railway login' 실행 필요"
    fi
else
    add_error "Railway CLI가 설치되지 않았습니다"
fi

# Vercel CLI 확인
if command -v vercel >/dev/null 2>&1; then
    print_success "Vercel CLI 설치됨"
    
    if vercel whoami >/dev/null 2>&1; then
        print_success "Vercel 계정 로그인됨"
    else
        add_error "Vercel에 로그인되지 않았습니다. 'vercel login' 실행 필요"
    fi
else
    add_error "Vercel CLI가 설치되지 않았습니다"
fi

# jq 도구 확인 (JSON 파싱용)
if command -v jq >/dev/null 2>&1; then
    print_success "jq JSON 파서 설치됨"
else
    add_warning "jq가 설치되지 않았습니다. JSON 검증 기능이 제한됩니다"
fi

print_section "4단계: 핵심 파일 구조 검증"

# 필수 파일들 확인
REQUIRED_FILES="app.py frontend/index.html frontend/script.js frontend/styles.css"
for file in $REQUIRED_FILES; do
    if [ -f "$file" ]; then
        print_success "$file 존재"
    else
        add_error "$file 파일이 없습니다"
    fi
done

# Python 파일 문법 검증
print_info "Python 파일 문법 검증 중..."
if python3 -m py_compile app.py 2>/dev/null; then
    print_success "app.py 문법 정상"
else
    add_error "app.py에 문법 오류가 있습니다"
fi

# JavaScript 파일 기본 검증
print_info "JavaScript 파일 기본 검증 중..."
if [ -f "frontend/script.js" ]; then
    # 기본적인 문법 오류 체크 (세미콜론, 괄호 등)
    if node -c frontend/script.js 2>/dev/null; then
        print_success "frontend/script.js 문법 정상"
    else
        add_warning "frontend/script.js에 문법 문제가 있을 수 있습니다"
    fi
fi

print_section "5단계: 환경 설정 검증"

# Python 가상 환경 확인
if [ -d "venv" ]; then
    print_success "Python 가상 환경 존재"
    
    # 가상 환경 활성화 테스트
    if [ -f "venv/bin/activate" ]; then
        print_success "가상 환경 활성화 스크립트 존재"
    else
        add_warning "가상 환경 활성화 스크립트가 없습니다"
    fi
else
    add_warning "Python 가상 환경이 없습니다"
fi

# .env 파일 확인 (선택사항)
if [ -f ".env" ]; then
    print_success ".env 파일 존재"
else
    print_info ".env 파일이 없습니다 (선택사항)"
fi

# .gitignore 확인
if [ -f ".gitignore" ]; then
    print_success ".gitignore 파일 존재"
    
    # 필수 항목 확인
    GITIGNORE_ITEMS="__pycache__ .env venv node_modules"
    for item in $GITIGNORE_ITEMS; do
        if grep -q "$item" .gitignore; then
            print_success "$item이 .gitignore에 포함됨"
        else
            add_warning "$item이 .gitignore에 없습니다"
        fi
    done
else
    add_warning ".gitignore 파일이 없습니다"
fi

print_section "6단계: 포트 및 프로세스 확인"

# 포트 사용 확인
if lsof -ti:8080 >/dev/null 2>&1; then
    PID=$(lsof -ti:8080)
    add_warning "포트 8080이 사용 중입니다 (PID: $PID)"
else
    print_success "포트 8080 사용 가능"
fi

if lsof -ti:3000 >/dev/null 2>&1; then
    PID=$(lsof -ti:3000)
    add_warning "포트 3000이 사용 중입니다 (PID: $PID)"
else
    print_success "포트 3000 사용 가능"
fi

print_section "7단계: 배포 준비 상태 확인"

# 로컬 서버 테스트 (선택사항)
print_info "로컬 서버 연결 테스트 중..."
if curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://localhost:8080/api/health 2>/dev/null | grep -q "200"; then
    print_success "로컬 백엔드 서버 응답 정상"
else
    print_info "로컬 백엔드 서버가 실행되지 않았습니다 (선택사항)"
fi

# 디스크 공간 확인
DISK_USAGE=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 90 ]; then
    print_success "디스크 공간 충분 (사용률: ${DISK_USAGE}%)"
else
    add_warning "디스크 공간 부족 (사용률: ${DISK_USAGE}%)"
fi

print_section "8단계: 검증 결과 요약"

echo ""
print_color "📊 배포 전 검증 완료" $BOLD$BLUE
print_color "====================" $BLUE
echo ""

print_color "📈 검증 통계:" $BLUE
print_color "  • 오류: $VALIDATION_ERRORS개" $([ $VALIDATION_ERRORS -eq 0 ] && echo $GREEN || echo $RED)
print_color "  • 경고: $VALIDATION_WARNINGS개" $([ $VALIDATION_WARNINGS -eq 0 ] && echo $GREEN || echo $YELLOW)
print_color "  • 자동 수정: $FIXES_APPLIED개" $GREEN
echo ""

if [ $VALIDATION_ERRORS -eq 0 ]; then
    print_color "🎉 배포 준비 완료!" $BOLD$GREEN
    print_color "이제 안전하게 배포할 수 있습니다:" $GREEN
    print_color "  ./deploy-all.sh \"커밋 메시지\"" $NC
else
    print_color "❌ 배포 전 문제 해결 필요" $BOLD$RED
    print_color "위의 오류들을 먼저 해결하세요." $RED
fi

if [ $VALIDATION_WARNINGS -gt 0 ]; then
    echo ""
    print_color "⚠️  경고 사항들:" $YELLOW
    print_color "  경고는 배포를 막지 않지만, 해결하면 더 안정적입니다." $NC
fi

echo ""
print_color "💡 다음 단계:" $BLUE
if [ $VALIDATION_ERRORS -eq 0 ]; then
    print_color "  1. ./deploy-all.sh \"feat: 새로운 기능\"  # 전체 배포" $NC
    print_color "  2. ./deploy-monitor.sh 300 30          # 배포 후 모니터링" $NC
    print_color "  3. ./deploy-status.sh                  # 상태 확인" $NC
else
    print_color "  1. 위의 오류들을 수정하세요" $NC
    print_color "  2. ./deploy-validate.sh               # 재검증" $NC
    print_color "  3. ./deploy-all.sh \"fix: 검증 후 수정\"  # 수정 후 배포" $NC
fi
