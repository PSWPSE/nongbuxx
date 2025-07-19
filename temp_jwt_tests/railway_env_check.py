#!/usr/bin/env python3
"""Railway 환경변수 설정 확인 스크립트"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://nongbuxxbackend-production.up.railway.app"

print("🔍 Railway 환경변수 설정 확인")
print("=" * 50)

# 색상 코드
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# 테스트용 사용자
test_user = {
    "email": f"railway_test_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
    "password": "RailwayTest123!",
    "username": "railwaytest"
}

print(f"\n{BLUE}1. 백엔드 연결 테스트{RESET}")
response = requests.get(f"{BACKEND_URL}/api/health")
if response.status_code == 200:
    print(f"{GREEN}✓ 백엔드 정상 작동{RESET}")
else:
    print(f"{RED}✗ 백엔드 연결 실패{RESET}")
    exit(1)

print(f"\n{BLUE}2. 회원가입 테스트{RESET}")
register = requests.post(f"{BACKEND_URL}/api/auth/register", json=test_user)
if register.status_code == 201:
    print(f"{GREEN}✓ 회원가입 성공{RESET}")
    data = register.json()
    access_token = data.get('tokens', {}).get('access_token')
    
    print(f"\n{BLUE}3. JWT 인증 테스트{RESET}")
    headers = {"Authorization": f"Bearer {access_token}"}
    profile = requests.get(f"{BACKEND_URL}/api/user/profile", headers=headers)
    
    if profile.status_code == 200:
        print(f"{GREEN}✓ JWT 인증 성공! 환경변수가 올바르게 설정됨{RESET}")
        print(f"\n{GREEN}🎉 축하합니다! 로그인 시스템이 완전히 작동합니다!{RESET}")
        print("\n다음 단계:")
        print("1. https://nongbuxxfrontend.vercel.app 에서 로그인 테스트")
        print("2. API 키 저장 및 콘텐츠 생성 테스트")
    else:
        print(f"{RED}✗ JWT 인증 실패{RESET}")
        print(f"\n{YELLOW}환경변수를 다시 확인하세요:{RESET}")
        print("JWT_SECRET_KEY=nongbuxx-jwt-secret-key-2025-fixed-for-production")
else:
    print(f"{RED}✗ 회원가입 실패{RESET}")

print("\n" + "=" * 50) 