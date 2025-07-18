#!/usr/bin/env python3
"""Railway 환경 변수 및 앱 상태 확인"""

import requests
import json

BACKEND_URL = "https://nongbuxxbackend-production.up.railway.app"

print("🔍 Railway 백엔드 상태 확인")
print("=" * 50)

# 1. 기본 API 테스트
print("\n1. 기본 API 작동 확인...")
response = requests.post(
    f"{BACKEND_URL}/api/generate",
    json={
        "url": "https://example.com",
        "content_type": "standard",
        "api_provider": "anthropic",
        "api_key": "test-key"
    }
)
print(f"기존 /api/generate: {response.status_code}")

# 2. 인증 API 존재 확인
print("\n2. 인증 API 엔드포인트 확인...")
endpoints = [
    "/api/auth/register",
    "/api/auth/login", 
    "/api/user/profile",
    "/api/v2/generate"
]

for endpoint in endpoints:
    response = requests.options(f"{BACKEND_URL}{endpoint}")
    print(f"{endpoint}: {response.status_code}")

# 3. 디버그 엔드포인트 생성 (임시)
print("\n3. 서버 정보 확인...")

# 회원가입으로 간접 확인
response = requests.post(
    f"{BACKEND_URL}/api/auth/register",
    json={
        "email": "env_test@test.com",
        "password": "Test123!",
        "username": "envtest"
    }
)

if response.status_code == 201:
    print("✅ 인증 시스템 활성화됨 (app_with_auth.py 실행 중)")
elif response.status_code == 404:
    print("❌ 인증 시스템 비활성화 (기존 app.py 실행 중)")
else:
    print(f"⚠️  예상치 못한 응답: {response.status_code}")
    print(response.text[:200])

print("\n" + "=" * 50)
print("결론: Railway에서 실행 중인 앱을 확인하세요!")
print("railway.json의 startCommand 확인 필요") 