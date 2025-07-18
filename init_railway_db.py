#!/usr/bin/env python3
"""
Railway PostgreSQL 데이터베이스 초기화 스크립트
Railway 환경에서 실행하여 테이블을 생성합니다
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_railway_database():
    """Initialize Railway PostgreSQL database tables"""
    try:
        # Railway DATABASE_URL 사용
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            print("❌ DATABASE_URL이 설정되지 않았습니다.")
            print("💡 Railway 환경에서 실행하거나 DATABASE_URL을 설정하세요.")
            return
        
        # PostgreSQL URL 형식 확인
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
            os.environ['DATABASE_URL'] = database_url
        
        print(f"🔗 연결 중: {database_url.split('@')[1] if '@' in database_url else 'DATABASE'}")
        
        # Import after path setup
        from models import db
        from flask import Flask
        from config import config_by_name
        
        # Create Flask app
        app = Flask(__name__)
        
        # Production 설정 사용
        app.config.from_object(config_by_name['production'])
        
        # Initialize database
        db.init_app(app)
        
        with app.app_context():
            # Create all tables
            print("📋 테이블 생성 중...")
            db.create_all()
            print("✅ 테이블 생성 완료!")
            
            # Show created tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("\n📊 생성된 테이블:")
            for table in tables:
                print(f"  ✓ {table}")
                
            # 각 테이블의 컬럼 정보 표시
            print("\n📝 테이블 구조:")
            for table in tables:
                print(f"\n  {table}:")
                columns = inspector.get_columns(table)
                for col in columns:
                    print(f"    - {col['name']} ({col['type']})")
            
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Railway PostgreSQL 초기화 시작...")
    print("=" * 50)
    init_railway_database()
    print("\n✨ 초기화 완료!") 