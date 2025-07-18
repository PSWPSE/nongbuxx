#!/usr/bin/env python3
"""
Database initialization script
Run this to create all database tables
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_database():
    """Initialize database tables"""
    try:
        # Import after path setup
        from models import db
        from flask import Flask
        from config import config_by_name
        
        # Create minimal Flask app for DB operations
        app = Flask(__name__)
        
        # Configure app
        env = os.getenv('FLASK_ENV', 'development')
        app.config.from_object(config_by_name[env])
        
        # Initialize database
        db.init_app(app)
        
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ 데이터베이스 테이블이 생성되었습니다.")
            
            # Show created tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("\n📋 생성된 테이블:")
            for table in tables:
                print(f"  - {table}")
                
            print(f"\n🔗 데이터베이스: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 데이터베이스 초기화 시작...")
    init_database()
    print("\n✨ 데이터베이스 초기화 완료!") 