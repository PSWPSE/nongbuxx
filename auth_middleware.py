from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import UserApiKey
from auth_utils import create_api_key_encryptor
import logging

logger = logging.getLogger(__name__)

def get_user_api_key(provider):
    """
    현재 로그인한 사용자의 저장된 API 키를 가져옵니다.
    
    Args:
        provider: 'anthropic' 또는 'openai'
        
    Returns:
        복호화된 API 키 또는 None
    """
    try:
        current_user_id = get_jwt_identity()
        
        # 사용자의 저장된 API 키 조회
        api_key_record = UserApiKey.query.filter_by(
            user_id=current_user_id,
            provider=provider.lower()
        ).first()
        
        if not api_key_record:
            return None
        
        # 복호화
        encryptor = create_api_key_encryptor()
        return encryptor.decrypt(api_key_record.encrypted_key)
        
    except Exception as e:
        logger.error(f"Error getting user API key: {str(e)}")
        return None

def require_api_key(provider=None):
    """
    API 키가 필요한 엔드포인트를 보호하는 데코레이터
    
    사용법:
        @require_api_key()  # provider를 request body에서 가져옴
        @require_api_key('anthropic')  # 특정 provider 지정
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()  # JWT 인증 필수
        def decorated_function(*args, **kwargs):
            # Provider 결정
            if provider:
                api_provider = provider
            else:
                # Request body에서 provider 가져오기
                data = request.get_json()
                api_provider = data.get('api_provider') if data else None
                
                if not api_provider:
                    return jsonify({
                        'success': False,
                        'error': 'API provider가 필요합니다.',
                        'code': 'MISSING_PROVIDER'
                    }), 400
            
            # 사용자의 저장된 API 키 가져오기
            api_key = get_user_api_key(api_provider)
            
            if not api_key:
                return jsonify({
                    'success': False,
                    'error': f'{api_provider.capitalize()} API 키가 설정되지 않았습니다. 프로필에서 API 키를 먼저 등록해주세요.',
                    'code': 'API_KEY_NOT_SET'
                }), 401
            
            # Request context에 API 키 저장
            request.user_api_key = api_key
            request.api_provider = api_provider
            
            return f(*args, **kwargs)
            
        return decorated_function
    return decorator

def optional_auth(f):
    """
    선택적 인증 데코레이터
    로그인한 경우 사용자 정보를 제공하지만, 로그인하지 않아도 접근 가능
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # JWT 토큰이 있는지 확인
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                # JWT 검증 시도
                from flask_jwt_extended import verify_jwt_in_request
                verify_jwt_in_request(optional=True)
                request.current_user_id = get_jwt_identity()
            else:
                request.current_user_id = None
                
        except Exception:
            # 토큰이 잘못된 경우에도 계속 진행
            request.current_user_id = None
            
        return f(*args, **kwargs)
        
    return decorated_function

def track_user_content(content_type, url, file_path=None):
    """
    사용자가 생성한 콘텐츠를 추적합니다.
    
    Args:
        content_type: 'standard', 'blog', 'x', 'threads' 등
        url: 원본 URL
        file_path: 생성된 파일 경로
    """
    try:
        if hasattr(request, 'current_user_id') and request.current_user_id:
            from models import db, GeneratedContent
            
            content = GeneratedContent(
                user_id=request.current_user_id,
                url=url,
                content_type=content_type,
                file_path=file_path
            )
            db.session.add(content)
            db.session.commit()
            
            logger.info(f"Tracked content generation for user {request.current_user_id}")
            
    except Exception as e:
        logger.error(f"Error tracking user content: {str(e)}") 