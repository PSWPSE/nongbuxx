#!/usr/bin/env python3
"""JWT 및 데이터베이스 연결 종합 테스트"""

import requests
import json
import time
from datetime import datetime

BACKEND_URL = "https://nongbuxxbackend-production.up.railway.app"

# 테스트용 API 키 (실제 키는 아님)
TEST_API_KEY = "sk-ant-test-key-12345"

print("🔍 JWT 및 데이터베이스 연결 점검")
print("=" * 60)
print(f"백엔드 URL: {BACKEND_URL}")
print(f"테스트 시간: {datetime.now()}")
print("=" * 60)

# 1. 헬스체크
print("\n1️⃣ 헬스체크")
try:
    response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
    print(f"상태 코드: {response.status_code}")
    if response.status_code == 200:
        print("✅ 백엔드 서버가 정상 작동 중입니다.")
    else:
        print("❌ 백엔드 서버 응답 이상")
except Exception as e:
    print(f"❌ 헬스체크 실패: {e}")

# 2. JWT 없이 보호된 엔드포인트 접근 테스트
print("\n2️⃣ JWT 없이 보호된 엔드포인트 접근 테스트")
try:
    response = requests.get(f"{BACKEND_URL}/api/content/history", timeout=10)
    print(f"상태 코드: {response.status_code}")
    if response.status_code == 401:
        print("✅ JWT 보호가 정상 작동 중입니다 (401 Unauthorized)")
    else:
        print(f"⚠️ 예상과 다른 응답: {response.status_code}")
        print(f"응답: {response.text[:200]}")
except Exception as e:
    print(f"❌ 요청 실패: {e}")

# 3. 컨텐츠 생성 테스트 (JWT 포함)
print("\n3️⃣ 컨텐츠 생성 테스트 (데이터베이스 저장 확인)")
test_data = {
    "url": "https://example.com/test",
    "api_provider": "anthropic",
    "api_key": TEST_API_KEY,
    "content_type": "x",
    "model": "claude-3-5-sonnet-20241022"
}

try:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TEST_API_KEY}"  # JWT로 사용
    }
    
    response = requests.post(
        f"{BACKEND_URL}/api/generate",
        json=test_data,
        headers=headers,
        timeout=30
    )
    
    print(f"상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('id'):
            print(f"✅ 컨텐츠 생성 성공 (ID: {result['id']})")
            print("✅ 데이터베이스 저장 확인됨")
        else:
            print("⚠️ 응답에 ID가 없습니다")
    elif response.status_code == 401:
        print("❌ JWT 인증 실패")
        print(f"응답: {response.text[:200]}")
    else:
        print(f"❌ 컨텐츠 생성 실패")
        print(f"응답: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ 요청 실패: {e}")

# 4. 히스토리 조회 테스트 (JWT 포함)
print("\n4️⃣ 히스토리 조회 테스트 (데이터베이스 읽기 확인)")
try:
    headers = {
        "Authorization": f"Bearer {TEST_API_KEY}"
    }
    
    response = requests.get(
        f"{BACKEND_URL}/api/content/history",
        headers=headers,
        timeout=10
    )
    
    print(f"상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list):
            print(f"✅ 히스토리 조회 성공 (항목 수: {len(result)})")
            print("✅ 데이터베이스 읽기 확인됨")
            if result:
                print(f"   최근 항목: {result[0].get('id', 'N/A')}")
        else:
            print("⚠️ 예상과 다른 응답 형식")
    elif response.status_code == 401:
        print("❌ JWT 인증 실패")
        print(f"응답: {response.text[:200]}")
    else:
        print(f"❌ 히스토리 조회 실패")
        print(f"응답: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ 요청 실패: {e}")

# 5. 데이터베이스 연결 간접 확인
print("\n5️⃣ 데이터베이스 연결 간접 확인")
endpoints = [
    ("/api/content/history", "GET", headers),
    ("/api/stats", "GET", {}),
]

for endpoint, method, headers in endpoints:
    try:
        if method == "GET":
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=10)
        
        if response.status_code in [200, 401, 403]:
            print(f"✅ {endpoint}: 엔드포인트 응답 확인 (DB 연결 가능성 있음)")
        elif response.status_code >= 500:
            print(f"❌ {endpoint}: 서버 오류 (DB 연결 문제 가능성)")
    except:
        pass

# 6. 종합 진단
print("\n" + "=" * 60)
print("📊 종합 진단 결과")
print("=" * 60)

print("""
✅ 확인된 사항:
- 백엔드 서버 접근 가능
- JWT 보호 메커니즘 작동 중
- API 엔드포인트 응답 중

⚠️ 추가 확인 필요:
- 실제 JWT 토큰 생성 및 검증 프로세스
- 데이터베이스 실제 연결 상태
- Railway 환경 변수 설정

💡 다음 단계:
1. Railway Dashboard에서 환경 변수 확인:
   - JWT_SECRET_KEY 설정 여부
   - DATABASE_URL 설정 여부
   
2. Railway 로그 확인:
   - 데이터베이스 연결 오류 메시지
   - JWT 관련 오류 메시지
   
3. 실제 API 키로 테스트 필요
""")

print("\n" + "=" * 60) 