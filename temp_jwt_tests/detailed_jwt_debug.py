#!/usr/bin/env python3
"""JWT 문제 근본 원인 분석"""

import requests
import json
import base64
from datetime import datetime

BACKEND_URL = "https://nongbuxxbackend-production.up.railway.app"

print("🔍 JWT 문제 근본 원인 분석")
print("=" * 60)

# JWT 토큰 디코딩 함수 (검증 없이)
def decode_jwt_payload(token):
    """JWT 토큰의 페이로드를 디코딩 (서명 검증 없이)"""
    try:
        # JWT는 3부분으로 구성: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # 페이로드 부분을 디코딩
        payload = parts[1]
        # Base64 패딩 추가
        payload += '=' * (4 - len(payload) % 4)
        
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        print(f"토큰 디코딩 오류: {e}")
        return None

# 1. 테스트 사용자 생성
print("\n1️⃣ 테스트 사용자 생성")
test_user = {
    "email": f"debug_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
    "password": "DebugPassword123!",
    "username": f"debug_{datetime.now().strftime('%H%M%S')}"
}

response = requests.post(f"{BACKEND_URL}/api/auth/register", json=test_user)
if response.status_code != 201:
    print(f"❌ 회원가입 실패: {response.status_code}")
    print(response.text)
    exit(1)

data = response.json()
access_token = data['tokens']['access_token']
print("✅ 회원가입 성공")
print(f"토큰 길이: {len(access_token)}")

# 2. JWT 토큰 분석
print("\n2️⃣ JWT 토큰 구조 분석")
payload = decode_jwt_payload(access_token)
if payload:
    print("토큰 페이로드:")
    print(json.dumps(payload, indent=2))
    print(f"발급 시간: {datetime.fromtimestamp(payload.get('iat', 0))}")
    print(f"만료 시간: {datetime.fromtimestamp(payload.get('exp', 0))}")

# 3. 프로필 조회 시도
print("\n3️⃣ JWT 인증 테스트")
headers = {"Authorization": f"Bearer {access_token}"}
profile_response = requests.get(f"{BACKEND_URL}/api/user/profile", headers=headers)

print(f"상태 코드: {profile_response.status_code}")
if profile_response.status_code != 200:
    print(f"응답: {profile_response.text}")

# 4. 디버그 엔드포인트 확인
print("\n4️⃣ 서버 설정 확인 시도")
debug_endpoints = [
    '/api/debug/jwt',
    '/api/debug/config',
    '/debug/jwt'
]

for endpoint in debug_endpoints:
    try:
        response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=5)
        if response.status_code == 200:
            print(f"✅ {endpoint} 응답:")
            print(json.dumps(response.json(), indent=2))
            break
    except:
        continue

# 5. 근본 원인 분석
print("\n" + "=" * 60)
print("📊 근본 원인 분석")
print("=" * 60)

print("""
🔴 JWT 문제의 일반적인 원인들:

1. **환경변수 미설정** (가장 흔함)
   - Railway에 JWT_SECRET_KEY가 설정되지 않음
   - 서버 재시작 시 환경변수가 로드되지 않음

2. **키 불일치**
   - 토큰 생성 시와 검증 시 다른 SECRET_KEY 사용
   - 개발/운영 환경 간 키 차이

3. **코드 배포 문제**
   - 최신 인증 코드가 배포되지 않음
   - 잘못된 파일이 실행됨

4. **타이밍 문제**
   - 서버 시간 동기화 문제
   - 토큰 만료 시간 설정 오류

🔧 해결 방법:

1. **즉시 시도할 것**:
   ```bash
   # Railway CLI로 환경변수 직접 설정
   railway variables set JWT_SECRET_KEY="nongbuxx-jwt-secret-key-2025-fixed-for-production"
   railway variables set ENCRYPTION_KEY="32-character-encryption-key-here"
   ```

2. **Railway Dashboard 확인**:
   - Variables 탭에서 환경변수 확인
   - Deploy 탭에서 최신 배포 상태 확인
   - Logs 탭에서 에러 메시지 확인

3. **강제 재배포**:
   ```bash
   railway up --detach
   ```

4. **로컬 테스트**:
   ```bash
   # 로컬에서 같은 환경변수로 테스트
   export JWT_SECRET_KEY="nongbuxx-jwt-secret-key-2025-fixed-for-production"
   python app_with_auth.py
   ```
""")

print("\n" + "=" * 60) 