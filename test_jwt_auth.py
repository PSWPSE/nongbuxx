#!/usr/bin/env python3
"""JWT 토큰 인증 디버깅"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://nongbuxxbackend-production.up.railway.app"

# 테스트 사용자
TEST_USER = {
    "email": f"jwt_test_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
    "password": "JwtTest123!",
    "username": "jwttest"
}

print("🧪 JWT 토큰 인증 테스트")
print("=" * 50)

# 1. 회원가입
print("\n1. 회원가입...")
response = requests.post(f"{BACKEND_URL}/api/auth/register", json=TEST_USER)
print(f"Status: {response.status_code}")
register_data = response.json()
print(f"Response: {json.dumps(register_data, indent=2)}")

if response.status_code != 201:
    print("❌ 회원가입 실패")
    exit(1)

# 토큰 추출
access_token = register_data.get('tokens', {}).get('access_token')
refresh_token = register_data.get('tokens', {}).get('refresh_token')

print(f"\n📋 토큰 정보:")
print(f"Access Token: {access_token[:20]}..." if access_token else "없음")
print(f"Refresh Token: {refresh_token[:20]}..." if refresh_token else "없음")

# 2. 프로필 조회 테스트 (여러 가지 헤더 형식)
print("\n2. 프로필 조회 테스트...")

# 테스트 1: Bearer 형식
print("\n테스트 1: Bearer 토큰 형식")
headers1 = {"Authorization": f"Bearer {access_token}"}
response1 = requests.get(f"{BACKEND_URL}/api/user/profile", headers=headers1)
print(f"Status: {response1.status_code}")
print(f"Headers sent: {headers1}")
print(f"Response: {response1.text[:200]}...")

# 테스트 2: 토큰만
print("\n테스트 2: 토큰만 전송")
headers2 = {"Authorization": access_token}
response2 = requests.get(f"{BACKEND_URL}/api/user/profile", headers=headers2)
print(f"Status: {response2.status_code}")

# 테스트 3: 헤더 없이
print("\n테스트 3: 헤더 없이")
response3 = requests.get(f"{BACKEND_URL}/api/user/profile")
print(f"Status: {response3.status_code}")

# 3. 로그인 후 재시도
print("\n3. 로그인 후 재시도...")
login_response = requests.post(
    f"{BACKEND_URL}/api/auth/login",
    json={"email": TEST_USER["email"], "password": TEST_USER["password"]}
)
print(f"Login Status: {login_response.status_code}")

if login_response.status_code == 200:
    login_data = login_response.json()
    new_access_token = login_data.get('tokens', {}).get('access_token')
    
    print("\n로그인 후 프로필 조회:")
    headers = {"Authorization": f"Bearer {new_access_token}"}
    profile_response = requests.get(f"{BACKEND_URL}/api/user/profile", headers=headers)
    print(f"Status: {profile_response.status_code}")
    if profile_response.status_code == 200:
        print(f"✅ 성공! Profile: {profile_response.json()}")
    else:
        print(f"❌ 실패. Response: {profile_response.text}")

print("\n" + "=" * 50)
print("테스트 완료") 