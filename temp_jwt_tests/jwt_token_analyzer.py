#!/usr/bin/env python3
"""JWT 토큰 분석 도구"""

import requests
import jwt
import json
from datetime import datetime

BACKEND_URL = 'https://nongbuxxbackend-production.up.railway.app'

# 1. 새 사용자 생성 및 토큰 받기
test_user = {
    'email': f'jwt_analysis_{datetime.now().strftime("%Y%m%d%H%M%S")}@test.com',
    'password': 'Analysis123!'
}

print("🔍 JWT 토큰 분석")
print("=" * 60)

# 회원가입
register = requests.post(f'{BACKEND_URL}/api/auth/register', json=test_user)
if register.status_code == 201:
    print("✅ 회원가입 성공")
    data = register.json()
    access_token = data['tokens']['access_token']
    
    print(f"\n📌 받은 토큰:")
    print(f"길이: {len(access_token)}")
    print(f"토큰: {access_token[:50]}...")
    
    # JWT 토큰 파싱 (검증 없이)
    try:
        # 헤더와 페이로드 디코딩 (서명 검증 없이)
        header = jwt.get_unverified_header(access_token)
        payload = jwt.decode(access_token, options={"verify_signature": False})
        
        print(f"\n📊 토큰 헤더:")
        print(json.dumps(header, indent=2))
        
        print(f"\n📊 토큰 페이로드:")
        print(json.dumps(payload, indent=2))
        
        # Railway에서 사용 중인 키로 검증 시도
        jwt_keys_to_try = [
            'MD1mIiR5pCnhpjhTNXklCY34gbgiPiv0mKsP6DHz_CU',  # 전체 키
            'MD1mIiR5pCnhpjhTNXklCY34gbgiPiv0mKsP6',  # 잘린 키
            'dev-jwt-secret-key-for-local-only'  # 개발 키
        ]
        
        print(f"\n🔐 다양한 키로 검증 시도:")
        for idx, key in enumerate(jwt_keys_to_try):
            try:
                decoded = jwt.decode(access_token, key, algorithms=['HS256'])
                print(f"✅ 키 #{idx+1} 성공! (키: {key[:20]}...)")
                break
            except jwt.InvalidSignatureError:
                print(f"❌ 키 #{idx+1} 실패 (키: {key[:20]}...)")
            except Exception as e:
                print(f"❌ 키 #{idx+1} 에러: {str(e)}")
        
    except Exception as e:
        print(f"\n❌ 토큰 파싱 에러: {str(e)}")
else:
    print(f"❌ 회원가입 실패: {register.status_code}")
    print(register.text)

print("\n" + "=" * 60) 