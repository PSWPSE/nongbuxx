#!/usr/bin/env python3

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import traceback
import logging
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
import json
import uuid
from dotenv import load_dotenv

# Load environment variables from env.local file
load_dotenv('env.local')

from url_extractor import OptimizedNewsExtractor
from nongbuxx_generator import NongbuxxGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app with frontend as static folder
app = Flask(__name__, static_folder='frontend', static_url_path='/static')

# CORS configuration for production deployment
CORS(app, origins=[
    "http://localhost:3000",  # Local development
    "http://localhost:5000",  # Local development 
    "http://localhost:8080",  # Local development
    "https://nongbuxxfrontend.vercel.app",  # Main production frontend domain
    "https://nongbuxx.vercel.app",  # Alternative domain
], allow_headers=["Content-Type", "Authorization", "Accept"], methods=["GET", "POST", "OPTIONS"], supports_credentials=False)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create necessary directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('generated_content', exist_ok=True)

# Store active jobs in memory (for production, use Redis or database)
active_jobs = {}

# 🚀 성능 최적화: 메모리 캐싱 시스템
content_cache = {}  # URL별 생성된 콘텐츠 캐싱
cache_expiry = {}   # 캐시 만료 시간 관리

# 캐싱 헬퍼 함수들
def normalize_url(url):
    """URL 정규화 (캐싱 키 생성용)"""
    import re
    # 쿼리 파라미터 제거, 슬래시 정규화
    url = re.sub(r'\?.*$', '', url)
    url = url.rstrip('/')
    return url.lower()

def get_cache_key(url, content_type):
    """캐시 키 생성"""
    return f"{normalize_url(url)}:{content_type}"

def is_cache_valid(cache_key):
    """캐시 유효성 확인 (30분 유효)"""
    if cache_key not in cache_expiry:
        return False
    return time.time() < cache_expiry[cache_key]

def get_cached_content(url, content_type):
    """캐시된 콘텐츠 조회"""
    cache_key = get_cache_key(url, content_type)
    if cache_key in content_cache and is_cache_valid(cache_key):
        logger.info(f"🚀 캐시 히트: {url} (타입: {content_type})")
        return content_cache[cache_key]
    return None

def set_cached_content(url, content_type, content):
    """콘텐츠 캐싱"""
    cache_key = get_cache_key(url, content_type)
    content_cache[cache_key] = content
    cache_expiry[cache_key] = time.time() + 1800  # 30분 후 만료
    logger.info(f"💾 캐시 저장: {url} (타입: {content_type})")

def cleanup_expired_cache():
    """만료된 캐시 정리"""
    current_time = time.time()
    expired_keys = [k for k, exp_time in cache_expiry.items() if current_time > exp_time]
    for key in expired_keys:
        content_cache.pop(key, None)
        cache_expiry.pop(key, None)
    if expired_keys:
        logger.info(f"🧹 만료된 캐시 {len(expired_keys)}개 정리 완료")


# 기본 라우트들

@app.route('/')
def index():
    """메인 페이지"""
    return send_from_directory('frontend', 'index.html')

# 정적 파일은 Flask가 자동으로 처리합니다 (static_folder 설정)

@app.route('/favicon.ico')
def favicon():
    """favicon 요청 처리"""
    return '', 204  # No Content 응답으로 favicon 요청 무시

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

