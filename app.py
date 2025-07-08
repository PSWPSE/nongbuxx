#!/usr/bin/env python3

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import traceback
import logging
from datetime import datetime
from pathlib import Path
import json
import uuid
from dotenv import load_dotenv

# Load environment variables from env.local file
load_dotenv('env.local')

# Import our existing modules
from nongbuxx_generator import NongbuxxGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# CORS configuration for production deployment
CORS(app, origins=[
    "http://localhost:3000",  # Local development
    "http://localhost:5000",  # Local development 
    "http://localhost:8080",  # Local development
    "https://nongbuxxfrontend.vercel.app",  # Main production frontend domain
    "https://nongbuxxfrontend-dsvsdvsdvsds-projects.vercel.app",  # Project-specific domain
    "https://nongbuxxfrontend-fgvw3eory-dsvsdvsdvsds-projects.vercel.app",  # New deployment URL
    "https://nongbuxx.vercel.app",  # Alternative domain
    "https://nongbuxx-frontend.vercel.app",  # Alternative domain
], allow_headers=["Content-Type", "Authorization", "Accept"], methods=["GET", "POST", "OPTIONS"], supports_credentials=False)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create necessary directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('generated_content', exist_ok=True)

# Store active jobs in memory (for production, use Redis or database)
active_jobs = {}

