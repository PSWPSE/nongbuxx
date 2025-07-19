#!/usr/bin/env python3
"""
NONGBUXX with Authentication - 간단한 버전
JWT 문제를 근본적으로 해결
"""

import os
import logging
from app import app, jsonify, request, logger
from models import db, User
from auth_routes import auth_bp
from user_routes import user_bp
from flask_jwt_extended import JWTManager

# 로거 설정
logging.basicConfig(level=logging.INFO)

# 환경 설정
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///nongbuxx.db').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT 설정 - 환경변수에서 읽기
jwt_secret = os.getenv('JWT_SECRET_KEY')
if not jwt_secret:
    print("❌ JWT_SECRET_KEY 환경변수가 없습니다!")
    jwt_secret = 'dev-jwt-secret-key-for-local-only'
    
app.config['JWT_SECRET_KEY'] = jwt_secret
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

print(f"📌 JWT Secret Key 설정: {jwt_secret[:10]}...{jwt_secret[-10:]}")

# 데이터베이스 초기화
db.init_app(app)

# JWT Manager 초기화 (한 번만!)
jwt = JWTManager(app)
print("✅ JWT Manager 초기화 완료")

# 블루프린트 등록
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)

# JWT 에러 핸들러
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'success': False,
        'error': '유효하지 않은 토큰입니다.',
        'code': 'INVALID_TOKEN'
    }), 401

# 애플리케이션 컨텍스트에서 테이블 생성
with app.app_context():
    db.create_all()
    print("✅ 데이터베이스 테이블 생성 완료")

# 헬스체크는 이미 app.py에 정의되어 있음

print("✅ 인증 시스템 초기화 완료")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 