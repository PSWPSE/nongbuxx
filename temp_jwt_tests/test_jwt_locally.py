#!/usr/bin/env python3
"""로컬에서 JWT 토큰 생성과 검증 테스트"""

import os
os.environ['JWT_SECRET_KEY'] = 'MD1mIiR5pCnhpjhTNXklCY34gbgiPiv0mKsP6DHz_CU'
os.environ['FLASK_ENV'] = 'production'

from flask_jwt_extended import create_access_token, decode_token
from app_with_auth import app
import jwt

print("🧪 로컬 JWT 테스트")
print("=" * 60)

with app.app_context():
    # 토큰 생성
    test_user_id = 123
    access_token = create_access_token(identity=test_user_id)
    
    print(f"✅ 토큰 생성 성공")
    print(f"토큰: {access_token[:50]}...")
    
    # 토큰 디코딩 (검증 없이)
    try:
        payload = jwt.decode(access_token, options={"verify_signature": False})
        print(f"\n📊 토큰 페이로드:")
        print(f"  - sub: {payload.get('sub')}")
        print(f"  - type: {payload.get('type')}")
        print(f"  - fresh: {payload.get('fresh')}")
    except Exception as e:
        print(f"❌ 토큰 디코딩 실패: {e}")
    
    # Flask-JWT-Extended로 검증
    try:
        decoded = decode_token(access_token)
        print(f"\n✅ Flask-JWT-Extended 검증 성공!")
        print(f"  - identity: {decoded.get('sub')}")
    except Exception as e:
        print(f"\n❌ Flask-JWT-Extended 검증 실패: {e}")
    
    # 직접 JWT 검증
    jwt_key = app.config.get('JWT_SECRET_KEY')
    print(f"\n📌 사용된 JWT 키: {jwt_key[:20]}...{jwt_key[-20:]}")
    
    try:
        verified = jwt.decode(
            access_token, 
            jwt_key, 
            algorithms=['HS256'],
            options={"verify_sub": False}
        )
        print(f"✅ 직접 JWT 검증 성공!")
    except Exception as e:
        print(f"❌ 직접 JWT 검증 실패: {e}")

print("\n" + "=" * 60) 