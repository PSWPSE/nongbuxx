#!/bin/bash

# 🚀 NONGBUXX 안전 재시작 스크립트
# 이 스크립트는 반복적인 서버 중단 문제를 방지하기 위해 만들어졌습니다

echo "🛡️ NONGBUXX 안전 재시작 시작..."

# 1. 기존 프로세스 완전 정리
echo "🧹 기존 프로세스 정리 중..."
lsof -ti:8080 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
pkill -f "python.*http.server" 2>/dev/null || true
pkill -f "python3.*app.py" 2>/dev/null || true

# 2. 포트 해제 대기
echo "⏳ 포트 해제 대기 중..."
sleep 3

# 3. 메모리 정리
echo "🧹 메모리 정리 중..."
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# 4. 시스템 리소스 체크
echo "📊 시스템 리소스 체크..."
if command -v python3 -c "import psutil; print(f'메모리: {psutil.virtual_memory().percent:.1f}%')" 2>/dev/null; then
    python3 -c "import psutil; mem=psutil.virtual_memory().percent; print(f'메모리 사용률: {mem:.1f}%'); exit(1) if mem > 90 else exit(0)"
    if [ $? -ne 0 ]; then
        echo "⚠️ 메모리 사용률이 높습니다. 대기 중..."
        sleep 5
    fi
fi

# 5. 백엔드 서버 시작
echo "🚀 백엔드 서버 시작 중..."
nohup python3 app.py > nongbuxx_backend.log 2>&1 &
BACKEND_PID=$!

# 백엔드 시작 확인
sleep 5
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ 백엔드 서버 시작 성공 (PID: $BACKEND_PID)"
else
    echo "❌ 백엔드 서버 시작 실패"
    exit 1
fi

# 6. 프론트엔드 서버 시작
echo "🌐 프론트엔드 서버 시작 중..."
cd frontend
nohup python -m http.server 3000 > ../nongbuxx_frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# 프론트엔드 시작 확인
sleep 3
if ps -p $FRONTEND_PID > /dev/null; then
    echo "✅ 프론트엔드 서버 시작 성공 (PID: $FRONTEND_PID)"
else
    echo "❌ 프론트엔드 서버 시작 실패"
    exit 1
fi

# 7. 헬스체크
echo "🔍 서비스 상태 확인 중..."
sleep 5

# 백엔드 헬스체크
if curl -s http://localhost:8080/api/health > /dev/null; then
    echo "✅ 백엔드 헬스체크 통과"
else
    echo "❌ 백엔드 헬스체크 실패"
    exit 1
fi

# 프론트엔드 연결 확인
if curl -s -I http://localhost:3000 > /dev/null; then
    echo "✅ 프론트엔드 연결 확인"
else
    echo "❌ 프론트엔드 연결 실패"
    exit 1
fi

# 8. 완료 메시지
echo ""
echo "🎉 NONGBUXX 시스템이 성공적으로 시작되었습니다!"
echo ""
echo "📍 서비스 정보:"
echo "   • 백엔드: http://localhost:8080 (PID: $BACKEND_PID)"
echo "   • 프론트엔드: http://localhost:3000 (PID: $FRONTEND_PID)"
echo "   • 로그: nongbuxx_backend.log, nongbuxx_frontend.log"
echo ""
echo "🛑 서비스 중지: ./safe_stop.sh"
echo "📊 상태 확인: curl http://localhost:8080/api/health"
echo ""
echo "🚀 웹 인터페이스에 접속하여 사용하세요: http://localhost:3000" 