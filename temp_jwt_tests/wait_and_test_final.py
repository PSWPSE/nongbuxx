#!/usr/bin/env python3
"""Railway 재배포 완료 후 최종 JWT 테스트"""

import requests
import time
from datetime import datetime

BACKEND_URL = "https://nongbuxxbackend-production.up.railway.app"

print("🚀 Railway 재배포 중...")
print("=" * 60)
print("✅ 올바른 환경변수가 설정되었습니다:")
print("   JWT_SECRET_KEY=MD1mIiR5pCnhpjhTNXklCY34gbgiPiv0mKsP6DHz_CU")
print("   ENCRYPTION_KEY=gtUN9kBcHB1fBHJLxdgvqNF0xIcQOnZE")
print("=" * 60)

# 재배포 완료 대기 (2분 30초)
wait_time = 150
print(f"\n⏳ Railway 재배포 대기 중 ({wait_time}초)...")
print("💡 이 시간 동안 Railway Dashboard에서 빌드 상태를 확인할 수 있습니다.")

for i in range(wait_time, 0, -1):
    mins = i // 60
    secs = i % 60
    print(f"\r남은 시간: {mins}분 {secs}초  ", end='', flush=True)
    time.sleep(1)

print("\n\n✅ 대기 완료! 테스트를 시작합니다...")

# 테스트 사용자 생성
test_user = {
    "email": f"working_test_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
    "password": "WorkingTest123!",
    "username": f"working_{datetime.now().strftime('%H%M%S')}"
}

# 1. 헬스체크
print("\n1️⃣ 서버 상태 확인")
health = requests.get(f"{BACKEND_URL}/api/health")
if health.status_code == 200:
    print("✅ 서버 정상 작동")
else:
    print("❌ 서버 응답 없음")

# 2. 회원가입
print("\n2️⃣ 회원가입 테스트")
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
        
        print("\n" + "="*60)
        print("🎉 축하합니다! JWT 문제가 완전히 해결되었습니다! 🎉")
        print("="*60)
        print("\n✅ 해결된 문제:")
        print("  - JWT 토큰 생성 및 검증")
        print("  - 데이터베이스 연결")
        print("  - 로그인 시스템 전체")
        
        print("\n📝 문제 원인:")
        print("  - 처음 생성한 보안 키와 코드의 기본값이 달랐음")
        print("  - Railway 환경변수가 올바른 키로 설정되지 않았음")
        
        print("\n💡 교훈:")
        print("  - 환경변수는 항상 일관성 있게 관리해야 함")
        print("  - 개발/운영 환경의 설정값을 문서화해야 함")
        print("  - 기본값은 절대 운영에서 사용하면 안 됨")
        
    else:
        print(f"❌ JWT 인증 실패 (상태 코드: {profile.status_code})")
        print(f"응답: {profile.text[:200]}")
        print("\n⚠️  문제가 계속되면 Railway 로그를 확인하세요.")
else:
    print(f"❌ 회원가입 실패: {register.status_code}")
    print(register.text[:200])

print("\n" + "=" * 60) 