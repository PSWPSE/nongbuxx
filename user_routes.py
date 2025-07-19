from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, UserApiKey
from auth_utils import create_api_key_encryptor
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Blueprint 생성
user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """사용자 프로필 조회"""
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
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({
            'success': False,
            'error': '프로필 조회 중 오류가 발생했습니다.',
            'code': 'PROFILE_ERROR'
        }), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    사용자 프로필 업데이트
    
    Request Body:
    {
        "username": "newusername" (optional)
    }
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
        
        data = request.get_json()
        
        # 사용자명 업데이트
        if 'username' in data:
            new_username = data['username'].strip()
            
            if not new_username:
                return jsonify({
                    'success': False,
                    'error': '사용자명을 입력해주세요.',
                    'code': 'INVALID_USERNAME'
                }), 400
            
            # 중복 확인
            existing = User.query.filter_by(username=new_username).first()
            if existing and existing.id != current_user_id:
                return jsonify({
                    'success': False,
                    'error': '이미 사용 중인 사용자명입니다.',
                    'code': 'USERNAME_EXISTS'
                }), 409
            
            user.username = new_username
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '프로필이 업데이트되었습니다.',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': '프로필 업데이트 중 오류가 발생했습니다.',
            'code': 'UPDATE_ERROR'
        }), 500

@user_bp.route('/api-keys', methods=['GET'])
@jwt_required()
def get_api_keys():
    """사용자의 API 키 목록 조회"""
    try:
        current_user_id = get_jwt_identity()
        
        # 사용자의 API 키 조회
        api_keys = UserApiKey.query.filter_by(user_id=current_user_id).all()
        
        # 암호화된 키는 일부만 표시
        result = []
        for key in api_keys:
            result.append({
                'id': key.id,
                'provider': key.provider,
                'masked_key': f"{key.encrypted_key[:10]}...{key.encrypted_key[-4:]}" if len(key.encrypted_key) > 14 else "***",
                'created_at': key.created_at.isoformat() if key.created_at else None,
                'updated_at': key.updated_at.isoformat() if key.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'api_keys': result
        }), 200
        
    except Exception as e:
        logger.error(f"Get API keys error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'API 키 조회 중 오류가 발생했습니다.',
            'code': 'GET_KEYS_ERROR'
        }), 500

@user_bp.route('/api-keys', methods=['POST'])
@jwt_required()
def save_api_key():
    """
    API 키 저장/업데이트
    
    Request Body:
    {
        "provider": "anthropic" or "openai",
        "api_key": "sk-..."
    }
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'provider' not in data or 'api_key' not in data:
            return jsonify({
                'success': False,
                'error': 'Provider와 API 키는 필수입니다.',
                'code': 'MISSING_FIELDS'
            }), 400
        
        provider = data['provider'].lower()
        api_key = data['api_key'].strip()
        
        # Provider 검증
        if provider not in ['anthropic', 'openai']:
            return jsonify({
                'success': False,
                'error': 'Provider는 anthropic 또는 openai만 가능합니다.',
                'code': 'INVALID_PROVIDER'
            }), 400
        
        # API 키 형식 검증
        if provider == 'anthropic' and not api_key.startswith('sk-ant-'):
            return jsonify({
                'success': False,
                'error': 'Invalid Anthropic API key format',
                'code': 'INVALID_KEY_FORMAT'
            }), 400
        elif provider == 'openai' and not api_key.startswith('sk-'):
            return jsonify({
                'success': False,
                'error': 'Invalid OpenAI API key format',
                'code': 'INVALID_KEY_FORMAT'
            }), 400
        
        # 암호화
        encryptor = create_api_key_encryptor()
        encrypted_key = encryptor.encrypt(api_key)
        
        # 기존 키 확인
        existing_key = UserApiKey.query.filter_by(
            user_id=current_user_id,
            provider=provider
        ).first()
        
        if existing_key:
            # 업데이트
            existing_key.encrypted_key = encrypted_key
            existing_key.updated_at = datetime.utcnow()
            message = f'{provider.capitalize()} API 키가 업데이트되었습니다.'
        else:
            # 새로 생성
            new_key = UserApiKey(
                user_id=current_user_id,
                provider=provider,
                encrypted_key=encrypted_key
            )
            db.session.add(new_key)
            message = f'{provider.capitalize()} API 키가 저장되었습니다.'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message
        }), 200
        
    except Exception as e:
        logger.error(f"Save API key error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'API 키 저장 중 오류가 발생했습니다.',
            'code': 'SAVE_KEY_ERROR'
        }), 500

@user_bp.route('/api-keys/<provider>', methods=['DELETE'])
@jwt_required()
def delete_api_key(provider):
    """API 키 삭제"""
    try:
        current_user_id = get_jwt_identity()
        provider = provider.lower()
        
        if provider not in ['anthropic', 'openai']:
            return jsonify({
                'success': False,
                'error': 'Invalid provider',
                'code': 'INVALID_PROVIDER'
            }), 400
        
        # API 키 찾기
        api_key = UserApiKey.query.filter_by(
            user_id=current_user_id,
            provider=provider
        ).first()
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API 키를 찾을 수 없습니다.',
                'code': 'KEY_NOT_FOUND'
            }), 404
        
        db.session.delete(api_key)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{provider.capitalize()} API 키가 삭제되었습니다.'
        }), 200
        
    except Exception as e:
        logger.error(f"Delete API key error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'API 키 삭제 중 오류가 발생했습니다.',
            'code': 'DELETE_KEY_ERROR'
        }), 500

@user_bp.route('/api-keys/test', methods=['POST'])
@jwt_required()
def test_api_key():
    """
    저장된 API 키 테스트
    
    Request Body:
    {
        "provider": "anthropic" or "openai"
    }
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'provider' not in data:
            return jsonify({
                'success': False,
                'error': 'Provider를 지정해주세요.',
                'code': 'MISSING_PROVIDER'
            }), 400
        
        provider = data['provider'].lower()
        
        # 저장된 API 키 조회
        api_key_record = UserApiKey.query.filter_by(
            user_id=current_user_id,
            provider=provider
        ).first()
        
        if not api_key_record:
            return jsonify({
                'success': False,
                'error': f'{provider.capitalize()} API 키가 저장되지 않았습니다.',
                'code': 'KEY_NOT_FOUND'
            }), 404
        
        # 복호화
        encryptor = create_api_key_encryptor()
        api_key = encryptor.decrypt(api_key_record.encrypted_key)
        
        # 실제 API 호출로 테스트
        try:
            if provider == 'anthropic':
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hello"}]
                )
            elif provider == 'openai':
                import openai
                client = openai.OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hello"}]
                )
            
            return jsonify({
                'success': True,
                'message': f'{provider.capitalize()} API 키가 유효합니다.',
                'provider': provider
            }), 200
            
        except Exception as api_error:
            error_msg = str(api_error)
            if 'Incorrect API key' in error_msg or 'Invalid API key' in error_msg:
                return jsonify({
                    'success': False,
                    'error': 'API 키가 유효하지 않습니다.',
                    'code': 'INVALID_API_KEY'
                }), 401
            else:
                return jsonify({
                    'success': False,
                    'error': f'API 테스트 실패: {error_msg}',
                    'code': 'API_TEST_FAILED'
                }), 400
                
    except Exception as e:
        logger.error(f"Test API key error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'API 키 테스트 중 오류가 발생했습니다.',
            'code': 'TEST_KEY_ERROR'
        }), 500 