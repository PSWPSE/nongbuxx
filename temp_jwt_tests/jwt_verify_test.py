#!/usr/bin/env python3
"""JWT 토큰 검증 문제 심층 분석"""

import requests
import jwt
import json
from datetime import datetime

BACKEND_URL = 'https://nongbuxxbackend-production.up.railway.app'

print("🔍 JWT 토큰 검증 문제 심층 분석")
print("=" * 60)

# 1. 로그인으로 토큰 생성
test_user = {
    'email': f'jwt_verify_test_{datetime.now().strftime("%Y%m%d%H%M%S")}@test.com',
    'password': 'TestVerify123!'
}

# 회원가입
register = requests.post(f'{BACKEND_URL}/api/auth/register', json=test_user)
if register.status_code == 201:
    print("✅ 회원가입 성공")
    
    # 로그인으로 새 토큰 받기
    login = requests.post(f'{BACKEND_URL}/api/auth/login', json={
        'email': test_user['email'],
        'password': test_user['password']
    })
    
    if login.status_code == 200:
        print("✅ 로그인 성공")
        login_data = login.json()
        login_token = login_data['tokens']['access_token']
        
        # 두 토큰 비교
        register_token = register.json()['tokens']['access_token']
        
        print(f"\n📊 토큰 비교:")
        print(f"회원가입 토큰 == 로그인 토큰: {register_token == login_token}")
        
        # 각 토큰으로 프로필 조회
        print(f"\n🧪 토큰별 프로필 조회:")
        
        # 회원가입 토큰
        headers1 = {'Authorization': f'Bearer {register_token}'}
        profile1 = requests.get(f'{BACKEND_URL}/api/user/profile', headers=headers1)
        print(f"회원가입 토큰: {profile1.status_code}")
        
        # 로그인 토큰
        headers2 = {'Authorization': f'Bearer {login_token}'}
        profile2 = requests.get(f'{BACKEND_URL}/api/user/profile', headers=headers2)
        print(f"로그인 토큰: {profile2.status_code}")
        
        # 잘못된 형식으로 요청
        print(f"\n🧪 다양한 인증 헤더 형식 테스트:")
        
        # Bearer 없이
        headers3 = {'Authorization': register_token}
        profile3 = requests.get(f'{BACKEND_URL}/api/user/profile', headers=headers3)
        print(f"Bearer 없이: {profile3.status_code}")
        
        # 소문자 bearer
        headers4 = {'Authorization': f'bearer {register_token}'}
        profile4 = requests.get(f'{BACKEND_URL}/api/user/profile', headers=headers4)
        print(f"소문자 bearer: {profile4.status_code}")
        
        # JWT로 시작
        headers5 = {'Authorization': f'JWT {register_token}'}
        profile5 = requests.get(f'{BACKEND_URL}/api/user/profile', headers=headers5)
        print(f"JWT 프리픽스: {profile5.status_code}")
        
    else:
        print(f"❌ 로그인 실패: {login.status_code}")
else:
    print(f"❌ 회원가입 실패: {register.status_code}")

print("\n" + "=" * 60) 