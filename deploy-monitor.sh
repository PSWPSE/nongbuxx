#!/bin/bash

# 📊 NONGBUXX 실시간 배포 모니터링 스크립트
# 배포 상태를 실시간으로 모니터링하고 문제 발생 시 알림

set -e

echo "📊 NONGBUXX 실시간 배포 모니터링"
echo "================================"

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

print_status() {
    local timestamp=$(date '+%H:%M:%S')
    printf "${BLUE}[$timestamp]${NC} $1\n"
}

check_service() {
    local service=$1
    local url=$2
    local expected=$3
    local timeout=${4:-10}
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $timeout "$url" 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected" ]; then
        printf "${GREEN}✅${NC}"
        return 0
    else
        printf "${RED}❌${NC}"
        return 1
    fi
}

check_api_function() {
    local response=$(curl -s --max-time 15 -X POST https://nongbuxxbackend-production.up.railway.app/api/generate \
        -H "Content-Type: application/json" \
        -d '{"url":"test","api_provider":"anthropic","api_key":"sk-ant-test","content_type":"x"}' \
        2>/dev/null || echo "{}")
    
    if [[ "$response" == *"INVALID_URL"* ]] || [[ "$response" == *"INVALID_ANTHROPIC_KEY"* ]]; then
        printf "${GREEN}✅${NC}"
        return 0
    else
        printf "${RED}❌${NC}"
        return 1
    fi
}

# 모니터링 파라미터
MONITOR_DURATION=${1:-300}  # 기본 5분 (300초)
CHECK_INTERVAL=${2:-30}     # 기본 30초 간격

print_color "⏱️  모니터링 시간: ${MONITOR_DURATION}초 ($(($MONITOR_DURATION / 60))분)" $BLUE
print_color "🔄 체크 간격: ${CHECK_INTERVAL}초" $BLUE
print_color "🛑 중단하려면 Ctrl+C를 누르세요" $YELLOW
echo ""

# 헤더 출력
printf "%-8s %-12s %-12s %-12s %-15s\n" "시간" "백엔드" "프론트엔드" "API기능" "상태"
echo "================================================================"

# 통계 변수
TOTAL_CHECKS=0
BACKEND_FAILURES=0
FRONTEND_FAILURES=0
API_FAILURES=0
START_TIME=$(date +%s)

# 모니터링 루프
while [ $(($(date +%s) - START_TIME)) -lt $MONITOR_DURATION ]; do
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    TIMESTAMP=$(date '+%H:%M:%S')
    
    # 서비스 상태 체크
    printf "%-8s " "$TIMESTAMP"
    
    # 백엔드 체크
    if check_service "Backend" "https://nongbuxxbackend-production.up.railway.app/api/health" "200" 10; then
        printf "%-12s " "정상"
    else
        printf "%-12s " "실패"
        BACKEND_FAILURES=$((BACKEND_FAILURES + 1))
    fi
    
    # 프론트엔드 체크
    if check_service "Frontend" "https://nongbuxxfrontend.vercel.app/" "200" 10; then
        printf "%-12s " "정상"
    else
        printf "%-12s " "실패"
        FRONTEND_FAILURES=$((FRONTEND_FAILURES + 1))
    fi
    
    # API 기능 체크
    if check_api_function; then
        printf "%-12s " "정상"
    else
        printf "%-12s " "실패"
        API_FAILURES=$((API_FAILURES + 1))
    fi
    
    # 전체 상태
    if [ $BACKEND_FAILURES -eq 0 ] && [ $FRONTEND_FAILURES -eq 0 ] && [ $API_FAILURES -eq 0 ]; then
        printf "${GREEN}%-15s${NC}" "모든 서비스 정상"
    else
        printf "${RED}%-15s${NC}" "일부 서비스 실패"
    fi
    
    echo ""
    
    # 연속 실패 감지 및 알림
    if [ $((TOTAL_CHECKS % 3)) -eq 0 ]; then  # 3번째 체크마다
        if [ $BACKEND_FAILURES -gt 1 ]; then
            print_color "🚨 백엔드 연속 실패 감지! 확인 필요" $RED
        fi
        if [ $FRONTEND_FAILURES -gt 1 ]; then
            print_color "🚨 프론트엔드 연속 실패 감지! 확인 필요" $RED
        fi
        if [ $API_FAILURES -gt 1 ]; then
            print_color "🚨 API 기능 연속 실패 감지! 확인 필요" $RED
        fi
    fi
    
    sleep $CHECK_INTERVAL
done

