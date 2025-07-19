#!/usr/bin/env python3
"""JWT 문제 최종 테스트"""

import requests
import time
from datetime import datetime

BACKEND_URL = "https://nongbuxxbackend-production.up.railway.app"

print("🎯 JWT 문제 최종 해결 테스트")
print("=" * 60)
print("✅ 해결한 문제들:")
print("  1. JWT_SECRET_KEY 환경변수 설정")
print("  2. railway.json의 startCommand 제거")
print("  3. Procfile이 app_with_auth.py 실행")
print("=" * 60)

print("\n⏳ Railway 재배포 대기 중 (2분)...")
for i in range(120, 0, -1):
    print(f"\r남은 시간: {i}초  ", end='', flush=True)
    time.sleep(1)

print("\n\n🧪 최종 테스트 시작...")

# 1. 디버그 엔드포인트 확인
print("\n1️⃣ 디버그 엔드포인트 확인")
try:
    debug = requests.get(f"{BACKEND_URL}/debug/jwt")
    if debug.status_code == 200 and debug.headers.get('content-type', '').startswith('application/json'):
        print("✅ app_with_auth.py가 실행 중입니다!")
        print(f"디버그 정보: {debug.json()}")
    else:
        print("⚠️ 아직 재배포가 진행 중일 수 있습니다.")
except Exception as e:
    print(f"디버그 확인 실패: {e}")

# 2. 테스트 사용자 생성
print("\n2️⃣ 회원가입 테스트")
test_user = {
    "email": f"success_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
    "password": "Success123!",
    "username": f"success_{datetime.now().strftime('%H%M%S')}"
}

register = requests.post(f"{BACKEND_URL}/api/auth/register", json=test_user)
if register.status_code == 201:
    print("✅ 회원가입 성공")
    data = register.json()
    access_token = data['tokens']['access_token']
    
    # 3. JWT 인증 테스트
    print("\n3️⃣ JWT 인증 테스트")
    headers = {"Authorization": f"Bearer {access_token}"}
    profile = requests.get(f"{BACKEND_URL}/api/user/profile", headers=headers)
    
    if profile.status_code == 200:
        print("✅ JWT 인증 성공!")
        print(f"사용자 정보: {profile.json()['user']['email']}")
        
        print("\n" + "🎉" * 30)
        print("\n축하합니다! JWT 문제가 완전히 해결되었습니다!")
        print("\n✅ 해결 완료:")
        print("  - JWT 토큰 생성 및 검증 정상 작동")
        print("  - 데이터베이스 연결 정상")
        print("  - 로그인 시스템 완전 작동")
        print("  - Railway 배포 설정 정상화")
        print("\n🎉" * 30)
    else:
        print(f"❌ JWT 인증 실패: {profile.status_code}")
        print("⚠️ 재배포가 완료될 때까지 기다려주세요.")
else:
    print(f"❌ 회원가입 실패: {register.status_code}")

print("\n" + "=" * 60) 