@app.route('/api/validate-key', methods=['POST', 'OPTIONS'])
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
        "save_intermediate": true,    // optional
        "content_type": "standard"    // optional: 'standard' or 'blog'
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
        content_type = data.get('content_type', 'standard')  # 기본값은 'standard'
        
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
        
        # 콘텐츠 타입 검증
        if content_type not in ['standard', 'blog', 'enhanced_blog', 'threads', 'x']:
            return jsonify({
                'success': False,
                'error': 'Content type must be standard, blog, enhanced_blog, threads, or x',
                'code': 'INVALID_CONTENT_TYPE'
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
            'content_type': content_type,
            'started_at': datetime.now().isoformat(),
            'progress': 0
        }
        
        logger.info(f"Starting content generation for URL: {url} (Job ID: {job_id}, Type: {content_type})")
        
        # 🚀 캐시 확인 (즉시 응답 가능)
        cached_result = get_cached_content(url, content_type)
        if cached_result:
            active_jobs[job_id].update({
                'status': 'completed',
                'progress': 100,
                'completed_at': datetime.now().isoformat(),
                'cached': True
            })
            return jsonify({
                'success': True,
                'job_id': job_id,
                'data': cached_result,
                'cached': True,
                'message': '캐시된 결과를 즉시 반환했습니다.'
            })
        
        # NONGBUXX 생성기 초기화 (사용자 제공 API 키 사용)
        generator = NongbuxxGenerator(
            api_provider=api_provider,
            api_key=api_key,
            save_intermediate=save_intermediate
        )
        
        # 진행 상황 업데이트
        active_jobs[job_id]['progress'] = 25
        active_jobs[job_id]['status'] = 'extracting'
        
        # 콘텐츠 생성 (콘텐츠 타입 전달)
        result = generator.generate_content(url, custom_filename, content_type)
        
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
                'title': result['title'],
                'content_type': result['content_type']
            })
            
            logger.info(f"Content generation completed for job {job_id} (Type: {content_type})")
            
            # 🚀 결과 캐싱 저장
            response_data = {
                'title': result['title'],
                'content': content,
                'output_file': str(result['output_file']),
                'timestamp': result['timestamp'],
                'url': url,
                'api_provider': api_provider,
                'content_type': result['content_type']
            }
            set_cached_content(url, content_type, response_data)
            
            return jsonify({
                'success': True,
                'job_id': job_id,
                'data': response_data,
                'cached': False
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
            else:
                # 기타 오류
                return jsonify({
                    'success': False,
                    'job_id': job_id,
                    'error': error_msg,
                    'code': 'GENERATION_FAILED'
            }), 500
            
    except Exception as e:
        logger.error(f"Content generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
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
        "save_intermediate": false,   // optional
        "content_type": "standard"    // optional: 'standard' or 'blog'
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
            logger.error(f"[BATCH-GENERATE] URLs 누락")
            return jsonify({
                'success': False,
                'error': 'URLs are required',
                'code': 'MISSING_URLS'
            }), 400
        
        # API 키 검증
        if 'api_provider' not in data or 'api_key' not in data:
            logger.error(f"[BATCH-GENERATE] API 자격 증명 누락")
            return jsonify({
                'success': False,
                'error': 'API provider and API key are required',
                'code': 'MISSING_API_CREDENTIALS'
            }), 400
        
        urls = data['urls']
        api_provider = data['api_provider']
        api_key = data['api_key']
        save_intermediate = data.get('save_intermediate', False)  # 성능 최적화: 기본값 False
        content_type = data.get('content_type', 'standard')  # 기본값은 'standard'
        selected_formats = data.get('selected_formats', None)  # 완성형 블로그 형식
        wordpress_type = data.get('wordpress_type', 'text')  # 워드프레스 형식 (text/html)
        
        if not isinstance(urls, list) or len(urls) == 0:
            return jsonify({
                'success': False,
                'error': 'URLs must be a non-empty list',
                'code': 'INVALID_URLS'
            }), 400
        
        # URL 개수 제한으로 타임아웃 방지
        if len(urls) > 20:
            return jsonify({
                'success': False,
                'error': 'Maximum 20 URLs allowed per batch to prevent timeout',
                'code': 'TOO_MANY_URLS'
            }), 400
        
        if api_provider not in ['anthropic', 'openai']:
            return jsonify({
                'success': False,
                'error': 'API provider must be anthropic or openai',
                'code': 'INVALID_API_PROVIDER'
            }), 400
        
        # 콘텐츠 타입 검증
        if content_type not in ['standard', 'blog', 'enhanced_blog', 'threads', 'x']:
            return jsonify({
                'success': False,
                'error': 'Content type must be standard, blog, enhanced_blog, threads, or x',
                'code': 'INVALID_CONTENT_TYPE'
            }), 400
        
        # 배치 작업 ID 생성
        batch_job_id = str(uuid.uuid4())
        active_jobs[batch_job_id] = {
            'status': 'processing',
            'type': 'batch',
            'urls': urls,
            'content_type': content_type,
            'started_at': datetime.now().isoformat(),
            'progress': 0,
            'results': []
        }
        
        logger.info(f"Starting batch generation for {len(urls)} URLs (Job ID: {batch_job_id}, Type: {content_type})")
        
        # NONGBUXX 생성기 초기화 (사용자 API 키 사용)
        generator = NongbuxxGenerator(
            api_provider=api_provider,
            api_key=api_key,  # 사용자 API 키 전달
            save_intermediate=save_intermediate
        )
        
        # 🚀 향상된 배치 처리 (콘텐츠 타입 전달)
        try:
            # 작업 시작 시간 기록
            start_time = time.time()
            
            # 예상 처리 시간 계산 (사용자 알림용)
            estimated_time_per_url = 30  # 기본값
            if content_type == 'blog':
                estimated_time_per_url = 45
            elif content_type == 'enhanced_blog':
                estimated_time_per_url = 60
            
            total_estimated_time = len(urls) * estimated_time_per_url
            
            # 작업 정보 업데이트
            active_jobs[batch_job_id].update({
                'estimated_time_seconds': total_estimated_time,
                'progress': 10
            })
            
            logger.info(f"Starting batch generation: {len(urls)} URLs, estimated time: {total_estimated_time}s")
            
            # 🧹 캐시 정리 (배치 처리 전)
            cleanup_expired_cache()
            
            # 배치 처리 실행 (워드프레스 타입 포함)
            results = generator.batch_generate(
                urls, 
                content_type=content_type,
                selected_formats=selected_formats,
                wordpress_type=wordpress_type
            )
            
            # 🎯 병렬처리 통계 수집
            parallel_stats = generator.get_parallel_stats()
            
            # 정리
            generator.cleanup()
            
            # 실제 처리 시간 계산
            actual_time = time.time() - start_time
            
            # 결과 처리 - 메모리 캐시에 저장
            processed_results = []
            for result in results:
                if result['success']:
                    # 파일에서 콘텐츠 읽기
                    with open(result['output_file'], 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 파일 영구 보관 (기존 방식 복원)
                    logger.info(f"파일 저장 완료: {result['output_file']}")
                    
                    processed_results.append({
                        'success': True,
                        'url': result['url'],
                        'title': result['title'],
                        'content': content,
                        'filename': result['output_file'].name,
                        'timestamp': result['timestamp'],
                        'content_type': result['content_type'],
                        'output_file': str(result['output_file'])
                    })
                else:
                    processed_results.append({
                        'success': False,
                        'url': result['url'],
                        'error': result['error']
                    })
            
            # 성공 통계
            success_count = sum(1 for r in processed_results if r['success'])
            
            # 작업 완료 처리
            active_jobs[batch_job_id].update({
                'status': 'completed',
                'progress': 100,
                'completed_at': datetime.now().isoformat(),
                'results': processed_results,
                'success_count': success_count,
                'total_count': len(urls),
                'actual_time_seconds': actual_time,
                'estimated_time_seconds': total_estimated_time
            })
            
            logger.info(f"Batch generation completed for job {batch_job_id}: {success_count}/{len(urls)} successful (Type: {content_type})")
            logger.info(f"Processing time: {actual_time:.2f}s (estimated: {total_estimated_time}s)")
            
            return jsonify({
                'success': True,
                'job_id': batch_job_id,
                'data': {
                    'results': processed_results,
                    'success_count': success_count,
                    'total_count': len(urls),
                    'api_provider': api_provider,
                    'content_type': content_type,
                    'processing_time_seconds': actual_time,
                    'parallel_stats': {
                        'max_workers': 3,
                        'completed_threads': parallel_stats.get('completed_tasks', 0),
                        'failed_threads': parallel_stats.get('failed_tasks', 0),
                        'total_threads': parallel_stats.get('completed_tasks', 0) + parallel_stats.get('failed_tasks', 0),
                        'parallel_efficiency': f"{((actual_time / len(urls) / 3) * 100):.1f}%" if len(urls) > 0 else "100%",
                        'speedup_factor': f"{3:.1f}x" if len(urls) > 1 else "1x"
                    }
                }
            })
            
        except Exception as processing_error:
            # 처리 중 오류 발생
            error_msg = str(processing_error)
            logger.error(f"Batch processing error: {error_msg}")
            
            # 사용자 친화적 에러 메시지 생성
            if 'timeout' in error_msg.lower():
                user_error = "처리 시간이 초과되었습니다. 선택한 뉴스 개수를 줄여주세요."
            elif 'memory' in error_msg.lower():
                user_error = "서버 메모리가 부족합니다. 선택한 뉴스 개수를 줄여주세요."
            elif 'api' in error_msg.lower() and 'key' in error_msg.lower():
                user_error = "API 키에 문제가 있습니다. 키를 확인해주세요."
            elif 'rate' in error_msg.lower() and 'limit' in error_msg.lower():
                user_error = "API 사용량 한도가 초과되었습니다. 잠시 후 다시 시도해주세요."
            else:
                user_error = f"처리 중 오류가 발생했습니다: {error_msg}"
            
            # 작업 실패 처리
            active_jobs[batch_job_id].update({
                'status': 'failed',
                'error': user_error,
                'completed_at': datetime.now().isoformat()
            })
            
            return jsonify({
                'success': False,
                'error': user_error,
                'code': 'PROCESSING_ERROR'
            }), 500
        
    except Exception as e:
        logger.error(f"Batch generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

@app.route('/api/extract-news-links', methods=['POST', 'OPTIONS'])
def extract_news_links():
    """
    뉴스 링크 추출 API (다중 출처 지원)
    
    Request Body:
    {
        "keyword": "Tesla AI",           // optional: 검색 키워드
        "count": 10,                    // optional: 추출할 뉴스 개수 (기본값: 10)
        "sources": ["yahoo_finance"]     // optional: 출처 ID 배열 (기본값: 활성화된 모든 출처)
    }
    """
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        return response
    
    try:
        data = request.get_json() or {}
        
        keyword = data.get('keyword', '').strip()
        count = data.get('count', 10)
        requested_sources = data.get('sources', [])
        
        # 입력값 검증
        if count < 1 or count > 50:
            return jsonify({
                'success': False,
                'error': '뉴스 개수는 1~50개 사이여야 합니다.',
                'code': 'INVALID_COUNT'
            }), 400
        
        # 사용할 출처 결정 (계층적 구조 지원)
        available_sources = get_all_extractable_sources()  # 서브카테고리 포함
        
        if requested_sources:
            # 요청된 출처만 사용
            selected_sources = [s for s in available_sources if s['id'] in requested_sources and s.get('active', True)]
            if not selected_sources:
                return jsonify({
                    'success': False,
                    'error': '요청된 출처 중 활성화된 출처가 없습니다.',
                    'code': 'NO_ACTIVE_SOURCES'
                }), 400
        else:
            # 활성화된 모든 출처 사용
            selected_sources = [s for s in available_sources if s.get('active', True)]
            if not selected_sources:
                return jsonify({
                    'success': False,
                    'error': '활성화된 출처가 없습니다.',
                    'code': 'NO_ACTIVE_SOURCES'
                }), 400
        
        logger.info(f"Starting multi-source news extraction - keyword: '{keyword}', count: {count}, sources: {[s['id'] for s in selected_sources]}")
        
        # 병렬 처리로 뉴스 추출 (성능 최적화)
        from url_extractor import extract_news_from_multiple_sources
        
        logger.info(f"병렬 뉴스 추출 시작: {len(selected_sources)}개 출처")
        start_time = time.time()
        
        # 병렬 처리로 모든 출처에서 동시에 뉴스 추출
        all_news_items = extract_news_from_multiple_sources(
            sources=selected_sources,
            keyword=keyword,
            count=count,
            max_workers=min(len(selected_sources), 8)  # 최대 8개 동시 처리 (성능 최적화)
        )
        
        end_time = time.time()
        logger.info(f"병렬 추출 완료: {len(all_news_items)}개 뉴스, 소요시간: {end_time - start_time:.2f}초")
        
        # 출처별 결과 통계
        source_results = []
        source_counts = {}
        
        for item in all_news_items:
            source_id = item.get('source_id')
            if source_id:
                source_counts[source_id] = source_counts.get(source_id, 0) + 1
        
        for source in selected_sources:
            count_extracted = source_counts.get(source['id'], 0)
            source_results.append({
                'source_id': source['id'],
                'source_name': source['name'],
                'count': count_extracted,
                'success': count_extracted > 0
            })
            
            # 성공한 소스만 로깅 (성능 최적화)
            if count_extracted > 0:
                logger.info(f"✅ {source['name']}: {count_extracted}개 뉴스 추출")
        
        # 중복 제거 (URL 기준) - 같은 URL의 뉴스가 여러 소스에서 나올 때 소스 정보 병합
        unique_news = []
        seen_urls = {}
        
        for item in all_news_items:
            url = item['url']
            if url not in seen_urls:
                # 새로운 URL - 그대로 추가
                unique_news.append(item)
                seen_urls[url] = len(unique_news) - 1  # 인덱스 저장
            else:
                # 중복 URL - 기존 아이템에 소스 정보 병합
                existing_index = seen_urls[url]
                existing_item = unique_news[existing_index]
                
                # 소스 정보 병합 (여러 소스에서 같은 뉴스가 나올 때)
                if existing_item['source_name'] != item['source_name']:
                    existing_item['source_name'] = f"{existing_item['source_name']}, {item['source_name']}"
                    
                # 키워드 병합 (중복 제거)
                if item.get('keywords'):
                    existing_keywords = set(existing_item.get('keywords', []))
                    new_keywords = set(item['keywords'])
                    merged_keywords = list(existing_keywords.union(new_keywords))
                    existing_item['keywords'] = merged_keywords
        
        # 중복 제거 후 최종 결과 확인
        if not unique_news:
            return jsonify({
                'success': False,
                'error': f"'{keyword}' 키워드와 관련된 뉴스를 찾을 수 없습니다." if keyword and keyword.strip() else '선택한 출처에서 뉴스를 찾을 수 없습니다. 출처 설정을 확인해주세요.',
                'code': 'NO_NEWS_FOUND',
                'source_results': source_results
            }), 404
        
        # 관련도 순으로 정렬 (키워드가 있는 경우)
        if keyword:
            keyword_lower = keyword.lower()
            unique_news.sort(key=lambda x: (
                keyword_lower in x['title'].lower(),
                sum(1 for kw in x.get('keywords', []) if keyword_lower in kw.lower())
            ), reverse=True)
        
        logger.info(f"Multi-source news extraction completed: {len(unique_news)} unique articles from {len(selected_sources)} sources")
        
        return jsonify({
            'success': True,
            'data': {
                'keyword': keyword,
                'count': len(unique_news),
                'total_extracted': len(all_news_items),
                'unique_count': len(unique_news),
                'news_items': unique_news,
                'source_results': source_results
            }
        })
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Multi-source news extraction error: {error_msg}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': f'뉴스 추출 중 오류가 발생했습니다: {error_msg}',
            'code': 'EXTRACTION_ERROR'
        }), 500

def extract_news_from_source(source, keyword, count):
    """특정 출처에서 뉴스 추출 (계층적 구조 지원)"""
    try:
        # 모든 출처에 대해 최적화된 추출기 사용
        from url_extractor import OptimizedNewsExtractor
        
        # 실제 추출 URL 결정 (계층적 구조 지원)
        extraction_url = source.get('full_url', source['url'])
        
        logger.info(f"Extracting news from {source['name']}")
        logger.info(f"Extraction URL: {extraction_url}")
        
        extractor = OptimizedNewsExtractor(
            base_url=extraction_url,
            search_keywords=keyword if keyword else None,
            max_news=count
        )
        
        return extractor.extract_news()
            
    except Exception as e:
        logger.error(f"Error extracting news from {source['name']}: {str(e)}")
        raise e

# ============================================================================
# 생성된 콘텐츠 관리 API
# ============================================================================

@app.route('/api/generated-content', methods=['GET'])
def get_generated_content():
    """생성된 콘텐츠 파일 목록 조회"""
    try:
        generated_dir = Path('generated_content')
        if not generated_dir.exists():
            return jsonify({
                'success': True,
                'data': {
                    'files': [],
                    'total_count': 0
                }
            })
        
        # 모든 .md 파일 찾기
        md_files = list(generated_dir.glob('*.md'))
        
        # 파일 정보 수집
        file_info = []
        for file_path in md_files:
            try:
                # 파일 메타데이터 읽기
                stat_info = file_path.stat()
                created_time = datetime.fromtimestamp(stat_info.st_ctime)
                modified_time = datetime.fromtimestamp(stat_info.st_mtime)
                
                # 파일 내용에서 제목 추출
                title = "제목 없음"
                content_type = "standard"
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                                    # 제목 추출 (마크다운 첫 번째 # 헤더 또는 이모지 제목)
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break
                    elif line and not line.startswith('##') and len(line) > 10:
                        # 첫 번째 줄이 제목 형태인 경우 (이모지 포함)
                        if any(ord(char) > 127 for char in line[:5]):  # 이모지 또는 특수문자 포함
                            title = line[:60] + ('...' if len(line) > 60 else '')
                            break
                    
                    # 콘텐츠 타입 판별
                    if 'blog_' in file_path.name:
                        content_type = "blog"
                
                file_info.append({
                    'filename': file_path.name,
                    'title': title,
                    'content_type': content_type,
                    'size': stat_info.st_size,
                    'created_at': created_time.isoformat(),
                    'modified_at': modified_time.isoformat(),
                    'url': f"/api/generated-content/{file_path.name}"
                })
                
            except Exception as e:
                logger.warning(f"파일 정보 읽기 실패: {file_path.name} - {e}")
                continue
        
        # 수정 시간 순으로 정렬 (최신 순)
        file_info.sort(key=lambda x: x['modified_at'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': {
                'files': file_info,
                'total_count': len(file_info)
            }
        })
        
    except Exception as e:
        logger.error(f"생성된 콘텐츠 목록 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': '생성된 콘텐츠 목록을 불러오는 중 오류가 발생했습니다.',
            'code': 'GENERATED_CONTENT_LIST_ERROR'
        }), 500

@app.route('/api/generated-content/<filename>', methods=['GET'])
def get_generated_content_file(filename):
    """특정 생성된 콘텐츠 파일 조회"""
    try:
        # 파일명 검증 (보안)
        if not filename.endswith('.md') or '..' in filename or '/' in filename:
            return jsonify({
                'success': False,
                'error': '유효하지 않은 파일명입니다.',
                'code': 'INVALID_FILENAME'
            }), 400
        
        file_path = Path('generated_content') / filename
        if not file_path.exists():
            return jsonify({
                'success': False,
                'error': '파일을 찾을 수 없습니다.',
                'code': 'FILE_NOT_FOUND'
            }), 404
        
        # 파일 내용 읽기
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 파일 정보
        stat_info = file_path.stat()
        
        # 제목 추출
        title = "제목 없음"
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        # 콘텐츠 타입 판별
        content_type = "blog" if 'blog_' in filename else "standard"
        
        return jsonify({
            'success': True,
            'data': {
                'filename': filename,
                'title': title,
                'content': content,
                'content_type': content_type,
                'size': stat_info.st_size,
                'created_at': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                'modified_at': datetime.fromtimestamp(stat_info.st_mtime).isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"생성된 콘텐츠 파일 조회 실패: {filename} - {e}")
        return jsonify({
            'success': False,
            'error': '파일을 읽는 중 오류가 발생했습니다.',
            'code': 'FILE_READ_ERROR'
        }), 500

@app.route('/api/generated-content/<filename>', methods=['DELETE'])
def delete_generated_content_file(filename):
    """특정 생성된 콘텐츠 파일 삭제"""
    try:
        # 파일명 검증 (보안)
        if not filename.endswith('.md') or '..' in filename or '/' in filename:
            return jsonify({
                'success': False,
                'error': '유효하지 않은 파일명입니다.',
                'code': 'INVALID_FILENAME'
            }), 400
        
        file_path = Path('generated_content') / filename
        if not file_path.exists():
            return jsonify({
                'success': False,
                'error': '파일을 찾을 수 없습니다.',
                'code': 'FILE_NOT_FOUND'
            }), 404
        
        # 파일 삭제
        file_path.unlink()
        
        logger.info(f"생성된 콘텐츠 파일 삭제 완료: {filename}")
        
        return jsonify({
            'success': True,
            'message': '파일이 성공적으로 삭제되었습니다.',
            'filename': filename
        })
        
    except Exception as e:
        logger.error(f"생성된 콘텐츠 파일 삭제 실패: {filename} - {e}")
        return jsonify({
            'success': False,
            'error': '파일을 삭제하는 중 오류가 발생했습니다.',
            'code': 'FILE_DELETE_ERROR'
        }), 500



# ============================================================================
# 출처 관리 API
# ============================================================================

def load_sources():
    """출처 정보를 JSON 파일에서 로드 (계층적 구조 지원)"""
    # Railway에서도 작동하도록 절대 경로 사용
    sources_file = Path(__file__).parent / 'data' / 'sources.json'
    try:
        if sources_file.exists():
            with open(sources_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('sources', [])
        else:
            # 기본 출처 데이터로 파일 생성
            default_sources = [{
                "id": "yahoo_finance",
                "name": "Yahoo Finance",
                "url": "https://finance.yahoo.com/topic/latest-news/",
                "parser_type": "yahoo_finance",
                "active": True,
                "description": "글로벌 금융 뉴스 및 시장 정보",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }]
            save_sources(default_sources)
            return default_sources
    except Exception as e:
        logger.error(f"Failed to load sources: {e}")
        return []

def save_sources(sources):
    """출처 정보를 JSON 파일에 저장"""
    # Railway에서도 작동하도록 절대 경로 사용
    sources_file = Path(__file__).parent / 'data' / 'sources.json'
    try:
        # data 디렉토리 생성
        sources_file.parent.mkdir(exist_ok=True)
        
        data = {
            "sources": sources,
            "updated_at": datetime.now().isoformat()
        }
        
        with open(sources_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"Failed to save sources: {e}")
        return False

def find_source_by_id(source_id):
    """ID로 출처 찾기 (계층적 구조 지원)"""
    sources = load_sources()
    
    # 부모 출처에서 찾기
    for source in sources:
        if source['id'] == source_id:
            return source
            
        # 서브 카테고리에서 찾기
        if 'subcategories' in source:
            for subcategory in source['subcategories']:
                if subcategory['id'] == source_id:
                    # 부모 URL과 서브 카테고리 URL 결합
                    subcategory_copy = subcategory.copy()
                    subcategory_copy['full_url'] = source['url'].rstrip('/') + subcategory['url']
                    subcategory_copy['parent_id'] = source['id']
                    subcategory_copy['parent_name'] = source['name']
                    return subcategory_copy
    
    return None

def get_all_extractable_sources():
    """추출 가능한 모든 출처 반환 (서브 카테고리 포함)"""
    sources = load_sources()
    extractable_sources = []
    
    for source in sources:
        if source.get('is_parent', False):
            # 부모 출처인 경우 서브 카테고리들 추가
            if 'subcategories' in source:
                for subcategory in source['subcategories']:
                    if subcategory.get('active', True):
                        subcategory_copy = subcategory.copy()
                        subcategory_copy['full_url'] = source['url'].rstrip('/') + subcategory['url']
                        subcategory_copy['parent_id'] = source['id']
                        subcategory_copy['parent_name'] = source['name']
                        subcategory_copy['parent_url'] = source['url']
                        extractable_sources.append(subcategory_copy)
        else:
            # 단독 출처인 경우
            if source.get('active', True):
                extractable_sources.append(source)
    
    return extractable_sources

def get_all_sources_with_structure():
    """계층적 구조를 포함한 모든 출처 반환"""
    sources = load_sources()
    result = {
        'parent_sources': [],
        'standalone_sources': [],
        'extractable_sources': []
    }
    
    for source in sources:
        if source.get('is_parent', False):
            # 부모 출처 추가
            result['parent_sources'].append(source)
            
            # 서브 카테고리들을 extractable_sources에 추가
            if 'subcategories' in source:
                for subcategory in source['subcategories']:
                    if subcategory.get('active', True):
                        subcategory_copy = subcategory.copy()
                        subcategory_copy['full_url'] = source['url'].rstrip('/') + subcategory['url']
                        subcategory_copy['parent_id'] = source['id']
                        subcategory_copy['parent_name'] = source['name']
                        subcategory_copy['parent_url'] = source['url']
                        result['extractable_sources'].append(subcategory_copy)
        else:
            # 단독 출처인 경우
            if source.get('active', True):
                result['standalone_sources'].append(source)
                result['extractable_sources'].append(source)
    
    return result

def validate_source_data(data):
    """출처 데이터 유효성 검증"""
    required_fields = ['name', 'url']
    for field in required_fields:
        if not data.get(field):
            return False, f'{field} is required'
    
    # URL 유효성 검증
    url = data.get('url', '')
    if not url.startswith(('http://', 'https://')):
        return False, 'Invalid URL format'
    
    return True, None

@app.route('/api/sources/extractable', methods=['GET'])
def get_extractable_sources():
    """추출 가능한 출처 목록 조회 (서브 카테고리 포함)"""
    try:
        extractable_sources = get_all_extractable_sources()
        
        return jsonify({
            'success': True,
            'data': {
                'sources': extractable_sources,
                'total_count': len(extractable_sources)
            }
        })
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to get extractable sources: {error_msg}")
        
        return jsonify({
            'success': False,
            'error': f'추출 가능한 출처 목록을 불러오는 중 오류가 발생했습니다: {error_msg}',
            'code': 'EXTRACTABLE_SOURCES_ERROR'
        }), 500

@app.route('/api/sources/structured', methods=['GET'])
def get_structured_sources():
    """계층적 구조를 포함한 출처 목록 조회"""
    try:
        structured_sources = get_all_sources_with_structure()
        
        return jsonify({
            'success': True,
            'data': structured_sources
        })
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to get structured sources: {error_msg}")
        
        return jsonify({
            'success': False,
            'error': f'계층적 출처 목록을 불러오는 중 오류가 발생했습니다: {error_msg}',
            'code': 'STRUCTURED_SOURCES_ERROR'
        }), 500

@app.route('/api/sources', methods=['GET', 'OPTIONS'])
def get_sources():
    """모든 출처 조회"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        return response
    
    try:
        sources = load_sources()
        
        return jsonify({
            'success': True,
            'data': {
                'sources': sources,
                'total_count': len(sources)
            }
        })
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to get sources: {error_msg}")
        
        return jsonify({
            'success': False,
            'error': f'출처 목록을 불러오는 중 오류가 발생했습니다: {error_msg}',
            'code': 'SOURCES_LOAD_ERROR'
        }), 500

@app.route('/api/sources', methods=['POST'])
def create_source():
    """새 출처 등록 (계층적 구조 지원)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request data is required',
                'code': 'MISSING_DATA'
            }), 400
        
        # 데이터 유효성 검증
        is_valid, error_msg = validate_source_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg,
                'code': 'INVALID_DATA'
            }), 400
        
        # 기존 출처 로드
        sources = load_sources()
        
        # 고유 ID 생성
        source_id = data.get('id') or f"source_{uuid.uuid4().hex[:8]}"
        
        # ID 중복 확인
        if any(source['id'] == source_id for source in sources):
            return jsonify({
                'success': False,
                'error': 'Source ID already exists',
                'code': 'DUPLICATE_ID'
            }), 400
        
        # 새 출처 객체 생성
        new_source = {
            'id': source_id,
            'name': data['name'],
            'url': data['url'],
            'is_parent': data.get('is_parent', False),
            'active': data.get('active', True),
            'description': data.get('description', ''),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 단독 출처인 경우에만 parser_type 추가
        if not new_source['is_parent']:
            new_source['parser_type'] = data.get('parser_type', 'generic')
        
        # 서브 카테고리 추가 (부모 출처인 경우)
        if new_source['is_parent'] and 'subcategories' in data:
            new_source['subcategories'] = []
            for subcategory in data['subcategories']:
                subcategory_obj = {
                    'id': subcategory.get('id') or f"sub_{uuid.uuid4().hex[:8]}",
                    'name': subcategory['name'],
                    'url': subcategory['url'],
                    'parser_type': subcategory.get('parser_type', 'universal'),
                    'active': subcategory.get('active', True),
                    'description': subcategory.get('description', ''),
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                new_source['subcategories'].append(subcategory_obj)
        
        # 출처 목록에 추가
        sources.append(new_source)
        
        # 저장
        if save_sources(sources):
            logger.info(f"New source created: {source_id} - {new_source['name']}")
            
            return jsonify({
                'success': True,
                'data': new_source,
                'message': '출처가 성공적으로 등록되었습니다.'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save source',
                'code': 'SAVE_ERROR'
            }), 500
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to create source: {error_msg}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': f'출처 등록 중 오류가 발생했습니다: {error_msg}',
            'code': 'CREATE_SOURCE_ERROR'
        }), 500

