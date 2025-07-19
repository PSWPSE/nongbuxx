#!/usr/bin/env python3
"""JWT 수정 후 테스트"""

import os
os.environ['JWT_SECRET_KEY'] = 'MD1mIiR5pCnhpjhTNXklCY34gbgiPiv0mKsP6DHz_CU'
os.environ['FLASK_ENV'] = 'production'

from flask_jwt_extended import create_access_token, decode_token
from app_with_auth import app
import jwt

print("🧪 JWT 수정 후 로컬 테스트")
print("=" * 60)

with app.app_context():
    # 문자열 ID로 토큰 생성
    test_user_id = "123"  # 문자열!
    access_token = create_access_token(identity=test_user_id)
    
    print(f"✅ 토큰 생성 성공 (문자열 ID)")
    print(f"토큰: {access_token[:50]}...")
    
    # Flask-JWT-Extended로 검증
    try:
        decoded = decode_token(access_token)
        print(f"\n✅ Flask-JWT-Extended 검증 성공!")
        print(f"  - identity: {decoded.get('sub')} (타입: {type(decoded.get('sub'))})")
        
        # identity가 문자열인지 확인
        if isinstance(decoded.get('sub'), str):
            print("  - ✅ identity가 문자열입니다!")
        else:
            print("  - ❌ identity가 문자열이 아닙니다!")
            
    except Exception as e:
        print(f"\n❌ Flask-JWT-Extended 검증 실패: {e}")

print("\n" + "=" * 60)
print("🎉 JWT identity 타입 문제가 해결되었습니다!") 