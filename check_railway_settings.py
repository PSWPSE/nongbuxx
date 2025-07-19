#!/usr/bin/env python3
"""Railway 설정 확인 체크리스트"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://nongbuxxbackend-production.up.railway.app"

print("🚂 Railway 설정 확인 체크리스트")
print("=" * 60)
print("이 스크립트를 실행하면서 Railway Dashboard를 함께 확인하세요.")
print("=" * 60)

# 1. 서버 응답 확인
print("\n1️⃣ 서버 응답 확인")
try:
    response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
    print(f"✅ 서버 응답: {response.status_code}")
except Exception as e:
    print(f"❌ 서버 응답 없음: {e}")

# 2. 디버그 엔드포인트 확인
print("\n2️⃣ 어떤 앱이 실행 중인지 확인")
try:
    debug = requests.get(f"{BACKEND_URL}/debug/jwt", timeout=10)
    content_type = debug.headers.get('content-type', '')
    
    if 'application/json' in content_type:
        print("✅ app_with_auth.py가 실행 중입니다!")
        data = debug.json()
        print(f"환경변수 설정: {data}")
    elif 'text/html' in content_type:
        print("❌ app.py가 실행 중입니다 (잘못됨)")
        print("⚠️  Railway Settings에서 Start Command가 비어있는지 확인하세요")
    else:
        print(f"⚠️  알 수 없는 응답: {content_type}")
except Exception as e:
    print(f"디버그 확인 실패: {e}")

# 3. Railway Dashboard 확인 가이드
print("\n" + "=" * 60)
print("📋 Railway Dashboard에서 확인할 사항:")
print("=" * 60)

print("\n✅ Variables 탭에서 확인:")
print("1. JWT_SECRET_KEY=MD1mIiR5pCnhpjhTNXklCY34gbgiPiv0mKsP6DHz_CU")
print("2. ENCRYPTION_KEY=gtUN9kBcHB1fBHJLxdgvqNF0xIcQOnZE")
print("3. SECRET_KEY=TiAnYueCfjXCIPcz8P7LPi8XDpC1LCpR1E5glf13wN4")
print("4. FLASK_ENV=production")
print("5. DATABASE_URL (자동 생성됨)")

print("\n✅ Settings 탭에서 확인:")
print("1. Start Command: 비어있어야 함")
print("2. Root Directory: / 또는 비어있음")

print("\n✅ Logs 탭에서 찾아볼 메시지:")
print("1. '[INFO] Starting gunicorn' (좋음)")
print("2. '* Running on' (나쁨 - 개발 서버)")

print("\n✅ Deployments 탭에서 확인:")
print("1. 최신 배포 상태: Success")
print("2. 배포 시간: 최근 (10분 이내)")

print("\n" + "=" * 60)

# 4. 최종 JWT 테스트
print("\n4️⃣ JWT 테스트")
test_user = {
    "email": f"railway_check_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
    "password": "RailwayCheck123!"
}

register = requests.post(f"{BACKEND_URL}/api/auth/register", json=test_user)
if register.status_code == 201:
    print("✅ 회원가입 성공")
    access_token = register.json()['tokens']['access_token']
    
    headers = {"Authorization": f"Bearer {access_token}"}
    profile = requests.get(f"{BACKEND_URL}/api/user/profile", headers=headers)
    
    if profile.status_code == 200:
        print("✅ JWT 인증 성공! 모든 설정이 올바릅니다!")
    else:
        print("❌ JWT 인증 실패")
        print("⚠️  환경변수를 다시 확인하세요")
else:
    print(f"❌ 회원가입 실패: {register.status_code}")

print("\n" + "=" * 60) 