@app.route('/')
def index():
    """메인 페이지"""
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """정적 파일 제공"""
    return send_from_directory('static', filename)

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    """헬스 체크 엔드포인트"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        return response
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/validate-api-key', methods=['POST', 'OPTIONS'])
def validate_api_key():
    """API 키 유효성 검증 엔드포인트"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        return response
    
    try:
        data = request.get_json()
        
        if not data or 'api_provider' not in data or 'api_key' not in data:
            return jsonify({
                'success': False,
                'error': 'API provider and API key are required',
                'code': 'MISSING_PARAMETERS'
            }), 400
        
        api_provider = data['api_provider']
        api_key = data['api_key']
        
        if api_provider not in ['anthropic', 'openai']:
            return jsonify({
                'success': False,
                'error': 'API provider must be anthropic or openai',
                'code': 'INVALID_API_PROVIDER'
            }), 400
        
        if not api_key or len(api_key.strip()) < 10:
            return jsonify({
                'success': False,
                'error': 'Invalid API key format',
                'code': 'INVALID_API_KEY'
            }), 400
        
        # API 키 형식 기본 검증
        if api_provider == 'anthropic':
            if not api_key.startswith('sk-ant-'):
                return jsonify({
                    'success': False,
                    'error': 'Invalid Anthropic API key format',
                    'code': 'INVALID_ANTHROPIC_KEY'
                }), 400
        elif api_provider == 'openai':
            if not api_key.startswith('sk-'):
                return jsonify({
                    'success': False,
                    'error': 'Invalid OpenAI API key format',
                    'code': 'INVALID_OPENAI_KEY'
                }), 400
        
        # 실제 API 호출을 통한 유효성 검증
        try:
            if api_provider == 'anthropic':
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                # 간단한 테스트 메시지로 유효성 확인
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hello"}]
                )
                
            elif api_provider == 'openai':
                import openai
                client = openai.OpenAI(api_key=api_key)
                # 간단한 테스트 호출로 유효성 확인
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hello"}]
                )
            
            return jsonify({
                'success': True,
                'message': 'API key is valid',
                'provider': api_provider
            })
            
        except Exception as e:
            error_msg = str(e)
            if 'Incorrect API key' in error_msg or 'Invalid API key' in error_msg:
                return jsonify({
                    'success': False,
                    'error': 'Invalid API key',
                    'code': 'INVALID_API_KEY'
                }), 401
            elif 'exceeded' in error_msg.lower():
                return jsonify({
                    'success': False,
                    'error': 'API rate limit exceeded',
                    'code': 'RATE_LIMIT_EXCEEDED'
                }), 429
            else:
                return jsonify({
                    'success': False,
                    'error': f'API validation failed: {error_msg}',
                    'code': 'API_VALIDATION_FAILED'
                }), 400
                
    except Exception as e:
        logger.error(f"API key validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

@app.route('/api/generate', methods=['POST', 'OPTIONS'])
def generate_content():
    """
    콘텐츠 생성 API
    
    Request Body:
    {
        "url": "https://example.com/news",
        "api_provider": "anthropic",  // required: anthropic or openai
        "api_key": "sk-...",         // required: user's API key
        "filename": "custom_name",    // optional
        "save_intermediate": true     // optional
    }
    """
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        return response
    
    try:
        # 요청 데이터 파싱
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL is required',
                'code': 'MISSING_URL'
            }), 400
        
        # 필수 파라미터 확인
        required_fields = ['url', 'api_provider', 'api_key']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'{field} is required',
                    'code': f'MISSING_{field.upper()}'
                }), 400
        
        url = data['url']
        api_provider = data['api_provider']
        api_key = data['api_key']
        custom_filename = data.get('filename')
        save_intermediate = data.get('save_intermediate', False)
        
        # URL 기본 검증
        if not url.startswith(('http://', 'https://')):
            return jsonify({
                'success': False,
                'error': 'Invalid URL format',
                'code': 'INVALID_URL'
            }), 400
        
        # API 제공자 검증
        if api_provider not in ['anthropic', 'openai']:
            return jsonify({
                'success': False,
                'error': 'API provider must be anthropic or openai',
                'code': 'INVALID_API_PROVIDER'
            }), 400
        
        # API 키 기본 형식 검증
        if api_provider == 'anthropic' and not api_key.startswith('sk-ant-'):
            return jsonify({
                'success': False,
                'error': 'Invalid Anthropic API key format',
                'code': 'INVALID_ANTHROPIC_KEY'
            }), 400
        elif api_provider == 'openai' and not api_key.startswith('sk-'):
            return jsonify({
                'success': False,
                'error': 'Invalid OpenAI API key format',
                'code': 'INVALID_OPENAI_KEY'
            }), 400
        
        # 작업 ID 생성
        job_id = str(uuid.uuid4())
        active_jobs[job_id] = {
            'status': 'processing',
            'url': url,
            'started_at': datetime.now().isoformat(),
            'progress': 0
        }
        
        logger.info(f"Starting content generation for URL: {url} (Job ID: {job_id})")
        
        # NONGBUXX 생성기 초기화 (사용자 제공 API 키 사용)
        generator = NongbuxxGenerator(
            api_provider=api_provider,
            api_key=api_key,
            save_intermediate=save_intermediate
        )
        
        # 진행 상황 업데이트
        active_jobs[job_id]['progress'] = 25
        active_jobs[job_id]['status'] = 'extracting'
        
        # 콘텐츠 생성
        result = generator.generate_content(url, custom_filename)
        
        # 정리
        generator.cleanup()
        
        if result['success']:
            # 생성된 파일 읽기
            with open(result['output_file'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 작업 완료 처리
            active_jobs[job_id].update({
                'status': 'completed',
                'progress': 100,
                'completed_at': datetime.now().isoformat(),
                'output_file': str(result['output_file']),
                'title': result['title']
            })
            
            logger.info(f"Content generation completed for job {job_id}")
            
            return jsonify({
                'success': True,
                'job_id': job_id,
                'data': {
                    'title': result['title'],
                    'content': content,
                    'output_file': str(result['output_file']),
                    'timestamp': result['timestamp'],
                    'url': url,
                    'api_provider': api_provider
                }
            })
        else:
            # 작업 실패 처리
            active_jobs[job_id].update({
                'status': 'failed',
                'error': result['error'],
                'completed_at': datetime.now().isoformat()
            })
            
            logger.error(f"Content generation failed for job {job_id}: {result['error']}")
            
            # 에러 메시지에 따라 적절한 HTTP 상태 코드 반환
            error_msg = result['error']
            if '차단' in error_msg or '403' in error_msg:
                # 웹사이트에서 접근을 차단한 경우
                return jsonify({
                    'success': False,
                    'job_id': job_id,
                    'error': error_msg,
                    'code': 'ACCESS_BLOCKED'
                }), 403
            elif '찾을 수 없습니다' in error_msg or '404' in error_msg:
                # 페이지를 찾을 수 없는 경우
                return jsonify({
                    'success': False,
                    'job_id': job_id,
                    'error': error_msg,
                    'code': 'PAGE_NOT_FOUND'
                }), 404
            elif '시간 초과' in error_msg or 'timeout' in error_msg.lower():
                # 시간 초과 에러
                return jsonify({
                    'success': False,
                    'job_id': job_id,
                    'error': error_msg,
                    'code': 'REQUEST_TIMEOUT'
                }), 408
            elif '네트워크' in error_msg or 'connection' in error_msg.lower():
                # 네트워크 연결 오류
                return jsonify({
                    'success': False,
                    'job_id': job_id,
                    'error': error_msg,
                    'code': 'NETWORK_ERROR'
                }), 502
            else:
                # 기타 서버 오류
                return jsonify({
                    'success': False,
                    'job_id': job_id,
                    'error': error_msg,
                    'code': 'GENERATION_FAILED'
                }), 500
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Unexpected error in generate_content: {error_msg}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': f'Internal server error: {error_msg}',
            'code': 'INTERNAL_ERROR'
        }), 500

