#!/usr/bin/env python3
"""JWT 토큰 고급 분석"""

import requests
import jwt
import json
from datetime import datetime
import base64

BACKEND_URL = 'https://nongbuxxbackend-production.up.railway.app'

print("🔍 JWT 토큰 고급 분석")
print("=" * 60)

# 1. 디버그 엔드포인트 확인
try:
    debug = requests.get(f'{BACKEND_URL}/debug/jwt')
    if debug.status_code == 200:
        debug_info = debug.json()
        print(f"✅ 서버 JWT 설정 확인:")
        print(f"  - JWT Secret Key 설정: {debug_info['jwt_secret_key_set']}")
        print(f"  - JWT Secret Key 미리보기: {debug_info['jwt_secret_key_preview']}")
except:
    print("❌ 디버그 엔드포인트 접근 실패")

# 2. 새 사용자로 토큰 생성
test_user = {
    'email': f'advanced_test_{datetime.now().strftime("%Y%m%d%H%M%S")}@test.com',
    'password': 'Advanced123!'
}

print(f"\n📊 테스트 사용자: {test_user['email']}")

# 회원가입
register = requests.post(f'{BACKEND_URL}/api/auth/register', json=test_user)
if register.status_code == 201:
    print("✅ 회원가입 성공")
    data = register.json()
    access_token = data['tokens']['access_token']
    
    # 토큰 분석
    print(f"\n📌 토큰 정보:")
    print(f"길이: {len(access_token)}")
    
    # JWT 구조 분석
    parts = access_token.split('.')
    if len(parts) == 3:
        # 페이로드 디코딩
        payload = jwt.decode(access_token, options={"verify_signature": False})
        print(f"\n📊 페이로드:")
        print(json.dumps(payload, indent=2))
        
        # 가능한 모든 키 조합 시도
        possible_keys = [
            'MD1mIiR5pCnhpjhTNXklCY34gbgiPiv0mKsP6DHz_CU',
            'MD1mIiR5pCnhpjhTNXklCY34gbgiPiv0mKsP6',
            'dev-jwt-secret-key-for-local-only',
            'TiAnYueCfjXCIPcz8P7LPi8XDpC1LCpR1E5glf13wN4',  # SECRET_KEY
        ]
        
        print(f"\n🔐 키 검증 시도:")
        for key in possible_keys:
            try:
                # subject 타입 문제 해결을 위해 verify_sub=False 추가
                decoded = jwt.decode(
                    access_token, 
                    key, 
                    algorithms=['HS256'],
                    options={"verify_sub": False}
                )
                print(f"✅ 성공! 사용된 키: {key[:20]}...")
                print(f"   전체 키: {key}")
                
                # 성공한 키로 프로필 조회
                headers = {'Authorization': f'Bearer {access_token}'}
                profile = requests.get(f'{BACKEND_URL}/api/user/profile', headers=headers)
                print(f"\n🧪 프로필 조회 테스트: {profile.status_code}")
                if profile.status_code == 200:
                    print("✅ JWT 인증 성공!")
                else:
                    print(f"❌ JWT 인증 실패: {profile.text}")
                break
                
            except jwt.InvalidSignatureError:
                print(f"❌ 서명 불일치: {key[:20]}...")
            except Exception as e:
                print(f"❌ 에러 ({key[:20]}...): {str(e)}")
    else:
        print("❌ 잘못된 토큰 형식")
else:
    print(f"❌ 회원가입 실패: {register.status_code}")

print("\n" + "=" * 60) 