#!/usr/bin/env python3
"""JWT 헤더 및 설정 디버깅"""

import requests
import json
import base64

BACKEND_URL = "https://nongbuxxbackend-production.up.railway.app"

print("🔍 JWT 헤더 및 설정 확인")
print("=" * 50)

# 1. 서버 설정 확인
print("\n1. 서버 설정 확인...")
response = requests.get(f"{BACKEND_URL}/api/health")
print(f"Health Check: {response.status_code}")

# 2. JWT 토큰 디코딩 테스트
print("\n2. JWT 토큰 구조 분석...")

# 간단한 테스트 로그인
test_user = {
    "email": "jwt_header_test@test.com",
    "password": "TestPassword123!"
}

# 회원가입
register_response = requests.post(
    f"{BACKEND_URL}/api/auth/register",
    json=test_user
)

if register_response.status_code == 201:
    data = register_response.json()
    access_token = data.get('tokens', {}).get('access_token', '')
    
    print(f"\n토큰 받음: {access_token[:50]}...")
    
    # JWT 토큰 구조 분석 (header.payload.signature)
    parts = access_token.split('.')
    if len(parts) == 3:
        try:
            # Header 디코딩
            header = base64.urlsafe_b64decode(parts[0] + '==')
            print(f"\nJWT Header: {header.decode('utf-8')}")
            
            # Payload 디코딩 (시그니처 검증 없이)
            payload = base64.urlsafe_b64decode(parts[1] + '==')
            print(f"JWT Payload: {payload.decode('utf-8')}")
        except Exception as e:
            print(f"디코딩 에러: {e}")
    
    # 3. 다양한 헤더 형식 테스트
    print("\n3. Authorization 헤더 형식 테스트...")
    
    # 올바른 형식
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BACKEND_URL}/api/user/profile", headers=headers)
    print(f"Bearer 형식: {response.status_code} - {response.json().get('error', 'Success')}")
    
    # Content-Type 추가
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"{BACKEND_URL}/api/user/profile", headers=headers)
    print(f"With Content-Type: {response.status_code}")
    
    # OPTIONS 요청 테스트
    print("\n4. CORS Preflight 테스트...")
    headers = {
        "Origin": "https://nongbuxxfrontend.vercel.app",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "Authorization"
    }
    response = requests.options(f"{BACKEND_URL}/api/user/profile", headers=headers)
    print(f"OPTIONS: {response.status_code}")
    print(f"Allow-Headers: {response.headers.get('Access-Control-Allow-Headers')}")
else:
    print(f"회원가입 실패: {register_response.status_code}")
    print(register_response.text)

print("\n" + "=" * 50) 