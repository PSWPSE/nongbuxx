"""
Flask 앱 인증 설정
기존 app.py에 인증 기능을 추가하기 위한 설정
"""

from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from models import db
from config import config_by_name
from auth_routes import auth_bp
from user_routes import user_bp
import os

def init_auth(app):
    """
    Flask 앱에 인증 시스템을 초기화합니다.
    
    Args:
        app: Flask 애플리케이션 인스턴스
    """
    # 환경 설정
    env = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config_by_name[env])
    
    # 데이터베이스 초기화
    db.init_app(app)
    
    # 마이그레이션 초기화
    migrate = Migrate(app, db)
    
    # JWT 초기화
    jwt = JWTManager(app)
    
    # 인증 관련 블루프린트 등록
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    
    # JWT 에러 핸들러
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {
            'success': False,
            'error': '토큰이 만료되었습니다. 다시 로그인해주세요.',
            'code': 'TOKEN_EXPIRED'
        }, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {
            'success': False,
            'error': '유효하지 않은 토큰입니다.',
            'code': 'INVALID_TOKEN'
        }, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {
            'success': False,
            'error': '인증이 필요합니다. 로그인해주세요.',
            'code': 'AUTHORIZATION_REQUIRED'
        }, 401
    
    # 애플리케이션 컨텍스트에서 테이블 생성 (개발 환경에서만)
    if env == 'development':
        with app.app_context():
            # 테이블이 없으면 생성
            db.create_all()
    
    return app

def modify_existing_routes(app):
    """
    기존 라우트에 선택적 인증을 추가합니다.
    
    이 함수는 기존 app.py의 라우트들을 수정하지 않고
    wrapper를 통해 인증 기능을 추가합니다.
    """
    from auth_middleware import optional_auth, require_api_key
    
    # 기존 라우트 목록
    protected_routes = [
        '/api/generate',
        '/api/batch-generate',
        '/api/validate-key'
    ]
    
    # 각 라우트에 인증 래퍼 추가
    for rule in app.url_map.iter_rules():
        if any(route in rule.rule for route in protected_routes):
            # 이미 등록된 뷰 함수를 가져와서 래핑
            endpoint = rule.endpoint
            view_func = app.view_functions.get(endpoint)
            if view_func:
                # 선택적 인증 적용 (로그인하지 않아도 접근 가능)
                app.view_functions[endpoint] = optional_auth(view_func) 