# 모니터링 완료 리포트
echo ""
echo "================================================================"
print_color "📊 모니터링 완료 리포트" $BOLD$BLUE
echo "================================================================"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

print_color "⏱️  모니터링 시간: ${DURATION}초 ($(($DURATION / 60))분 $(($DURATION % 60))초)" $BLUE
print_color "🔢 총 체크 횟수: $TOTAL_CHECKS" $BLUE
echo ""

# 성공률 계산
BACKEND_SUCCESS_RATE=$(( (TOTAL_CHECKS - BACKEND_FAILURES) * 100 / TOTAL_CHECKS ))
FRONTEND_SUCCESS_RATE=$(( (TOTAL_CHECKS - FRONTEND_FAILURES) * 100 / TOTAL_CHECKS ))
API_SUCCESS_RATE=$(( (TOTAL_CHECKS - API_FAILURES) * 100 / TOTAL_CHECKS ))

print_color "📈 서비스별 성공률:" $BLUE
if [ $BACKEND_SUCCESS_RATE -ge 95 ]; then
    print_color "  • 백엔드: ${BACKEND_SUCCESS_RATE}% (${BACKEND_FAILURES}/${TOTAL_CHECKS} 실패)" $GREEN
elif [ $BACKEND_SUCCESS_RATE -ge 80 ]; then
    print_color "  • 백엔드: ${BACKEND_SUCCESS_RATE}% (${BACKEND_FAILURES}/${TOTAL_CHECKS} 실패)" $YELLOW
else
    print_color "  • 백엔드: ${BACKEND_SUCCESS_RATE}% (${BACKEND_FAILURES}/${TOTAL_CHECKS} 실패)" $RED
fi

if [ $FRONTEND_SUCCESS_RATE -ge 95 ]; then
    print_color "  • 프론트엔드: ${FRONTEND_SUCCESS_RATE}% (${FRONTEND_FAILURES}/${TOTAL_CHECKS} 실패)" $GREEN
elif [ $FRONTEND_SUCCESS_RATE -ge 80 ]; then
    print_color "  • 프론트엔드: ${FRONTEND_SUCCESS_RATE}% (${FRONTEND_FAILURES}/${TOTAL_CHECKS} 실패)" $YELLOW
else
    print_color "  • 프론트엔드: ${FRONTEND_SUCCESS_RATE}% (${FRONTEND_FAILURES}/${TOTAL_CHECKS} 실패)" $RED
fi

if [ $API_SUCCESS_RATE -ge 95 ]; then
    print_color "  • API 기능: ${API_SUCCESS_RATE}% (${API_FAILURES}/${TOTAL_CHECKS} 실패)" $GREEN
elif [ $API_SUCCESS_RATE -ge 80 ]; then
    print_color "  • API 기능: ${API_SUCCESS_RATE}% (${API_FAILURES}/${TOTAL_CHECKS} 실패)" $YELLOW
else
    print_color "  • API 기능: ${API_SUCCESS_RATE}% (${API_FAILURES}/${TOTAL_CHECKS} 실패)" $RED
fi

echo ""

# 권장사항
if [ $BACKEND_FAILURES -gt 0 ] || [ $FRONTEND_FAILURES -gt 0 ] || [ $API_FAILURES -gt 0 ]; then
    print_color "🔧 권장사항:" $YELLOW
    
    if [ $BACKEND_FAILURES -gt 2 ]; then
        print_color "  • 백엔드 재배포: railway up --force" $NC
        print_color "  • 백엔드 로그 확인: railway logs -n 100" $NC
    fi
    
    if [ $FRONTEND_FAILURES -gt 2 ]; then
        print_color "  • 프론트엔드 재배포: ./deploy-quick.sh" $NC
        print_color "  • Vercel 대시보드 확인: vercel ls" $NC
    fi
    
    if [ $API_FAILURES -gt 2 ]; then
        print_color "  • 전체 재배포: ./deploy-all.sh \"fix: 모니터링 후 수정\"" $NC
        print_color "  • 롤백 고려: ./deploy-rollback.sh" $NC
    fi
else
    print_color "🎉 모든 서비스가 안정적으로 작동하고 있습니다!" $GREEN
fi

echo ""
print_color "💡 추가 명령어:" $BLUE
print_color "  • 현재 상태 확인: ./deploy-status.sh" $NC
print_color "  • 연속 모니터링: ./deploy-monitor.sh 600 20  # 10분간 20초 간격" $NC
print_color "  • Railway 로그: railway logs -f" $NC
