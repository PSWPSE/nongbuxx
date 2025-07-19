"""
JWT 초기화 문제 해결을 위한 패치
"""

from flask_jwt_extended import JWTManager
import os

def fix_jwt_initialization(app):
    """JWT를 올바르게 초기화하는 함수"""
    
    # 환경변수에서 JWT_SECRET_KEY 가져오기
    jwt_secret = os.getenv('JWT_SECRET_KEY')
    
    if not jwt_secret:
        print("❌ JWT_SECRET_KEY 환경변수가 없습니다!")
        return
    
    # Flask 앱 설정에 강제로 JWT_SECRET_KEY 설정
    app.config['JWT_SECRET_KEY'] = jwt_secret
    
    # JWT Manager가 이미 초기화되었는지 확인
    if not hasattr(app, 'jwt_manager'):
        # 새로운 JWT Manager 생성
        jwt_manager = JWTManager()
        jwt_manager.init_app(app)
        app.jwt_manager = jwt_manager
        print(f"✅ JWT Manager 초기화 완료 (키: {jwt_secret[:10]}...{jwt_secret[-10:]})")
    else:
        # 기존 JWT Manager 재설정
        app.jwt_manager.init_app(app)
        print(f"✅ JWT Manager 재설정 완료 (키: {jwt_secret[:10]}...{jwt_secret[-10:]})")
    
    return app 