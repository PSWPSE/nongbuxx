#!/usr/bin/env python3
"""JWT 문제 해결 확인"""

import requests
import time
from datetime import datetime

BACKEND_URL = "https://nongbuxxbackend-production.up.railway.app"

print("🔍 JWT 문제 해결 확인")
print("=" * 50)
print("⚠️  Railway Dashboard에서 환경변수를 설정하셨나요?")
print("   JWT_SECRET_KEY=nongbuxx-jwt-secret-key-2025-fixed-for-production")
print("   ENCRYPTION_KEY=32-character-encryption-key-here")
print("=" * 50)

input("\n환경변수 설정 후 Enter를 누르세요...")

print("\n⏳ 재배포 대기 중 (1분)...")
time.sleep(60)

# 테스트
test_user = {
    "email": f"fix_test_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
    "password": "TestPassword123!"
}

print("\n🧪 테스트 시작...")

# 1. 회원가입
register = requests.post(f"{BACKEND_URL}/api/auth/register", json=test_user)
if register.status_code == 201:
    print("✅ 회원가입 성공")
    access_token = register.json()['tokens']['access_token']
    
    # 2. JWT 인증 테스트
    headers = {"Authorization": f"Bearer {access_token}"}
    profile = requests.get(f"{BACKEND_URL}/api/user/profile", headers=headers)
    
    if profile.status_code == 200:
        print("✅ JWT 인증 성공!")
        print("\n🎉 축하합니다! JWT 문제가 해결되었습니다!")
        print("✅ 데이터베이스 연결 정상")
        print("✅ 로그인 시스템 정상 작동")
    else:
        print("❌ JWT 인증 실패")
        print("⚠️  Railway Dashboard에서 환경변수를 다시 확인하세요")
else:
    print("❌ 회원가입 실패")

print("\n" + "=" * 50) 