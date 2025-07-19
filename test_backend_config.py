#!/usr/bin/env python3
"""백엔드 설정 확인"""

import requests
import json

BACKEND_URL = "https://nongbuxxbackend-production.up.railway.app"

print("🔍 백엔드 설정 확인")
print("=" * 60)

# 디버그 엔드포인트가 있는지 확인
debug_endpoints = [
    '/api/debug/config',
    '/api/debug/env',
    '/debug/config',
    '/debug'
]

for endpoint in debug_endpoints:
    try:
        response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            print(f"\n✅ {endpoint} 응답:")
            print(json.dumps(response.json(), indent=2))
            break
    except:
        continue
else:
    print("\n❌ 디버그 엔드포인트가 없습니다.")

# 다른 방법으로 확인
print("\n\n🔧 간접적 확인 방법:")
print("1. Railway Dashboard → Backend 서비스 → Logs 탭")
print("2. 최근 로그에서 다음 내용 찾기:")
print("   - 'Starting Flask app'")
print("   - 'JWT' 관련 메시지")
print("   - 'Environment' 관련 메시지")

print("\n" + "=" * 60) 