@app.route('/api/sources/<source_id>', methods=['GET', 'OPTIONS'])
def get_source(source_id):
    """특정 출처 조회"""
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        response.headers['Access-Control-Allow-Methods'] = 'GET, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        return response
    
    try:
        source = find_source_by_id(source_id)
        
        if not source:
            return jsonify({
                'success': False,
                'error': 'Source not found',
                'code': 'SOURCE_NOT_FOUND'
            }), 404
        
        return jsonify({
            'success': True,
            'data': source
        })
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to get source {source_id}: {error_msg}")
        
        return jsonify({
            'success': False,
            'error': f'출처 조회 중 오류가 발생했습니다: {error_msg}',
            'code': 'GET_SOURCE_ERROR'
        }), 500

@app.route('/api/sources/<source_id>', methods=['PUT'])
def update_source(source_id):
    """출처 수정"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request data is required',
                'code': 'MISSING_DATA'
            }), 400
        
        # 데이터 유효성 검증
        is_valid, error_msg = validate_source_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_msg,
                'code': 'INVALID_DATA'
            }), 400
        
        # 기존 출처 로드
        sources = load_sources()
        
        # 출처 찾기
        source_index = next((i for i, source in enumerate(sources) if source['id'] == source_id), None)
        
        if source_index is None:
            return jsonify({
                'success': False,
                'error': 'Source not found',
                'code': 'SOURCE_NOT_FOUND'
            }), 404
        
        # 출처 정보 업데이트
        existing_source = sources[source_index]
        updated_source = {
            **existing_source,
            'name': data['name'],
            'url': data['url'],
            'is_parent': data.get('is_parent', existing_source.get('is_parent', False)),
            'active': data.get('active', existing_source.get('active', True)),
            'description': data.get('description', existing_source.get('description', '')),
            'updated_at': datetime.now().isoformat()
        }
        
        # 부모 출처가 아닌 경우에만 parser_type 추가
        if not updated_source['is_parent']:
            updated_source['parser_type'] = data.get('parser_type', existing_source.get('parser_type', 'generic'))
        
        # 서브카테고리 업데이트 (부모 출처인 경우)
        if updated_source['is_parent'] and 'subcategories' in data:
            updated_source['subcategories'] = []
            for subcategory in data['subcategories']:
                subcategory_obj = {
                    'id': subcategory.get('id') or f"sub_{uuid.uuid4().hex[:8]}",
                    'name': subcategory['name'],
                    'url': subcategory['url'],
                    'parser_type': subcategory.get('parser_type', 'universal'),
                    'active': subcategory.get('active', True),
                    'description': subcategory.get('description', ''),
                    'created_at': subcategory.get('created_at', datetime.now().isoformat()),
                    'updated_at': datetime.now().isoformat()
                }
                updated_source['subcategories'].append(subcategory_obj)
        
        sources[source_index] = updated_source
        
        # 저장
        if save_sources(sources):
            logger.info(f"Source updated: {source_id} - {updated_source['name']}")
            
            return jsonify({
                'success': True,
                'data': updated_source,
                'message': '출처가 성공적으로 수정되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save source',
                'code': 'SAVE_ERROR'
            }), 500
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to update source {source_id}: {error_msg}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': f'출처 수정 중 오류가 발생했습니다: {error_msg}',
            'code': 'UPDATE_SOURCE_ERROR'
        }), 500

@app.route('/api/sources/<source_id>', methods=['DELETE'])
def delete_source(source_id):
    """출처 삭제 (계층적 구조 지원)"""
    try:
        # 기존 출처 로드
        sources = load_sources()
        
        # 출처 찾기 (부모 출처 및 서브 카테고리 모두 검색)
        source_index = None
        parent_index = None
        subcategory_index = None
        
        for i, source in enumerate(sources):
            if source['id'] == source_id:
                source_index = i
                break
            
            # 서브 카테고리에서 찾기
            if 'subcategories' in source:
                for j, subcategory in enumerate(source['subcategories']):
                    if subcategory['id'] == source_id:
                        parent_index = i
                        subcategory_index = j
                        break
        
        if source_index is not None:
            # 부모 출처 삭제
            if len(sources) <= 1:
                return jsonify({
                    'success': False,
                    'error': '최소 하나의 출처는 유지되어야 합니다.',
                    'code': 'MINIMUM_SOURCES_REQUIRED'
                }), 400
            
            deleted_source = sources.pop(source_index)
        elif parent_index is not None and subcategory_index is not None:
            # 서브 카테고리 삭제
            deleted_source = sources[parent_index]['subcategories'].pop(subcategory_index)
        else:
            return jsonify({
                'success': False,
                'error': 'Source not found',
                'code': 'SOURCE_NOT_FOUND'
            }), 404
        
        # 저장
        if save_sources(sources):
            logger.info(f"Source deleted: {source_id} - {deleted_source['name']}")
            
            return jsonify({
                'success': True,
                'data': deleted_source,
                'message': '출처가 성공적으로 삭제되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save sources',
                'code': 'SAVE_ERROR'
            }), 500
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to delete source {source_id}: {error_msg}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': f'출처 삭제 중 오류가 발생했습니다: {error_msg}',
            'code': 'DELETE_SOURCE_ERROR'
        }), 500

@app.route('/api/sources/<parent_id>/subcategories', methods=['POST'])
def add_subcategory(parent_id):
    """서브 카테고리 추가"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request data is required',
                'code': 'MISSING_DATA'
            }), 400
        
        # 부모 출처 찾기
        sources = load_sources()
        parent_source = None
        parent_index = None
        
        for i, source in enumerate(sources):
            if source['id'] == parent_id:
                parent_source = source
                parent_index = i
                break
        
        if not parent_source:
            return jsonify({
                'success': False,
                'error': 'Parent source not found',
                'code': 'PARENT_NOT_FOUND'
            }), 404
        
        if not parent_source.get('is_parent', False):
            return jsonify({
                'success': False,
                'error': 'Source is not a parent source',
                'code': 'NOT_PARENT_SOURCE'
            }), 400
        
        # 서브 카테고리 객체 생성
        subcategory_id = data.get('id') or f"sub_{uuid.uuid4().hex[:8]}"
        new_subcategory = {
            'id': subcategory_id,
            'name': data['name'],
            'url': data['url'],
            'parser_type': data.get('parser_type', 'universal'),
            'active': data.get('active', True),
            'description': data.get('description', ''),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 서브 카테고리 목록이 없으면 생성
        if 'subcategories' not in parent_source:
            parent_source['subcategories'] = []
        
        # 서브 카테고리 추가
        parent_source['subcategories'].append(new_subcategory)
        parent_source['updated_at'] = datetime.now().isoformat()
        
        # 저장
        if save_sources(sources):
            logger.info(f"Subcategory added: {subcategory_id} - {new_subcategory['name']}")
            
            return jsonify({
                'success': True,
                'data': new_subcategory,
                'message': '서브 카테고리가 성공적으로 추가되었습니다.'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save sources',
                'code': 'SAVE_ERROR'
            }), 500
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to add subcategory: {error_msg}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': f'서브 카테고리 추가 중 오류가 발생했습니다: {error_msg}',
            'code': 'ADD_SUBCATEGORY_ERROR'
        }), 500

