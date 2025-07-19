#!/usr/bin/env python3
"""JWT 수정 후 최종 테스트"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://nongbuxxbackend-production.up.railway.app"

# 색상 코드
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

print(f"{YELLOW}🎯 JWT 최종 테스트{RESET}")
print("=" * 50)

# 테스트 사용자
test_user = {
    "email": f"jwt_final_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
    "password": "FinalJWT123!",
    "username": "jwtfinal"
}

# 1. 회원가입
print(f"\n{BLUE}1. 회원가입 테스트{RESET}")
register = requests.post(f"{BACKEND_URL}/api/auth/register", json=test_user)
print(f"상태: {register.status_code}")

if register.status_code == 201:
    data = register.json()
    access_token = data.get('tokens', {}).get('access_token')
    print(f"{GREEN}✓ 회원가입 성공{RESET}")
    
    # 2. 프로필 조회
    print(f"\n{BLUE}2. 프로필 조회 테스트{RESET}")
    headers = {"Authorization": f"Bearer {access_token}"}
    profile = requests.get(f"{BACKEND_URL}/api/user/profile", headers=headers)
    print(f"상태: {profile.status_code}")
    
    if profile.status_code == 200:
        print(f"{GREEN}✓ JWT 인증 성공!{RESET}")
        print(f"사용자: {profile.json()['user']['email']}")
        
        # 3. API 키 저장 테스트
        print(f"\n{BLUE}3. API 키 저장 테스트{RESET}")
        api_key_data = {
            "provider": "openai",
            "api_key": "sk-test-final-key"
        }
        api_response = requests.post(
            f"{BACKEND_URL}/api/user/api-keys",
            headers=headers,
            json=api_key_data
        )
        print(f"상태: {api_response.status_code}")
        
        if api_response.status_code == 200:
            print(f"{GREEN}✓ API 키 저장 성공{RESET}")
        else:
            print(f"{RED}✗ API 키 저장 실패{RESET}")
            print(api_response.text)
    else:
        print(f"{RED}✗ JWT 인증 실패{RESET}")
        print(f"에러: {profile.json()}")
        
        # /api/auth/me 테스트
        me = requests.get(f"{BACKEND_URL}/api/auth/me", headers=headers)
        print(f"\n/api/auth/me 테스트: {me.status_code}")
else:
    print(f"{RED}✗ 회원가입 실패{RESET}")
    print(register.text)

print("\n" + "=" * 50)
print(f"{BLUE}📊 최종 결과:{RESET}")

# 결과 요약
if register.status_code == 201 and profile.status_code == 200:
    print(f"{GREEN}✅ JWT 문제 해결 완료!{RESET}")
    print("\n다음 단계:")
    print("1. 프론트엔드에서 로그인 테스트")
    print("2. API 키 관리 기능 확인")
    print("3. 콘텐츠 생성 연동 확인")
else:
    print(f"{RED}❌ JWT 문제가 계속됨{RESET}")
    print("\n추가 확인 필요:")
    print("1. Railway 환경변수 재확인")
    print("2. 서비스 재배포")
    print("3. PostgreSQL 연결 고려") 