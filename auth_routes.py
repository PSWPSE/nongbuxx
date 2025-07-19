from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity,
    get_jwt
)
from datetime import datetime, timedelta
from models import db, User, UserApiKey
from auth_utils import (
    validate_password_strength, validate_email_format,
    generate_username_from_email, create_api_key_encryptor,
    generate_reset_token
)
import logging

logger = logging.getLogger(__name__)

# Blueprint 생성
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    회원가입 API
    
    Request Body:
    {
        "email": "user@example.com",
        "password": "StrongPassword123!",
        "username": "username123" (optional)
    }
    """
    try:
        data = request.get_json()
        
        # 필수 필드 확인
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': '이메일과 비밀번호는 필수입니다.',
                'code': 'MISSING_FIELDS'
            }), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        username = data.get('username', '').strip()
        
        # 이메일 유효성 검사
        is_valid_email, validated_email = validate_email_format(email)
        if not is_valid_email:
            return jsonify({
                'success': False,
                'error': validated_email,  # 에러 메시지
                'code': 'INVALID_EMAIL'
            }), 400
        
        # 비밀번호 강도 검사
        is_strong, password_msg = validate_password_strength(password)
        if not is_strong:
            return jsonify({
                'success': False,
                'error': password_msg,
                'code': 'WEAK_PASSWORD'
            }), 400
        
        # 기존 사용자 확인
        existing_user = User.query.filter_by(email=validated_email).first()
        if existing_user:
            return jsonify({
                'success': False,
                'error': '이미 등록된 이메일입니다.',
                'code': 'EMAIL_EXISTS'
            }), 409
        
        # 사용자명 생성 (제공되지 않은 경우)
        if not username:
            username = generate_username_from_email(validated_email)
        
        # 사용자명 중복 확인
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            # 중복되면 랜덤 suffix 추가
            import secrets
            username = f"{username}_{secrets.token_hex(3)}"
        
        # 새 사용자 생성
        new_user = User(
            email=validated_email,
            username=username
        )
        new_user.set_password(password)
        
        # 데이터베이스에 저장
        db.session.add(new_user)
        db.session.commit()
        
        # JWT 토큰 생성
        access_token = create_access_token(identity=str(new_user.id))
        refresh_token = create_refresh_token(identity=str(new_user.id))
        
        logger.info(f"New user registered: {validated_email}")
        
        return jsonify({
            'success': True,
            'message': '회원가입이 완료되었습니다.',
            'user': new_user.to_dict(),
            'tokens': {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': '회원가입 중 오류가 발생했습니다.',
            'code': 'REGISTRATION_ERROR'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    로그인 API
    
    Request Body:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': '이메일과 비밀번호를 입력해주세요.',
                'code': 'MISSING_CREDENTIALS'
            }), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # 사용자 찾기
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'error': '이메일 또는 비밀번호가 올바르지 않습니다.',
                'code': 'INVALID_CREDENTIALS'
            }), 401
        
        # 계정 활성화 확인
        if not user.is_active:
            return jsonify({
                'success': False,
                'error': '비활성화된 계정입니다.',
                'code': 'ACCOUNT_INACTIVE'
            }), 403
        
        # JWT 토큰 생성 (CSRF 없이)
        access_token = create_access_token(identity=str(user.id), fresh=False)
        refresh_token = create_refresh_token(identity=str(user.id))
        
        # 마지막 로그인 시간 업데이트
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"User logged in: {email}")
        
        return jsonify({
            'success': True,
            'message': '로그인되었습니다.',
            'user': user.to_dict(),
            'tokens': {
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': '로그인 중 오류가 발생했습니다.',
            'code': 'LOGIN_ERROR'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    로그아웃 API
    
    Note: JWT는 stateless이므로 실제로는 클라이언트에서 토큰을 삭제하면 됨
    여기서는 로그아웃 이벤트만 기록
    """
    try:
        current_user_id = get_jwt_identity()
        logger.info(f"User logged out: {current_user_id}")
        
        return jsonify({
            'success': True,
            'message': '로그아웃되었습니다.'
        }), 200
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({
            'success': False,
            'error': '로그아웃 중 오류가 발생했습니다.',
            'code': 'LOGOUT_ERROR'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    토큰 갱신 API
    
    Refresh token을 사용하여 새로운 access token 발급
    """
    try:
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=str(current_user_id), fresh=False)
        
        return jsonify({
            'success': True,
            'access_token': new_access_token
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({
            'success': False,
            'error': '토큰 갱신 중 오류가 발생했습니다.',
            'code': 'REFRESH_ERROR'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    현재 로그인한 사용자 정보 조회
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({
                'success': False,
                'error': '사용자를 찾을 수 없습니다.',
                'code': 'USER_NOT_FOUND'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({
            'success': False,
            'error': '사용자 정보 조회 중 오류가 발생했습니다.',
            'code': 'GET_USER_ERROR'
        }), 500

@auth_bp.route('/check-email', methods=['POST'])
def check_email():
    """
    이메일 중복 확인 API
    
    Request Body:
    {
        "email": "user@example.com"
    }
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({
                'success': False,
                'error': '이메일을 입력해주세요.',
                'code': 'MISSING_EMAIL'
            }), 400
        
        # 이메일 유효성 검사
        is_valid_email, validated_email = validate_email_format(email)
        if not is_valid_email:
            return jsonify({
                'success': False,
                'error': validated_email,
                'code': 'INVALID_EMAIL'
            }), 400
        
        # 중복 확인
        existing_user = User.query.filter_by(email=validated_email).first()
        
        return jsonify({
            'success': True,
            'available': existing_user is None,
            'message': '사용 가능한 이메일입니다.' if not existing_user else '이미 사용 중인 이메일입니다.'
        }), 200
        
    except Exception as e:
        logger.error(f"Email check error: {str(e)}")
        return jsonify({
            'success': False,
            'error': '이메일 확인 중 오류가 발생했습니다.',
            'code': 'EMAIL_CHECK_ERROR'
        }), 500 