@app.route('/api/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """작업 상태 조회"""
    if job_id not in active_jobs:
        return jsonify({
            'success': False,
            'error': 'Job not found',
            'code': 'JOB_NOT_FOUND'
        }), 404
    
    job_info = active_jobs[job_id]
    return jsonify({
        'success': True,
        'job_id': job_id,
        'status': job_info['status'],
        'progress': job_info['progress'],
        'started_at': job_info['started_at'],
        'completed_at': job_info.get('completed_at'),
        'error': job_info.get('error')
    })

@app.route('/api/download/<job_id>', methods=['GET'])
def download_file(job_id):
    """생성된 파일 다운로드"""
    if job_id not in active_jobs:
        return jsonify({
            'success': False,
            'error': 'Job not found',
            'code': 'JOB_NOT_FOUND'
        }), 404
    
    job_info = active_jobs[job_id]
    
    if job_info['status'] != 'completed':
        return jsonify({
            'success': False,
            'error': 'Job not completed',
            'code': 'JOB_NOT_COMPLETED'
        }), 400
    
    file_path = Path(job_info['output_file'])
    if not file_path.exists():
        return jsonify({
            'success': False,
            'error': 'File not found',
            'code': 'FILE_NOT_FOUND'
        }), 404
    
    return send_from_directory(
        file_path.parent,
        file_path.name,
        as_attachment=True,
        mimetype='text/markdown'
    )

@app.route('/api/batch-generate', methods=['POST', 'OPTIONS'])
def batch_generate():
    """
    배치 콘텐츠 생성 API
    
    Request Body:
    {
        "urls": ["https://example1.com", "https://example2.com"],
        "api_provider": "anthropic",  // required: anthropic or openai
        "api_key": "sk-...",         // required: user's API key
        "save_intermediate": false
    }
    """
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        return response
    
    try:
        data = request.get_json()
        
        if not data or 'urls' not in data:
            return jsonify({
                'success': False,
                'error': 'URLs are required',
                'code': 'MISSING_URLS'
            }), 400
        
        # API 키 검증
        if 'api_provider' not in data or 'api_key' not in data:
            return jsonify({
                'success': False,
                'error': 'API provider and API key are required',
                'code': 'MISSING_API_CREDENTIALS'
            }), 400
        
        urls = data['urls']
        api_provider = data['api_provider']
        api_key = data['api_key']
        save_intermediate = data.get('save_intermediate', False)
        
        if not isinstance(urls, list) or len(urls) == 0:
            return jsonify({
                'success': False,
                'error': 'URLs must be a non-empty list',
                'code': 'INVALID_URLS'
            }), 400
        
        if api_provider not in ['anthropic', 'openai']:
            return jsonify({
                'success': False,
                'error': 'API provider must be anthropic or openai',
                'code': 'INVALID_API_PROVIDER'
            }), 400
        
        # 배치 작업 ID 생성
        batch_job_id = str(uuid.uuid4())
        active_jobs[batch_job_id] = {
            'status': 'processing',
            'type': 'batch',
            'urls': urls,
            'started_at': datetime.now().isoformat(),
            'progress': 0,
            'results': []
        }
        
        logger.info(f"Starting batch generation for {len(urls)} URLs (Job ID: {batch_job_id})")
        
        # NONGBUXX 생성기 초기화 (사용자 API 키 사용)
        generator = NongbuxxGenerator(
            api_provider=api_provider,
            api_key=api_key,  # 사용자 API 키 전달
            save_intermediate=save_intermediate
        )
        
        # 배치 처리
        results = generator.batch_generate(urls)
        
        # 정리
        generator.cleanup()
        
        # 결과 처리
        processed_results = []
        for result in results:
            if result['success']:
                with open(result['output_file'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                processed_results.append({
                    'success': True,
                    'url': result['url'],
                    'title': result['title'],
                    'content': content,
                    'output_file': str(result['output_file']),
                    'timestamp': result['timestamp']
                })
            else:
                processed_results.append({
                    'success': False,
                    'url': result['url'],
                    'error': result['error']
                })
        
        # 배치 작업 완료 처리
        active_jobs[batch_job_id].update({
            'status': 'completed',
            'progress': 100,
            'completed_at': datetime.now().isoformat(),
            'results': processed_results
        })
        
        success_count = sum(1 for r in processed_results if r['success'])
        
        logger.info(f"Batch generation completed for job {batch_job_id}: {success_count}/{len(urls)} successful")
        
        return jsonify({
            'success': True,
            'job_id': batch_job_id,
            'data': {
                'results': processed_results,
                'summary': {
                    'total': len(urls),
                    'successful': success_count,
                    'failed': len(urls) - success_count
                }
            }
        })
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Unexpected error in batch_generate: {error_msg}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': f'Internal server error: {error_msg}',
            'code': 'INTERNAL_ERROR'
        }), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'success': False,
        'error': 'Request entity too large',
        'code': 'REQUEST_TOO_LARGE'
    }), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Not found',
        'code': 'NOT_FOUND'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'code': 'INTERNAL_ERROR'
    }), 500

if __name__ == '__main__':
    # 환경 변수 확인
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Starting NONGBUXX API server on port {port}")
    logger.info(f"🔧 Debug mode: {debug}")
    logger.info(f"🌍 Environment: {os.getenv('FLASK_ENV', 'development')}")
    logger.info(f"🔑 API Keys - OpenAI: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT_SET'}, Anthropic: {'SET' if os.getenv('ANTHROPIC_API_KEY') else 'NOT_SET'}")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug)
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise 