#!/usr/bin/env python3
"""JWT 문제 최종 검증"""

import requests
import time
from datetime import datetime

BACKEND_URL = "https://nongbuxxbackend-production.up.railway.app"

print("🎯 JWT 문제 최종 검증")
print("=" * 60)

print("⏳ Railway 재배포 완료 대기 중 (3분)...")
for i in range(180, 0, -1):
    mins = i // 60
    secs = i % 60
    print(f"\r남은 시간: {mins}분 {secs}초  ", end='', flush=True)
    time.sleep(1)

print("\n\n🔍 검증 시작...")

# 1. 디버그 확인
print("\n1️⃣ 서버 확인")
try:
    debug = requests.get(f"{BACKEND_URL}/debug/jwt", timeout=10)
    if debug.headers.get('content-type', '').startswith('application/json'):
        print("✅ app_with_auth.py가 실행 중입니다!")
        print(f"환경변수 상태: {debug.json()}")
    else:
        print("⚠️ 아직 app.py가 실행 중일 수 있습니다")
except:
    print("디버그 엔드포인트 확인 실패")

# 2. JWT 테스트
print("\n2️⃣ JWT 인증 테스트")
test_user = {
    "email": f"final_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
    "password": "Final123!"
}

register = requests.post(f"{BACKEND_URL}/api/auth/register", json=test_user)
if register.status_code == 201:
    print("✅ 회원가입 성공")
    token = register.json()['tokens']['access_token']
    
    headers = {"Authorization": f"Bearer {token}"}
    profile = requests.get(f"{BACKEND_URL}/api/user/profile", headers=headers)
    
    if profile.status_code == 200:
        print("✅ JWT 인증 성공!")
        print("\n🎉 축하합니다! 모든 문제가 해결되었습니다!")
        print("✅ JWT 토큰 생성 및 검증: 정상")
        print("✅ 데이터베이스 연결: 정상")
        print("✅ Railway 배포: 정상")
    else:
        print(f"❌ JWT 인증 실패: {profile.status_code}")
else:
    print(f"❌ 회원가입 실패: {register.status_code}")
    print("Railway Dashboard의 Logs를 확인해주세요")

print("\n" + "=" * 60) 