@app.route('/api/cache-stats', methods=['GET'])
def get_cache_stats():
    """캐시 사용 통계 조회"""
    try:
        cleanup_expired_cache()  # 정리 후 통계 조회
        
        total_cache_size = len(content_cache)
        valid_cache_count = sum(1 for k in content_cache.keys() if is_cache_valid(k))
        
        return jsonify({
            'success': True,
            'cache_stats': {
                'total_cached_items': total_cache_size,
                'valid_cached_items': valid_cache_count,
                'expired_items_cleaned': total_cache_size - valid_cache_count,
                'cache_hit_potential': f"{(valid_cache_count / max(total_cache_size, 1)) * 100:.1f}%"
            },
            'performance_impact': {
                'potential_speedup': "2-3배 빠른 응답 (캐시된 항목)",
                'cache_duration': "30분",
                'memory_efficiency': "자동 만료 관리"
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# 기존 에러 핸들러들
# ============================================================================

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'success': False,
        'error': 'Request entity too large',
        'code': 'REQUEST_TOO_LARGE'
    }), 413

@app.errorhandler(404)
def not_found(error):
    """404 에러 처리"""
    # API 요청인 경우 JSON 응답
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'API endpoint not found',
            'code': 'NOT_FOUND',
            'path': request.path
        }), 404
    
    # favicon 요청은 빈 응답
    if request.path.endswith('.ico'):
        return '', 204
    
    # 기타 요청은 메인 페이지로 리다이렉트
    return send_from_directory('frontend', 'index.html')

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'code': 'INTERNAL_ERROR'
    }), 500

if __name__ == '__main__':
    # 환경 변수 확인
    port = int(os.getenv('PORT', 8080))  # Railway 기본 포트 8080
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"🚀 Starting NONGBUXX API server on port {port}")
    logger.info(f"🔧 Debug mode: {debug}")
    logger.info(f"🌍 Environment: {os.getenv('FLASK_ENV', 'development')}")
    logger.info(f"🔑 API Keys - OpenAI: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT_SET'}, Anthropic: {'SET' if os.getenv('ANTHROPIC_API_KEY') else 'NOT_SET'}")
    

    
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
                'app:app'
            ]
            logger.info(f"🚂 Railway environment detected, using gunicorn: {' '.join(cmd)}")
            subprocess.run(cmd)
        else:
            # 로컬 환경에서는 Flask 개발 서버 사용
            app.run(host='0.0.0.0', port=port, debug=debug)
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise 