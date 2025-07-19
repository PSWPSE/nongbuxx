#!/usr/bin/env python3
"""
NONGBUXX with Authentication
기존 app.py에 로그인 시스템을 통합한 버전
"""

# 기존 app.py의 모든 import와 설정을 가져옴
from app import *
from app_auth_config import init_auth, modify_existing_routes
from auth_middleware import optional_auth, require_api_key, track_user_content
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging

# 로거 설정
logger = logging.getLogger(__name__)

# 인증 시스템 초기화
print("🔐 인증 시스템 초기화 중...")
app = init_auth(app)

# JWT 설정 확인 (디버깅용)
jwt_key = app.config.get('JWT_SECRET_KEY', 'NOT_SET')
if jwt_key != 'NOT_SET':
    masked_key = f"{jwt_key[:10]}...{jwt_key[-10:]}" if len(jwt_key) > 20 else jwt_key
    print(f"📌 JWT Secret Key 설정됨: {masked_key}")
else:
    print("❌ JWT Secret Key가 설정되지 않았습니다!")

print("✅ 인증 시스템 초기화 완료")

# 기존 라우트에 선택적 인증 추가
modify_existing_routes(app)

# 인증이 적용된 콘텐츠 생성 엔드포인트
@app.route('/api/v2/generate', methods=['POST', 'OPTIONS'])
@require_api_key()
def generate_content_v2():
    """
    인증이 필요한 콘텐츠 생성 API (v2)
    사용자의 저장된 API 키를 사용합니다.
    """
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        return response
    
    try:
        data = request.get_json()
        
        # 사용자의 저장된 API 키 사용
        api_key = request.user_api_key
        api_provider = request.api_provider
        
        # 기존 generate_content 로직 활용
        url = data.get('url')
        content_type = data.get('content_type', 'standard')
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL은 필수입니다.',
                'code': 'MISSING_URL'
            }), 400
        
        # 작업 ID 생성
        job_id = str(uuid.uuid4())
        active_jobs[job_id] = {
            'status': 'processing',
            'url': url,
            'content_type': content_type,
            'started_at': datetime.now().isoformat(),
            'progress': 0
        }
        
        # NONGBUXX 생성기 초기화 (사용자의 API 키 사용)
        generator = NongbuxxGenerator(
            api_provider=api_provider,
            api_key=api_key,
            save_intermediate=False
        )
        
        # 콘텐츠 생성
        logger.info(f"Generating content for authenticated user: {get_jwt_identity()}")
        result = generator.process_url(url, content_type=content_type)
        
        if result['success']:
            # 사용자 콘텐츠 추적
            track_user_content(
                content_type=content_type,
                url=url,
                file_path=result.get('filename')
            )
            
            active_jobs[job_id].update({
                'status': 'completed',
                'progress': 100,
                'completed_at': datetime.now().isoformat()
            })
            
            return jsonify({
                'success': True,
                'job_id': job_id,
                'data': result,
                'message': '콘텐츠가 생성되었습니다.'
            })
        else:
            active_jobs[job_id].update({
                'status': 'failed',
                'error': result.get('error', 'Unknown error')
            })
            
            return jsonify({
                'success': False,
                'error': result.get('error', '콘텐츠 생성 실패'),
                'code': 'GENERATION_FAILED'
            }), 500
            
    except Exception as e:
        logger.error(f"Content generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': '콘텐츠 생성 중 오류가 발생했습니다.',
            'code': 'INTERNAL_ERROR'
        }), 500

# 사용자의 생성된 콘텐츠 목록
@app.route('/api/user/generated-content', methods=['GET'])
@jwt_required()
def get_user_generated_content():
    """사용자가 생성한 콘텐츠 목록 조회"""
    try:
        from models import GeneratedContent
        from flask_jwt_extended import get_jwt_identity
        
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # 페이지네이션
        contents = GeneratedContent.query.filter_by(user_id=current_user_id)\
            .order_by(GeneratedContent.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': {
                'contents': [c.to_dict() for c in contents.items],
                'total': contents.total,
                'page': page,
                'per_page': per_page,
                'pages': contents.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get user content error: {str(e)}")
        return jsonify({
            'success': False,
            'error': '콘텐츠 목록 조회 중 오류가 발생했습니다.',
            'code': 'GET_CONTENT_ERROR'
        }), 500

# 인증 상태 확인 엔드포인트
@app.route('/api/auth/status', methods=['GET'])
@optional_auth
def auth_status():
    """현재 인증 상태 확인"""
    if hasattr(request, 'current_user_id') and request.current_user_id:
        from models import User
        user = User.query.get(request.current_user_id)
        return jsonify({
            'success': True,
            'authenticated': True,
            'user': user.to_dict() if user else None
        }), 200
    else:
        return jsonify({
            'success': True,
            'authenticated': False,
            'user': None
        }), 200

# 임시 디버그 엔드포인트 (운영 환경에서는 제거해야 함)
@app.route('/debug/jwt', methods=['GET'])
def debug_jwt():
    """JWT 환경변수 확인 (디버깅용)"""
    import os
    jwt_key = os.getenv('JWT_SECRET_KEY', 'NOT_SET')
    
    # 보안을 위해 일부만 표시
    if jwt_key != 'NOT_SET':
        masked_key = f"{jwt_key[:10]}...{jwt_key[-10:]}"
    else:
        masked_key = "NOT_SET"
    
    return jsonify({
        'jwt_secret_key_set': jwt_key != 'NOT_SET',
        'jwt_secret_key_preview': masked_key,
        'config_jwt_key': app.config.get('JWT_SECRET_KEY', 'NOT_SET')[:20] + '...',
        'env_vars_count': len(os.environ),
        'railway_env': os.getenv('RAILWAY_ENVIRONMENT_NAME', 'NOT_SET')
    }), 200

if __name__ == '__main__':
    # 환경 변수 확인
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Starting NONGBUXX with Authentication on port {port}")
    logger.info(f"🔐 Authentication enabled")
    logger.info(f"🗄️ Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
    
    try:
        # Railway 환경에서는 gunicorn 사용
        if os.getenv('RAILWAY_ENVIRONMENT_NAME'):
            import subprocess
            cmd = [
                'gunicorn',
                '--bind', f'0.0.0.0:{port}',
                '--workers', '2',
                '--timeout', '600',
                '--keep-alive', '10',
                '--max-requests', '1000',
                '--max-requests-jitter', '50',
                'app_with_auth:app'  # app_with_auth 모듈 사용
            ]
            logger.info(f"🚂 Railway environment detected, using gunicorn")
            subprocess.run(cmd)
        else:
            # 로컬 환경에서는 Flask 개발 서버 사용
            app.run(host='0.0.0.0', port=port, debug=debug)
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise 