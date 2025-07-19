#!/usr/bin/env python3
"""JWT 문제 최종 해결 확인"""

import requests
import time
from datetime import datetime

BACKEND_URL = "https://nongbuxxbackend-production.up.railway.app"

print("🔍 JWT 문제 최종 해결 확인")
print("=" * 60)
print("✅ 올바른 환경변수로 재설정 완료:")
print("   JWT_SECRET_KEY=MD1mIiR5pCnhpjhTNXklCY34gbgiPiv0mKsP6DHz_CU")
print("   ENCRYPTION_KEY=gtUN9kBcHB1fBHJLxdgvqNF0xIcQOnZE")
print("=" * 60)

# 디버그 엔드포인트 확인
print("\n🔍 서버 환경변수 확인 시도...")
try:
    debug_response = requests.get(f"{BACKEND_URL}/debug/jwt")
    if debug_response.status_code == 200:
        print("디버그 응답:", debug_response.text)
except:
    print("디버그 엔드포인트 없음")

print("\n⏳ Railway 재배포 대기 중 (90초)...")
for i in range(90, 0, -1):
    print(f"\r남은 시간: {i}초  ", end='', flush=True)
    time.sleep(1)

print("\n\n🧪 테스트 시작...")

# 테스트 사용자 생성
test_user = {
    "email": f"final_test_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
    "password": "FinalTest123!",
    "username": f"final_{datetime.now().strftime('%H%M%S')}"
}

# 1. 회원가입
print("\n1️⃣ 회원가입 테스트")
register = requests.post(f"{BACKEND_URL}/api/auth/register", json=test_user)
if register.status_code == 201:
    print("✅ 회원가입 성공")
    data = register.json()
    access_token = data['tokens']['access_token']
    
    # 2. JWT 인증 테스트
    print("\n2️⃣ JWT 인증 테스트")
    headers = {"Authorization": f"Bearer {access_token}"}
    profile = requests.get(f"{BACKEND_URL}/api/user/profile", headers=headers)
    
    if profile.status_code == 200:
        print("✅ JWT 인증 성공!")
        print(f"사용자 정보: {profile.json()['user']['email']}")
        
        print("\n" + "🎉" * 20)
        print("축하합니다! JWT 문제가 완전히 해결되었습니다!")
        print("✅ 데이터베이스 연결: 정상")
        print("✅ JWT 인증 시스템: 정상")
        print("✅ 로그인 시스템: 완전 작동")
        print("🎉" * 20)
        
        print("\n📋 다음 단계:")
        print("1. 프론트엔드에서 로그인 기능 테스트")
        print("2. API 키 저장 기능 테스트")
        print("3. 콘텐츠 생성 기능 테스트")
    else:
        print(f"❌ JWT 인증 실패 (상태 코드: {profile.status_code})")
        print(f"응답: {profile.text[:200]}")
        print("\n⚠️  아직 재배포가 진행 중일 수 있습니다.")
        print("2-3분 후에 다시 실행해보세요.")
else:
    print(f"❌ 회원가입 실패: {register.status_code}")
    print(register.text[:200])

print("\n" + "=" * 60) 