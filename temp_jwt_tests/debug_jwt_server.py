#!/usr/bin/env python3
"""서버 JWT 설정 직접 확인"""

import requests

BACKEND_URL = 'https://nongbuxxbackend-production.up.railway.app'

print("🔍 서버 JWT 설정 디버깅")
print("=" * 60)

# 1. 헬스체크
health = requests.get(f'{BACKEND_URL}/api/health')
print(f"서버 상태: {'✅ 정상' if health.status_code == 200 else '❌ 문제'}")

# 2. JWT 디버그 정보
debug = requests.get(f'{BACKEND_URL}/debug/jwt')
if debug.status_code == 200:
    info = debug.json()
    print(f"\n📊 JWT 환경변수 설정:")
    print(f"  - 설정 여부: {info['jwt_secret_key_set']}")
    print(f"  - 키 미리보기: {info['jwt_secret_key_preview']}")
    print(f"  - Config JWT 키: {info.get('config_jwt_key', 'N/A')}")
else:
    print("❌ 디버그 엔드포인트 접근 실패")

# 3. Railway 환경변수 확인 제안
print(f"\n💡 Railway Dashboard에서 확인할 사항:")
print("1. Variables 탭에서 JWT_SECRET_KEY 값 확인")
print("2. 값이 정확히 다음과 같은지 확인:")
print("   MD1mIiR5pCnhpjhTNXklCY34gbgiPiv0mKsP6DHz_CU")
print("3. 앞뒤 공백이나 따옴표가 없는지 확인")
print("4. FLASK_ENV=production 인지 확인")

print("\n" + "=" * 60) 