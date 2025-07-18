#!/bin/bash

# 로컬 .env 파일의 보안 키만 업데이트
echo "🔧 .env 파일의 보안 키 업데이트 중..."

# 백업 생성
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# macOS sed 명령어로 보안 키 업데이트
sed -i '' 's/SECRET_KEY=.*/SECRET_KEY=dev-secret-key-for-local-development-only/' .env
sed -i '' 's/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=dev-jwt-secret-key-for-local-only/' .env
sed -i '' 's/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=dev32charactersencryptionkeyhere/' .env

echo "✅ 보안 키 업데이트 완료!"
echo ""
echo "📋 업데이트된 내용:"
grep -E "SECRET_KEY|JWT_SECRET_KEY|ENCRYPTION_KEY" .env 