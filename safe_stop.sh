#!/bin/bash

# 🛑 NONGBUXX 안전 중지 스크립트

echo "🛑 NONGBUXX 시스템 중지 중..."

# 1. 실행 중인 프로세스 확인
echo "🔍 실행 중인 프로세스 확인..."

BACKEND_PROCESSES=$(lsof -ti:8080 2>/dev/null)
FRONTEND_PROCESSES=$(lsof -ti:3000 2>/dev/null)

if [ -z "$BACKEND_PROCESSES" ] && [ -z "$FRONTEND_PROCESSES" ]; then
    echo "ℹ️ 실행 중인 NONGBUXX 프로세스가 없습니다."
    exit 0
fi

# 2. 정상 종료 시도 (SIGTERM)
echo "📤 정상 종료 신호 전송 중..."

if [ ! -z "$BACKEND_PROCESSES" ]; then
    echo "  • 백엔드 프로세스 정상 종료 시도..."
    echo $BACKEND_PROCESSES | xargs kill -TERM 2>/dev/null || true
fi

if [ ! -z "$FRONTEND_PROCESSES" ]; then
    echo "  • 프론트엔드 프로세스 정상 종료 시도..."
    echo $FRONTEND_PROCESSES | xargs kill -TERM 2>/dev/null || true
fi

# 3. 정상 종료 대기
echo "⏳ 정상 종료 대기 중 (10초)..."
sleep 10

# 4. 강제 종료 확인 및 실행
echo "🔍 프로세스 상태 재확인..."

REMAINING_BACKEND=$(lsof -ti:8080 2>/dev/null)
REMAINING_FRONTEND=$(lsof -ti:3000 2>/dev/null)

if [ ! -z "$REMAINING_BACKEND" ] || [ ! -z "$REMAINING_FRONTEND" ]; then
    echo "⚠️ 일부 프로세스가 종료되지 않았습니다. 강제 종료 실행..."
    
    # 강제 종료 (SIGKILL)
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    pkill -9 -f "python.*http.server" 2>/dev/null || true
    pkill -9 -f "python3.*app.py" 2>/dev/null || true
    
    echo "💥 강제 종료 완료"
else
    echo "✅ 모든 프로세스가 정상적으로 종료되었습니다"
fi

# 5. 최종 확인
sleep 2
FINAL_BACKEND=$(lsof -ti:8080 2>/dev/null)
FINAL_FRONTEND=$(lsof -ti:3000 2>/dev/null)

if [ -z "$FINAL_BACKEND" ] && [ -z "$FINAL_FRONTEND" ]; then
    echo "✅ NONGBUXX 시스템이 완전히 중지되었습니다"
    
    # 6. 정리 작업
    echo "🧹 정리 작업 수행 중..."
    
    # 로그 파일 이동 (선택사항)
    if [ -f "nongbuxx_backend.log" ]; then
        mv nongbuxx_backend.log "logs/backend_$(date +%Y%m%d_%H%M%S).log" 2>/dev/null || true
    fi
    
    if [ -f "nongbuxx_frontend.log" ]; then
        mv nongbuxx_frontend.log "logs/frontend_$(date +%Y%m%d_%H%M%S).log" 2>/dev/null || true
    fi
    
    # 임시 파일 정리
    find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    echo "🎉 정리 작업 완료"
    echo ""
    echo "📍 시스템 재시작: ./safe_restart.sh"
    
else
    echo "❌ 일부 프로세스가 여전히 실행 중입니다"
    echo "   포트 8080: $(lsof -ti:8080 2>/dev/null | wc -l) 프로세스"
    echo "   포트 3000: $(lsof -ti:3000 2>/dev/null | wc -l) 프로세스"
    exit 1
fi 