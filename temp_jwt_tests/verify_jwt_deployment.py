#!/usr/bin/env python3
"""JWT 및 데이터베이스 배포 상태 상세 검증"""

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

print(f"{BLUE}🔍 JWT 및 데이터베이스 연결 상세 검증{RESET}")
print("=" * 60)

# 1. 헬스체크
print(f"\n{BLUE}1. 헬스체크{RESET}")
try:
    response = requests.get(f"{BACKEND_URL}/api/health")
    print(f"상태 코드: {response.status_code}")
    if response.status_code == 200:
        print(f"{GREEN}✅ 백엔드 서버 정상 작동{RESET}")
    else:
        print(f"{RED}❌ 백엔드 서버 문제{RESET}")
except Exception as e:
    print(f"{RED}❌ 연결 실패: {e}{RESET}")

# 2. 인증 엔드포인트 확인
print(f"\n{BLUE}2. 인증 엔드포인트 확인{RESET}")
auth_endpoints = [
    '/api/auth/register',
    '/api/auth/login',
    '/api/user/profile',
    '/api/auth/status'
]

for endpoint in auth_endpoints:
    try:
        response = requests.options(f"{BACKEND_URL}{endpoint}")
        if response.status_code in [200, 204]:
            print(f"{GREEN}✅ {endpoint} - 엔드포인트 존재{RESET}")
        else:
            print(f"{RED}❌ {endpoint} - 상태 코드: {response.status_code}{RESET}")
    except Exception as e:
        print(f"{RED}❌ {endpoint} - 오류: {e}{RESET}")

# 3. 테스트 사용자로 회원가입
print(f"\n{BLUE}3. 회원가입 테스트{RESET}")
test_user = {
    "email": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
    "password": "TestPassword123!",
    "username": f"test_{datetime.now().strftime('%H%M%S')}"
}

try:
    response = requests.post(f"{BACKEND_URL}/api/auth/register", json=test_user)
    print(f"상태 코드: {response.status_code}")
    
    if response.status_code == 201:
        print(f"{GREEN}✅ 회원가입 성공{RESET}")
        data = response.json()
        print(f"응답 데이터 키: {list(data.keys())}")
        
        # 토큰 확인
        if 'tokens' in data:
            access_token = data['tokens'].get('access_token')
            if access_token:
                print(f"{GREEN}✅ JWT 토큰 발급됨{RESET}")
                
                # 4. JWT로 프로필 조회
                print(f"\n{BLUE}4. JWT 인증 테스트{RESET}")
                headers = {"Authorization": f"Bearer {access_token}"}
                profile_response = requests.get(f"{BACKEND_URL}/api/user/profile", headers=headers)
                
                print(f"프로필 조회 상태 코드: {profile_response.status_code}")
                if profile_response.status_code == 200:
                    print(f"{GREEN}✅ JWT 인증 성공! 로그인 시스템 정상 작동{RESET}")
                    print(f"{GREEN}✅ 데이터베이스 연결 정상{RESET}")
                else:
                    print(f"{RED}❌ JWT 인증 실패{RESET}")
                    print(f"응답: {profile_response.text[:200]}")
        else:
            print(f"{YELLOW}⚠️ 토큰이 응답에 없음{RESET}")
    else:
        print(f"{RED}❌ 회원가입 실패{RESET}")
        print(f"응답: {response.text[:200]}")
        
except Exception as e:
    print(f"{RED}❌ 요청 실패: {e}{RESET}")

# 5. 결론
print(f"\n{BLUE}=" * 60)
print("📊 최종 진단{RESET}")
print("=" * 60)

print("""
🔍 확인 필요 사항:
1. Railway Dashboard에서 환경변수 확인:
   - JWT_SECRET_KEY=nongbuxx-jwt-secret-key-2025-fixed-for-production
   - DATABASE_URL (자동 설정됨)
   - ENCRYPTION_KEY=32-character-encryption-key-here

2. 배포 로그 확인:
   - railway logs 명령으로 최근 로그 확인
   - 'Starting Flask app' 메시지 확인
   - 오류 메시지 확인

3. 재배포가 필요한 경우:
   - railway up --force
""")

print("\n" + "=" * 60) 