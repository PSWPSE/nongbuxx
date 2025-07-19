#!/usr/bin/env python3
"""
인증 시스템 테스트 스크립트
로컬 환경에서 인증 API를 테스트합니다
"""

import requests
import json
import sys
from datetime import datetime

# API 베이스 URL
BASE_URL = "http://localhost:8080"

# 테스트 사용자 정보
TEST_USER = {
    "email": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
    "password": "TestPassword123!",
    "username": f"testuser_{datetime.now().strftime('%H%M%S')}"
}

# 색상 코드
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(test_name, success, message=""):
    """테스트 결과 출력"""
    status = f"{GREEN}✓ PASS{RESET}" if success else f"{RED}✗ FAIL{RESET}"
    print(f"{status} {test_name}")
    if message:
        print(f"   {message}")

def test_register():
    """회원가입 테스트"""
    print(f"\n{BLUE}=== 회원가입 테스트 ==={RESET}")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=TEST_USER
    )
    
    if response.status_code == 201:
        data = response.json()
        print_test("회원가입", True, f"User: {data['user']['email']}")
        return data['tokens']
    else:
        print_test("회원가입", False, response.text)
        return None

def test_login():
    """로그인 테스트"""
    print(f"\n{BLUE}=== 로그인 테스트 ==={RESET}")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print_test("로그인", True)
        return data['tokens']
    else:
        print_test("로그인", False, response.text)
        return None

def test_profile(access_token):
    """프로필 조회 테스트"""
    print(f"\n{BLUE}=== 프로필 조회 테스트 ==={RESET}")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{BASE_URL}/api/user/profile",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_test("프로필 조회", True, f"Username: {data['user']['username']}")
        return True
    else:
        print_test("프로필 조회", False, response.text)
        return False

def test_save_api_key(access_token):
    """API 키 저장 테스트"""
    print(f"\n{BLUE}=== API 키 저장 테스트 ==={RESET}")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Anthropic API 키 저장
    response = requests.post(
        f"{BASE_URL}/api/user/api-keys",
        headers=headers,
        json={
            "provider": "anthropic",
            "api_key": "sk-ant-api03-test-key-for-testing-only"
        }
    )
    
    if response.status_code == 200:
        print_test("Anthropic API 키 저장", True)
    else:
        print_test("Anthropic API 키 저장", False, response.text)
    
    # OpenAI API 키 저장
    response = requests.post(
        f"{BASE_URL}/api/user/api-keys",
        headers=headers,
        json={
            "provider": "openai",
            "api_key": "sk-test-key-for-testing-only"
        }
    )
    
    if response.status_code == 200:
        print_test("OpenAI API 키 저장", True)
    else:
        print_test("OpenAI API 키 저장", False, response.text)

def test_email_check():
    """이메일 중복 확인 테스트"""
    print(f"\n{BLUE}=== 이메일 중복 확인 테스트 ==={RESET}")
    
    # 새 이메일 확인
    response = requests.post(
        f"{BASE_URL}/api/auth/check-email",
        json={"email": "new_user@example.com"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_test("새 이메일 확인", data['available'])
    else:
        print_test("새 이메일 확인", False, response.text)
    
    # 기존 이메일 확인
    response = requests.post(
        f"{BASE_URL}/api/auth/check-email",
        json={"email": TEST_USER["email"]}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_test("기존 이메일 확인", not data['available'])
    else:
        print_test("기존 이메일 확인", False, response.text)

def test_token_refresh(refresh_token):
    """토큰 갱신 테스트"""
    print(f"\n{BLUE}=== 토큰 갱신 테스트 ==={RESET}")
    
    headers = {"Authorization": f"Bearer {refresh_token}"}
    response = requests.post(
        f"{BASE_URL}/api/auth/refresh",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_test("토큰 갱신", True)
        return data['access_token']
    else:
        print_test("토큰 갱신", False, response.text)
        return None

def test_protected_endpoint(access_token):
    """보호된 엔드포인트 테스트"""
    print(f"\n{BLUE}=== 보호된 엔드포인트 테스트 ==={RESET}")
    
    # 토큰 없이 접근
    response = requests.get(f"{BASE_URL}/api/user/api-keys")
    print_test("토큰 없이 접근 차단", response.status_code == 401)
    
    # 토큰 있이 접근
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{BASE_URL}/api/user/api-keys",
        headers=headers
    )
    print_test("토큰으로 접근 허용", response.status_code == 200)

def main():
    """메인 테스트 실행"""
    print(f"{YELLOW}🧪 NONGBUXX 인증 시스템 테스트{RESET}")
    print("=" * 50)
    
    # 서버 연결 확인
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code != 200:
            print(f"{RED}❌ 서버에 연결할 수 없습니다.{RESET}")
            print(f"   {BASE_URL}에서 서버가 실행 중인지 확인하세요.")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"{RED}❌ 서버에 연결할 수 없습니다.{RESET}")
        print(f"   python app.py로 서버를 먼저 실행하세요.")
        sys.exit(1)
    
    # 테스트 실행
    tokens = test_register()
    if not tokens:
        print(f"\n{RED}회원가입 실패로 테스트를 중단합니다.{RESET}")
        return
    
    test_login()
    test_profile(tokens['access_token'])
    test_save_api_key(tokens['access_token'])
    test_email_check()
    
    new_token = test_token_refresh(tokens['refresh_token'])
    if new_token:
        test_protected_endpoint(new_token)
    
    # 결과 요약
    print(f"\n{YELLOW}=== 테스트 완료 ==={RESET}")
    print(f"테스트 사용자: {TEST_USER['email']}")
    print("\n💡 다음 단계:")
    print("1. Railway에 배포")
    print("2. 프론트엔드 로그인 UI 구현")
    print("3. 기존 API에 인증 통합")

if __name__ == "__main__":
    main() 