"""
임시 디버그 엔드포인트
JWT 설정 문제를 진단하기 위한 엔드포인트
프로덕션에서는 반드시 제거해야 함
"""

from flask import Blueprint
import os
import json

debug_bp = Blueprint('debug', __name__, url_prefix='/api/debug')

@debug_bp.route('/env-check', methods=['GET'])
def check_env():
    """환경 변수 확인 (보안상 일부만 표시)"""
    env_vars = {
        'FLASK_ENV': os.getenv('FLASK_ENV', 'not set'),
        'JWT_SECRET_KEY_EXISTS': bool(os.getenv('JWT_SECRET_KEY')),
        'SECRET_KEY_EXISTS': bool(os.getenv('SECRET_KEY')),
        'ENCRYPTION_KEY_EXISTS': bool(os.getenv('ENCRYPTION_KEY')),
        'DATABASE_URL_EXISTS': bool(os.getenv('DATABASE_URL')),
        'JWT_SECRET_KEY_LENGTH': len(os.getenv('JWT_SECRET_KEY', '')) if os.getenv('JWT_SECRET_KEY') else 0,
        'APP_VERSION': 'app_with_auth'
    }
    
    return {
        'success': True,
        'env_check': env_vars,
        'message': '이 엔드포인트는 디버깅용입니다. 프로덕션에서는 제거하세요.'
    }, 200 