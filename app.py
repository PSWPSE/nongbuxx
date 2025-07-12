#!/usr/bin/env python3

from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
import os
import traceback
import logging
import time
from datetime import datetime
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
        if content_type not in ['standard', 'blog']:
            return jsonify({
                'success': False,
                'error': 'Content type must be standard or blog',
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
            
            return jsonify({
                'success': True,
                'job_id': job_id,
                'data': {
                    'title': result['title'],
                    'content': content,
                    'output_file': str(result['output_file']),
                    'timestamp': result['timestamp'],
                    'url': url,
                    'api_provider': api_provider,
                    'content_type': result['content_type']
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
        content_type = data.get('content_type', 'standard')  # 기본값은 'standard'
        
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
        
        # 콘텐츠 타입 검증
        if content_type not in ['standard', 'blog']:
            return jsonify({
                'success': False,
                'error': 'Content type must be standard or blog',
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
        
        # 배치 처리 (콘텐츠 타입 전달)
        results = generator.batch_generate(urls, content_type=content_type)
        
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
                    'timestamp': result['timestamp'],
                    'content_type': result['content_type']
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
            'total_count': len(urls)
        })
        
        logger.info(f"Batch generation completed for job {batch_job_id}: {success_count}/{len(urls)} successful (Type: {content_type})")
        
        return jsonify({
            'success': True,
            'job_id': batch_job_id,
            'data': {
                'results': processed_results,
                'success_count': success_count,
                'total_count': len(urls),
                'api_provider': api_provider,
                'content_type': content_type
            }
        })
        
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
            max_workers=min(len(selected_sources), 3)  # 최대 3개 동시 처리
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
            
            if count_extracted > 0:
                logger.info(f"✅ {source['name']}: {count_extracted}개 뉴스 추출")
            else:
                logger.warning(f"❌ {source['name']}: 뉴스 추출 실패")
        
        # 중복 제거 (URL 기준)
        unique_news = []
        seen_urls = set()
        
        for item in all_news_items:
            if item['url'] not in seen_urls:
                unique_news.append(item)
                seen_urls.add(item['url'])
        
        # 결과가 없는 경우
        if not unique_news:
            return jsonify({
                'success': False,
                'error': f"'{keyword}' 키워드와 관련된 뉴스를 찾을 수 없습니다." if keyword else '뉴스를 찾을 수 없습니다.',
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
# 출처 관리 API
# ============================================================================

def load_sources():
    """출처 정보를 JSON 파일에서 로드 (계층적 구조 지원)"""
    sources_file = Path('data/sources.json')
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
    sources_file = Path('data/sources.json')
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
                        extractable_sources.append(subcategory_copy)
        else:
            # 단독 출처인 경우
            if source.get('active', True):
                extractable_sources.append(source)
    
    return extractable_sources

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
            'parser_type': data.get('parser_type', existing_source.get('parser_type', 'generic')),
            'active': data.get('active', existing_source.get('active', True)),
            'description': data.get('description', existing_source.get('description', '')),
            'updated_at': datetime.now().isoformat()
        }
        
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