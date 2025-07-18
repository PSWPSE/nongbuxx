#!/usr/bin/env python3
"""
Railway PostgreSQL 연결 테스트 스크립트
"""

import os
import psycopg2
from urllib.parse import urlparse

def test_railway_connection():
    """Railway PostgreSQL 연결 테스트"""
    
    # 두 가지 DATABASE_URL 확인
    internal_url = "postgresql://postgres:RJOSkhbScKRksDwTSfQaGewXhbBpkDVk@postgres.railway.internal:5432/railway"
    external_url = "postgresql://postgres:RJOSkhbScKRksDwTSfQaGewXhbBpkDVk@crossover.proxy.rlwy.net:22602/railway"
    
    print("🔍 Railway PostgreSQL 연결 테스트")
    print("=" * 50)
    
    # 외부 URL로 테스트
    print("\n📡 외부 연결 URL 테스트:")
    print(f"   {external_url.split('@')[1]}")
    
    try:
        # URL 파싱
        parsed = urlparse(external_url)
        
        # 연결
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password
        )
        
        print("   ✅ 연결 성공!")
        
        # 간단한 쿼리 실행
        cur = conn.cursor()
        
        # 테이블 목록 확인
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        print(f"\n📊 데이터베이스 테이블 ({len(tables)}개):")
        for table in tables:
            print(f"   - {table[0]}")
            
        # 각 테이블의 행 수 확인
        print("\n📈 테이블 데이터:")
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cur.fetchone()[0]
            print(f"   - {table[0]}: {count}개 행")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"   ❌ 연결 실패: {str(e)}")
    
    print("\n💡 참고:")
    print("   - 내부 URL: Railway 서비스 간 통신용")
    print("   - 외부 URL: 로컬 개발 및 외부 접속용")
    print("\n🚀 백엔드 서비스 Variables 확인:")
    print("   DATABASE_URL이 자동으로 설정되어 있는지 확인하세요")
    print("   형식: DATABASE_URL=${{Postgres.DATABASE_URL}}")

if __name__ == "__main__":
    test_railway_connection() 