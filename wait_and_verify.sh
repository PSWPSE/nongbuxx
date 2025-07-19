#!/bin/bash

echo "⏳ Railway 배포 대기 중... (2분)"
echo "이 시간 동안 Railway Dashboard에서 환경변수를 확인하세요:"
echo ""
echo "1. JWT_SECRET_KEY=nongbuxx-jwt-secret-key-2025-fixed-for-production"
echo "2. ENCRYPTION_KEY=32-character-encryption-key-here"
echo ""

# 프로그레스 바 표시
for i in {1..120}; do
    printf "\r진행률: [%-50s] %d%%" $(printf '#%.0s' $(seq 1 $((i/2)))) $((i*100/120))
    sleep 1
done
echo ""

echo "✅ 대기 완료. 검증을 시작합니다..."
python3 verify_jwt_deployment.py 