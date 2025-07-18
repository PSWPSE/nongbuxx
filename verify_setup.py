#!/usr/bin/env python3
"""
환경 설정 검증 스크립트
로그인 시스템에 필요한 모든 설정이 올바른지 확인합니다
"""

import os
import sys
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def check_env_var(name, required=True, min_length=0, exact_length=None, hide_value=True):
    """환경 변수 확인"""
    value = os.getenv(name)
    
    if not value:
        if required:
            return f"❌ {name}: 설정되지 않음"
        else:
            return f"⚠️  {name}: 설정되지 않음 (선택사항)"
    
    if exact_length and len(value) != exact_length:
        return f"❌ {name}: 길이가 {exact_length}자여야 함 (현재: {len(value)}자)"
    
    if min_length and len(value) < min_length:
        return f"❌ {name}: 최소 {min_length}자 이상이어야 함 (현재: {len(value)}자)"
    
    # 값 표시 (민감한 정보는 일부만)
    if hide_value and len(value) > 10:
        display_value = f"{value[:6]}...{value[-4:]}"
    else:
        display_value = value
    
    return f"✅ {name}: {display_value} ({len(value)}자)"

def check_database():
    """데이터베이스 연결 확인"""
    try:
        from models import db
        from flask import Flask
        from config import config_by_name
        
        app = Flask(__name__)
        env = os.getenv('FLASK_ENV', 'development')
        app.config.from_object(config_by_name[env])
        db.init_app(app)
        
        with app.app_context():
            # 간단한 쿼리로 연결 테스트
            result = db.session.execute(db.text('SELECT 1')).scalar()
            if result == 1:
                return "✅ 데이터베이스 연결 성공"
            else:
                return "❌ 데이터베이스 연결 실패"
    except Exception as e:
        return f"❌ 데이터베이스 오류: {str(e)}"

def main():
    print("🔍 NONGBUXX 로그인 시스템 환경 설정 검증")
    print("=" * 50)
    print()
    
    # 필수 환경 변수 확인
    print("📋 필수 환경 변수:")
    print("-" * 50)
    
    # API 키
    print(check_env_var('ANTHROPIC_API_KEY', hide_value=True))
    print(check_env_var('OPENAI_API_KEY', hide_value=True))
    
    # 보안 키
    print(check_env_var('SECRET_KEY', min_length=20))
    print(check_env_var('JWT_SECRET_KEY', min_length=20))
    print(check_env_var('ENCRYPTION_KEY', exact_length=32))
    
    # Flask 설정
    print(check_env_var('FLASK_ENV', hide_value=False))
    print(check_env_var('DATABASE_URL', hide_value=False))
    
    print()
    print("📋 선택적 환경 변수:")
    print("-" * 50)
    
    # 이메일 설정
    print(check_env_var('MAIL_SERVER', required=False, hide_value=False))
    print(check_env_var('MAIL_USERNAME', required=False))
    
    print()
    print("🗄️ 데이터베이스 상태:")
    print("-" * 50)
    print(check_database())
    
    print()
    print("📊 전체 상태:")
    print("-" * 50)
    
    # 전체 상태 확인
    required_vars = ['ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'SECRET_KEY', 
                     'JWT_SECRET_KEY', 'ENCRYPTION_KEY', 'DATABASE_URL']
    
    all_set = all(os.getenv(var) for var in required_vars)
    
    if all_set:
        print("✅ 모든 필수 환경 변수가 설정되었습니다!")
        print("🚀 로그인 시스템 개발을 진행할 수 있습니다.")
    else:
        print("❌ 일부 필수 환경 변수가 누락되었습니다.")
        print("📝 위의 목록을 확인하고 .env 파일을 업데이트하세요.")
        
    # Railway 정보
    print()
    print("🚂 Railway 배포 정보:")
    print("-" * 50)
    if os.getenv('RAILWAY_ENVIRONMENT_NAME'):
        print("✅ Railway 환경에서 실행 중")
    else:
        print("💻 로컬 개발 환경에서 실행 중")
        print("📝 Railway Variables 탭에 RAILWAY_ENV_VARS.txt 내용을 추가하세요")

if __name__ == "__main__":
    main() 