#!/bin/bash

echo "🚀 Railway 재배포 및 JWT 문제 해결 확인"
echo "=" * 50

echo "✅ 환경변수가 설정되었습니다!"
echo "   JWT_SECRET_KEY=nongbuxx-jwt-secret-key-2025-fixed-for-production"
echo "   ENCRYPTION_KEY=32-character-encryption-key-here"

echo ""
echo "⏳ Railway가 자동으로 재배포를 시작합니다... (2-3분 소요)"
echo ""

# 60초 대기
for i in {1..60}; do
    printf "\r대기 중: [%-30s] %d초" $(printf '#%.0s' $(seq 1 $((i/2)))) $i
    sleep 1
done
echo ""

echo ""
echo "🧪 JWT 문제 해결 확인 중..."
python3 verify_jwt_deployment.py 