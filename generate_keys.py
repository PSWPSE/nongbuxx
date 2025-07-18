#!/usr/bin/env python3
"""
환경 변수 키 생성 헬퍼
로그인 시스템에 필요한 보안 키들을 생성합니다
"""

import secrets
import string
import random

def generate_secret_key():
    """SECRET_KEY 생성 (32자 이상)"""
    return secrets.token_urlsafe(32)

def generate_jwt_secret_key():
    """JWT_SECRET_KEY 생성 (32자 이상)"""
    return secrets.token_urlsafe(32)

def generate_encryption_key():
    """ENCRYPTION_KEY 생성 (정확히 32자)"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(32))

def main():
    print("🔐 NONGBUXX 로그인 시스템 환경 변수 생성기")
    print("=" * 50)
    print()
    
    # 키 생성
    secret_key = generate_secret_key()
    jwt_secret_key = generate_jwt_secret_key()
    encryption_key = generate_encryption_key()
    
    print("📋 Railway Variables 탭에 복사해서 붙여넣으세요:")
    print("-" * 50)
    print(f"SECRET_KEY={secret_key}")
    print(f"JWT_SECRET_KEY={jwt_secret_key}")
    print(f"ENCRYPTION_KEY={encryption_key}")
    print(f"FLASK_ENV=production")
    print()
    
    print("💻 로컬 .env 파일용 (개발 환경):")
    print("-" * 50)
    print("# 기존 API 키들은 그대로 유지하세요")
    print("# ANTHROPIC_API_KEY=your_actual_key")
    print("# OPENAI_API_KEY=your_actual_key")
    print()
    print("# 데이터베이스")
    print("DATABASE_URL=sqlite:///nongbuxx.db")
    print()
    print("# 보안 키 (개발용)")
    print("SECRET_KEY=dev-secret-key-for-local-development-only")
    print("JWT_SECRET_KEY=dev-jwt-secret-key-for-local-only")  
    print("ENCRYPTION_KEY=dev32charactersencryptionkeyhere")
    print()
    print("# Flask 환경")
    print("FLASK_ENV=development")
    print()
    
    print("⚠️  주의사항:")
    print("- 위의 프로덕션 키들은 한 번만 사용하고 재생성하지 마세요")
    print("- 이 키들을 안전하게 보관하세요")
    print("- GitHub에 커밋하지 마세요")
    print()
    
    # 키 검증
    print("✅ 생성된 키 검증:")
    print(f"- SECRET_KEY 길이: {len(secret_key)}자 (32자 이상 ✓)")
    print(f"- JWT_SECRET_KEY 길이: {len(jwt_secret_key)}자 (32자 이상 ✓)")
    print(f"- ENCRYPTION_KEY 길이: {len(encryption_key)}자 (정확히 32자 ✓)")

if __name__ == "__main__":
    main() 