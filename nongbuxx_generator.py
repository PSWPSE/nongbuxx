#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading
from typing import Optional, Dict, List, Any

# Import our existing modules
from web_extractor import WebExtractor
from converter import NewsConverter
from blog_content_generator import BlogContentGenerator

class NongbuxxGenerator:
    def __init__(self, api_provider='anthropic', api_key=None, save_intermediate=True):
        """
        NONGBUXX 콘텐츠 생성기
        
        Args:
            api_provider: 'anthropic' 또는 'openai'
            api_key: 사용자 제공 API 키 (선택사항, 없으면 환경변수에서 읽기)
            save_intermediate: 중간 파일들을 저장할지 여부
        """
        self.api_provider = api_provider
        self.api_key = api_key
        self.save_intermediate = save_intermediate
        
        # 타입 힌트로 린터 오류 해결
        self.extractor: Optional[WebExtractor] = None
        self.converter: Optional[NewsConverter] = None
        self.blog_generator: Optional[BlogContentGenerator] = None
        
        # 초기화 상태 추적
        self._initialization_errors: List[str] = []
        self._is_properly_initialized = False
        
        # 병렬처리 모니터링을 위한 변수들
        self.parallel_stats: Dict[str, Any] = {
            'active_threads': set(),
            'completed_tasks': 0,
            'failed_tasks': 0,
            'start_time': None,
            'thread_timings': {}
        }
        
        try:
            # 출력 디렉토리 설정
            self.generated_dir = Path('generated_content')
            self.extracted_dir = Path('extracted_articles')
            
            # 디렉토리 생성
            self.generated_dir.mkdir(exist_ok=True)
            if save_intermediate:
                self.extracted_dir.mkdir(exist_ok=True)
            
            # 🛡️ 안전한 모듈 초기화 (각각 개별적으로 검증)
            self._initialize_components()
            
            # 최종 초기화 검증
            self._validate_initialization()
            
            key_status = "사용자 제공" if api_key else "환경변수"
            print(f"NONGBUXX Generator 초기화 완료 (API: {api_provider}, 키: {key_status})")
            
        except Exception as e:
            self._initialization_errors.append(f"전체 초기화 실패: {str(e)}")
            raise ValueError(f"NONGBUXX Generator 초기화 실패: {str(e)}")
        
    def _log_thread_activity(self, action, url, **kwargs):
        """병렬처리 스레드 활동을 로깅"""
        thread_id = threading.current_thread().ident
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        if action == 'start':
            self.parallel_stats['active_threads'].add(thread_id)
            self.parallel_stats['thread_timings'][thread_id] = {
                'start_time': time.time(),
                'url': url
            }
            print(f"🔄 [{timestamp}] 스레드-{thread_id} 시작: {url[:50]}...")
        elif action == 'complete':
            if thread_id in self.parallel_stats['active_threads']:
                self.parallel_stats['active_threads'].remove(thread_id)
            if thread_id in self.parallel_stats['thread_timings']:
                elapsed = time.time() - self.parallel_stats['thread_timings'][thread_id]['start_time']
                success = kwargs.get('success', False)
                if success:
                    self.parallel_stats['completed_tasks'] += 1
                    print(f"✅ [{timestamp}] 스레드-{thread_id} 완료: {elapsed:.2f}초 - {url[:50]}...")
                else:
                    self.parallel_stats['failed_tasks'] += 1
                    print(f"❌ [{timestamp}] 스레드-{thread_id} 실패: {elapsed:.2f}초 - {url[:50]}...")
                del self.parallel_stats['thread_timings'][thread_id]
        elif action == 'progress':
            print(f"📊 [{timestamp}] 스레드-{thread_id}: {kwargs.get('message', '')} - {url[:50]}...")
            
    def get_parallel_stats(self):
        """현재 병렬처리 통계 반환"""
        return {
            'active_threads_count': len(self.parallel_stats['active_threads']),
            'active_thread_ids': list(self.parallel_stats['active_threads']),
            'completed_tasks': self.parallel_stats['completed_tasks'],
            'failed_tasks': self.parallel_stats['failed_tasks'],
            'total_elapsed': time.time() - self.parallel_stats['start_time'] if self.parallel_stats['start_time'] else 0
        }
    
    def _initialize_components(self):
        """각 컴포넌트를 안전하게 초기화"""
        # WebExtractor 초기화
        try:
            self.extractor = WebExtractor(use_selenium=False, save_to_file=self.save_intermediate)
            if self.extractor is None:
                raise ValueError("WebExtractor 초기화 결과가 None입니다")
            print("✅ WebExtractor 초기화 성공")
        except Exception as e:
            error_msg = f"WebExtractor 초기화 실패: {str(e)}"
            self._initialization_errors.append(error_msg)
            raise ValueError(error_msg)
        
        # NewsConverter 초기화
        try:
            self.converter = NewsConverter(api_provider=self.api_provider, api_key=self.api_key)
            if self.converter is None:
                raise ValueError("NewsConverter 초기화 결과가 None입니다")
            
            # API 클라이언트 확인
            if self.api_provider == 'anthropic' and not hasattr(self.converter, 'anthropic_client'):
                raise ValueError("NewsConverter Anthropic 클라이언트 초기화 실패")
            elif self.api_provider == 'openai' and not hasattr(self.converter, 'openai_client'):
                raise ValueError("NewsConverter OpenAI 클라이언트 초기화 실패")
            
            print("✅ NewsConverter 초기화 성공")
        except Exception as e:
            error_msg = f"NewsConverter 초기화 실패: {str(e)}"
            self._initialization_errors.append(error_msg)
            raise ValueError(error_msg)
        
        # BlogContentGenerator 초기화
        try:
            self.blog_generator = BlogContentGenerator(api_provider=self.api_provider, api_key=self.api_key)
            if self.blog_generator is None:
                raise ValueError("BlogContentGenerator 초기화 결과가 None입니다")
            print("✅ BlogContentGenerator 초기화 성공")
        except Exception as e:
            error_msg = f"BlogContentGenerator 초기화 실패: {str(e)}"
            self._initialization_errors.append(error_msg)
            raise ValueError(error_msg)
    
    def _validate_initialization(self):
        """초기화 상태 검증"""
        validation_errors = []
        
        # 필수 컴포넌트 존재 확인
        if self.extractor is None:
            validation_errors.append("extractor가 None입니다")
        elif not hasattr(self.extractor, 'extract_data'):
            validation_errors.append("extractor에 extract_data 메서드가 없습니다")
        
        if self.converter is None:
            validation_errors.append("converter가 None입니다")
        elif not hasattr(self.converter, 'convert_from_data'):
            validation_errors.append("converter에 convert_from_data 메서드가 없습니다")
        
        if self.blog_generator is None:
            validation_errors.append("blog_generator가 None입니다")
        elif not hasattr(self.blog_generator, 'generate_rich_text_blog_content'):
            validation_errors.append("blog_generator에 generate_rich_text_blog_content 메서드가 없습니다")
        
        # 메서드 존재 확인
        if not hasattr(self, 'batch_generate'):
            validation_errors.append("batch_generate 메서드가 없습니다")
        elif not callable(getattr(self, 'batch_generate', None)):
            validation_errors.append("batch_generate가 호출 가능하지 않습니다")
        
        if validation_errors:
            error_msg = "초기화 검증 실패: " + "; ".join(validation_errors)
            self._initialization_errors.extend(validation_errors)
            raise ValueError(error_msg)
        
        self._is_properly_initialized = True
        print("✅ 모든 컴포넌트 초기화 검증 완료")
    
    def is_ready(self):
        """Generator가 사용 준비가 되었는지 확인"""
        return (
            self._is_properly_initialized and 
            self.extractor is not None and 
            self.converter is not None and 
            self.blog_generator is not None and
            len(self._initialization_errors) == 0
        )
    
    def get_initialization_errors(self):
        """초기화 중 발생한 에러 목록 반환"""
        return self._initialization_errors.copy()
    
    def validate_url(self, url):
        """URL 유효성 검사"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def extract_domain_name(self, url):
        """URL에서 도메인명 추출하여 파일명에 사용"""
        try:
            domain = urlparse(url).netloc
            # www. 제거 및 특수문자 정리
            domain = domain.replace('www.', '').replace('.', '_')
            return domain
        except:
            return 'article'
    
    def generate_content(self, url, custom_filename=None, content_type='standard', selected_formats=None, wordpress_type='text'):
        """
        URL에서 콘텐츠를 추출하고 마크다운으로 변환 (최적화된 버전)
        
        Args:
            url: 추출할 뉴스 기사 URL
            custom_filename: 사용자 지정 파일명 (선택사항)
            content_type: 콘텐츠 타입 ('standard', 'blog', 'enhanced_blog')
            selected_formats: 선택된 파일 형식 목록 (완성형 블로그 전용)
            wordpress_type: 워드프레스 형식 ('text' 또는 'html')
            
        Returns:
            dict: 결과 정보 (성공 여부, 파일 경로 등)
        """
        
        print(f"\n🔗 URL 분석 중: {url}")
        print(f"📝 콘텐츠 타입: {content_type}")
        
        # URL 유효성 검사
        if not self.validate_url(url):
            return {
                'success': False,
                'error': 'Invalid URL format',
                'url': url
            }
        
        # Step 1: 웹에서 콘텐츠 추출
        print("📄 웹 콘텐츠 추출 중...")
        start_time = time.time()
        
        # 웹 추출 (None 체크로 린터 오류 해결)
        if self.extractor is None:
            return {'success': False, 'error': 'Extractor not initialized', 'url': url}
        extracted_content = self.extractor.extract_data(url)
        
        if not extracted_content.get('success', False):
            return {
                'success': False,
                'error': f'Content extraction failed: {extracted_content.get("error", "Unknown error")}',
                'url': url
            }
        
        extraction_time = time.time() - start_time
        print(f"✅ 웹 추출 완료 ({extraction_time:.2f}초)")
        
        # Step 2: AI 변환
        print("🤖 AI 변환 중...")
        conversion_start = time.time()
        
        # 콘텐츠 타입에 따른 변환
        if content_type == 'enhanced_blog':
            # 새로운 완성형 블로그 콘텐츠 생성 (None 체크로 린터 오류 해결)
            if self.blog_generator is None:
                return {'success': False, 'error': 'Blog generator not initialized', 'url': url}
            rich_content = self.blog_generator.generate_rich_text_blog_content(extracted_content, wordpress_type)
            converted_content = rich_content['markdown']  # 기본적으로 마크다운 반환
            
            # 추가 형식들도 파일로 저장 (선택된 형식만)
            domain = self.extract_domain_name(url)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_prefix = f"{domain}_{timestamp}_enhanced_blog"
            
            # 선택된 형식만 저장 (extracted_content 전달하여 출처별 최적화)
            saved_files = self.blog_generator.save_blog_content(rich_content, filename_prefix, selected_formats, extracted_content, wordpress_type)
            print(f"✅ 완성형 블로그 콘텐츠 생성 완료 (선택된 형식: {selected_formats or 'all'})")
            
            # 생성된 파일 정보 반환에 추가
            # 메인 파일 경로 결정
            if saved_files:
                main_file = saved_files.get('md')
                if not main_file:
                    # md 파일이 없으면 첫 번째 파일 사용
                    main_file = list(saved_files.values())[0]
            else:
                # 파일이 없으면 에러 반환
                return {
                    'success': False,
                    'error': 'No files were saved',
                    'url': url
                }
            
            return {
                'success': True,
                'output_file': Path(main_file),  # 메인 파일 경로
                'saved_files': saved_files,  # 생성된 모든 파일 정보
                'title': extracted_content.get('title', '제목 없음'),
                'content_type': content_type,
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'processing_time': time.time() - start_time
            }
            
        elif content_type == 'blog':
            if self.converter is None:
                return {'success': False, 'error': 'Converter not initialized', 'url': url}
            converted_content = self.converter.convert_from_data_blog(extracted_content)
        elif content_type == 'threads':
            # Threads용 짧은 콘텐츠 생성 (490자 미만)
            if self.converter is None:
                return {'success': False, 'error': 'Converter not initialized', 'url': url}
            converted_content = self.converter.generate_threads_content({
                'title': extracted_content.get('title', ''),
                'description': extracted_content.get('description', ''),
                'content': extracted_content['content']['text']
            })
        elif content_type == 'x' or content_type == 'twitter':
            # X(Twitter)용 콘텐츠 생성
            if self.converter is None:
                return {'success': False, 'error': 'Converter not initialized', 'url': url}
            converted_content = self.converter.generate_x_content({
                'title': extracted_content.get('title', ''),
                'body': extracted_content['content']['text']
            })
        else:
            if self.converter is None:
                return {'success': False, 'error': 'Converter not initialized', 'url': url}
            converted_content = self.converter.convert_from_data(extracted_content)
        
        if not converted_content or not isinstance(converted_content, str):
            return {
                'success': False,
                'error': f'AI conversion failed: Invalid response format',
                'url': url
            }
        
        conversion_time = time.time() - conversion_start
        print(f"✅ AI 변환 완료 ({conversion_time:.2f}초)")
        
        # Step 3: 파일명 생성 및 저장 (일반 콘텐츠만 해당)
        if custom_filename:
            filename = f"{custom_filename}_{content_type}.md"
        else:
            domain = self.extract_domain_name(url)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{domain}_{timestamp}_{content_type}.md"
        
        output_file = self.generated_dir / filename
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(converted_content)
            
            total_time = time.time() - start_time
            print(f"💾 파일 저장 완료: {output_file} (총 {total_time:.2f}초)")
            
            # 제목 추출 (마크다운 첫 번째 줄에서)
            title = extracted_content.get('title', '제목 없음')
            
            return {
                'success': True,
                'output_file': output_file,
                'title': title,
                'content_type': content_type,
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'processing_time': total_time
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'File save failed: {str(e)}',
                'url': url
            }
    
    def batch_generate(self, urls, content_type='standard', selected_formats=None, max_workers=8, wordpress_type='text'):
        """
        다중 URL에서 콘텐츠를 병렬로 생성 (성능 최적화)
        
        Args:
            urls: URL 목록
            content_type: 콘텐츠 타입 ('standard', 'blog', 'enhanced_blog')
            selected_formats: 선택된 파일 형식 목록 (완성형 블로그 전용)
            max_workers: 최대 병렬 처리 수 (기본값: 8 - 성능 최적화)
            wordpress_type: 워드프레스 형식 ('text' 또는 'html')
            
        Returns:
            list: 각 URL의 결과 목록
        """
        if not urls:
            return []
        
        print(f"\n🚀 병렬 배치 생성 시작: {len(urls)}개 URL (타입: {content_type})")
        if content_type == 'enhanced_blog' and selected_formats:
            print(f"📋 선택된 형식: {selected_formats}")
        print(f"⚡ 최대 병렬 처리 수: {max_workers}")
        print(f"🎯 실제 병렬처리 확인: 각 스레드의 시작/완료 시간을 실시간으로 표시합니다")
        
        # 병렬처리 통계 초기화
        self.parallel_stats = {
            'active_threads': set(),
            'completed_tasks': 0,
            'failed_tasks': 0,
            'start_time': time.time(),
            'thread_timings': {}
        }
        
        start_time = time.time()
        
        # 🔧 순서 보장을 위한 개선된 병렬 처리
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # URL에 인덱스를 추가하여 순서 보장
            indexed_urls = [(i, url) for i, url in enumerate(urls)]
            
            # 각 URL에 대한 future 생성 (인덱스와 함께)
            future_to_index_url = {
                executor.submit(self._generate_with_index, index, url, content_type, selected_formats, wordpress_type): (index, url)
                for index, url in indexed_urls
            }
            
            # 결과를 인덱스 순서대로 정렬하기 위한 딕셔너리
            indexed_results = {}
            
            # 결과 수집
            for future in as_completed(future_to_index_url):
                index, url = future_to_index_url[future]
                try:
                    result = future.result()
                    indexed_results[index] = result
                    
                    if result['success']:
                        print(f"✅ 성공: {url}")
                    else:
                        print(f"❌ 실패: {url} - {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"❌ 예외 발생: {url} - {str(e)}")
                    indexed_results[index] = {
                        'success': False,
                        'error': str(e),
                        'url': url
                    }
        
        # 🔧 인덱스 순서대로 결과 정렬
        results = [indexed_results[i] for i in sorted(indexed_results.keys())]
        
        # 결과 통계
        success_count = sum(1 for r in results if r['success'])
        total_time = time.time() - start_time
        
        # 🎯 병렬처리 성능 통계 출력
        final_stats = self.get_parallel_stats()
        parallel_efficiency = (total_time / len(urls) / max_workers) * 100 if max_workers > 1 else 100
        
        print(f"\n📊 병렬 배치 생성 완료:")
        print(f"   • 성공: {success_count}/{len(urls)}")
        print(f"   • 실패: {final_stats['failed_tasks']}")
        print(f"   • 총 소요 시간: {total_time:.2f}초")
        print(f"   • 평균 시간: {total_time/len(urls):.2f}초/URL")
        print(f"   • 병렬 효율성: {parallel_efficiency:.1f}% (최대 {max_workers}개 동시 처리)")
        print(f"   • 완료된 스레드: {final_stats['completed_tasks'] + final_stats['failed_tasks']}개")
        
        if max_workers > 1:
            sequential_time = total_time * max_workers
            print(f"   🚀 병렬처리 덕분에 약 {sequential_time/total_time:.1f}배 빨라졌습니다!")
        
        return results
    
    def _generate_with_index(self, index, url, content_type='standard', selected_formats=None, wordpress_type='text'):
        """
        인덱스가 포함된 콘텐츠 생성 (파일명 중복 방지)
        
        Args:
            index: URL 순서 인덱스
            url: 추출할 뉴스 기사 URL
            content_type: 콘텐츠 타입
            selected_formats: 선택된 파일 형식 목록
            wordpress_type: 워드프레스 형식 ('text' 또는 'html')
            
        Returns:
            dict: 결과 정보
        """
        # 🎯 병렬처리 시작 로깅
        self._log_thread_activity('start', url)
        
        try:
            print(f"\n🔗 URL 분석 중: {url}")
            print(f"📝 콘텐츠 타입: {content_type}")
            
            # URL 유효성 검사
            if not self.validate_url(url):
                self._log_thread_activity('complete', url, success=False)
                return {
                    'success': False,
                    'error': 'Invalid URL format',
                    'url': url
                }
        
            # Step 1: 웹에서 콘텐츠 추출
            self._log_thread_activity('progress', url, message="웹 콘텐츠 추출 시작")
            print("📄 웹 콘텐츠 추출 중...")
            extraction_start = time.time()
            
            # 웹 추출 (None 체크로 린터 오류 해결)
            if self.extractor is None:
                self._log_thread_activity('complete', url, success=False)
                return {'success': False, 'error': 'Extractor not initialized', 'url': url}
            extracted_content = self.extractor.extract_data(url)
            
            if not extracted_content.get('success', False):
                self._log_thread_activity('complete', url, success=False)
                return {
                    'success': False,
                    'error': f'Content extraction failed: {extracted_content.get("error", "Unknown error")}',
                    'url': url
                }
            
            extraction_time = time.time() - extraction_start
            self._log_thread_activity('progress', url, message=f"웹 추출 완료 ({extraction_time:.2f}초)")
            print(f"✅ 웹 추출 완료 ({extraction_time:.2f}초)")
            
                        # Step 2: AI 변환
            self._log_thread_activity('progress', url, message="AI 변환 시작")
            print("🤖 AI 변환 중...")
            conversion_start = time.time()
            
            # 완성형 블로그인 경우
            if content_type == 'enhanced_blog':
                self._log_thread_activity('progress', url, message="완성형 블로그 생성 시작")
                if self.blog_generator is None:
                    self._log_thread_activity('complete', url, success=False)
                    return {'success': False, 'error': 'Blog generator not initialized', 'url': url}
                blog_result = self.blog_generator.generate_rich_text_blog_content(extracted_content, wordpress_type)
                
                if blog_result:
                    # 🔧 고유한 파일명 생성 (마이크로초 + 인덱스 포함)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    microsecond = datetime.now().microsecond
                    domain = self.extract_domain_name(url)
                    filename_prefix = f"{domain}_{timestamp}_{microsecond:06d}_{index:03d}_enhanced_blog"
                    
                    # 파일 저장 (extracted_content 전달하여 출처별 최적화)
                    saved_files = self.blog_generator.save_blog_content(
                        blog_result, 
                        filename_prefix, 
                        selected_formats,
                        extracted_content,
                        wordpress_type
                    )
                    
                    conversion_time = time.time() - conversion_start
                    self._log_thread_activity('progress', url, message=f"완성형 블로그 생성 완료 ({conversion_time:.2f}초)")
                    print(f"✅ 완성형 블로그 콘텐츠 생성 완료 (선택된 형식: {selected_formats})")
                    print(f"✅ AI 변환 완료 ({conversion_time:.2f}초)")
                    
                    # 메인 마크다운 파일 경로 또는 첫 번째 파일
                    if saved_files:
                        # md 파일이 있으면 사용, 없으면 첫 번째 파일 사용
                        main_file = saved_files.get('md')
                        if not main_file and saved_files:
                            # saved_files의 첫 번째 값 사용
                            main_file = list(saved_files.values())[0]
                    else:
                        main_file = None
                    
                    result = {
                        'success': True,
                        'url': url,
                        'title': blog_result['meta_info']['title'],
                        'output_file': Path(main_file) if main_file else None,
                        'all_files': saved_files,
                        'timestamp': datetime.now().isoformat(),
                        'content_type': content_type,
                        'selected_formats': selected_formats
                    }
                    self._log_thread_activity('complete', url, success=True)
                    return result
                else:
                    result = {
                        'success': False,
                        'error': f'Blog generation failed: 콘텐츠 생성 중 오류가 발생했습니다.',
                        'url': url
                    }
                    self._log_thread_activity('complete', url, success=False)
                    return result
            else:
                # 일반 콘텐츠 변환
                if content_type == 'threads':
                    # Threads용 짧은 콘텐츠 생성 (490자 미만)
                    self._log_thread_activity('progress', url, message="Threads 콘텐츠 생성 시작")
                    if self.converter is None:
                        self._log_thread_activity('complete', url, success=False)
                        return {'success': False, 'error': 'Converter not initialized', 'url': url}
                    converted_content = self.converter.generate_threads_content({
                        'title': extracted_content.get('title', ''),
                        'description': extracted_content.get('description', ''),
                        'content': extracted_content['content']['text']
                    })
                    
                    if not converted_content or not isinstance(converted_content, str):
                        result = {
                            'success': False,
                            'error': f'Threads content generation failed: Invalid response format',
                            'url': url
                        }
                        self._log_thread_activity('complete', url, success=False)
                        return result
                    
                    # 직접 문자열을 content로 사용
                    converted_response = {
                        'success': True,
                        'content': converted_content,
                        'title': extracted_content.get('title', 'Generated Threads Content')
                    }
                elif content_type == 'blog':
                    # 블로그 콘텐츠 생성
                    self._log_thread_activity('progress', url, message="블로그 콘텐츠 생성 시작")
                    if self.converter is None:
                        self._log_thread_activity('complete', url, success=False)
                        return {'success': False, 'error': 'Converter not initialized', 'url': url}
                    converted_response = self.converter.convert_from_data_blog(extracted_content)
                    if not isinstance(converted_response, str):
                        converted_response = {
                            'success': True,
                            'content': converted_response,
                            'title': extracted_content.get('title', 'Generated Blog Content')
                        }
                    else:
                        converted_response = {
                            'success': True,
                            'content': converted_response,
                            'title': extracted_content.get('title', 'Generated Blog Content')
                        }
                elif content_type == 'x' or content_type == 'twitter':
                    # X(Twitter)용 콘텐츠 생성
                    self._log_thread_activity('progress', url, message="X 콘텐츠 생성 시작")
                    if self.converter is None:
                        self._log_thread_activity('complete', url, success=False)
                        return {'success': False, 'error': 'Converter not initialized', 'url': url}
                    converted_response = self.converter.generate_x_content({
                        'title': extracted_content.get('title', ''),
                        'body': extracted_content['content']['text']
                    })
                    if not isinstance(converted_response, str):
                        converted_response = {
                            'success': True,
                            'content': converted_response,
                            'title': extracted_content.get('title', 'Generated X Content')
                        }
                    else:
                        converted_response = {
                            'success': True,
                            'content': converted_response,
                            'title': extracted_content.get('title', 'Generated X Content')
                        }
                else:
                    # 표준 마크다운 콘텐츠 생성
                    self._log_thread_activity('progress', url, message="표준 마크다운 생성 시작")
                    if self.converter is None:
                        self._log_thread_activity('complete', url, success=False)
                        return {'success': False, 'error': 'Converter not initialized', 'url': url}
                    converted_response = self.converter.convert_from_data(extracted_content)
                    if not isinstance(converted_response, str):
                        converted_response = {
                            'success': True,
                            'content': converted_response,
                            'title': extracted_content.get('title', 'Generated Content')
                        }
                    else:
                        converted_response = {
                            'success': True,
                            'content': converted_response,
                            'title': extracted_content.get('title', 'Generated Content')
                        }
                
                # 응답 형식 통일
                if isinstance(converted_response, str):
                    # 문자열인 경우 성공으로 간주
                    converted_content = {
                        'success': True,
                        'content': converted_response,
                        'title': extracted_content.get('title', 'Generated Content')
                    }
                else:
                    # 딕셔너리인 경우 그대로 사용
                    converted_content = converted_response
                
                if converted_content.get('success', False):
                    # 🔧 고유한 파일명 생성 (마이크로초 + 인덱스 포함)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    microsecond = datetime.now().microsecond
                    domain = self.extract_domain_name(url)
                    filename = f"{domain}_{timestamp}_{microsecond:06d}_{index:03d}_{content_type}.md"
                    
                    # 파일 저장
                    output_file = self.generated_dir / filename
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(converted_content['content'])
                    
                    conversion_time = time.time() - conversion_start
                    self._log_thread_activity('progress', url, message=f"AI 변환 완료 ({conversion_time:.2f}초)")
                    print(f"✅ AI 변환 완료 ({conversion_time:.2f}초)")
                    
                    total_time = time.time() - extraction_start
                    print(f"💾 파일 저장 완료: {output_file} (총 {total_time:.2f}초)")
                    
                    result = {
                        'success': True,
                        'url': url,
                        'title': converted_content.get('title', 'Generated Content'),
                        'output_file': output_file,
                        'timestamp': datetime.now().isoformat(),
                        'content_type': content_type
                    }
                    self._log_thread_activity('complete', url, success=True)
                    return result
                else:
                    result = {
                        'success': False,
                        'error': f'Content conversion failed: {converted_content.get("error", "Unknown error")}',
                        'url': url
                    }
                    self._log_thread_activity('complete', url, success=False)
                    return result
                    
        except Exception as e:
            error_msg = f"Unexpected error during content generation: {str(e)}"
            self._log_thread_activity('complete', url, success=False)
            return {
                'success': False,
                'error': error_msg,
                'url': url
            }
    
    def cleanup(self):
        """리소스 정리"""
        if self.extractor is not None and hasattr(self.extractor, 'cleanup'):
            self.extractor.cleanup()
        if self.converter is not None and hasattr(self.converter, 'cleanup'):
            self.converter.cleanup()
        print("🧹 리소스 정리 완료")

def print_usage():
    """사용법 출력"""
    print("""
NONGBUXX Content Generator - 원스탑 뉴스 콘텐츠 생성기

사용법:
  python nongbuxx_generator.py <URL> [options]
  python nongbuxx_generator.py --batch <URL1> <URL2> ... [options]

옵션:
  --api <provider>     API 제공자 (anthropic/openai, 기본값: anthropic)
  --filename <name>    사용자 지정 파일명
  --no-temp           중간 파일 저장하지 않음
  --batch             여러 URL 일괄 처리
  --help              도움말 표시

예시:
  python nongbuxx_generator.py "https://finance.yahoo.com/news/example"
  python nongbuxx_generator.py "https://example.com/news" --api openai --filename "my_article"
  python nongbuxx_generator.py --batch "https://url1.com" "https://url2.com" --api anthropic

필수 환경변수:
  ANTHROPIC_API_KEY   (anthropic 사용 시)
  OPENAI_API_KEY      (openai 사용 시)
""")

def main():
    if len(sys.argv) < 2 or '--help' in sys.argv:
        print_usage()
        sys.exit(0)
    
    # 명령행 인수 파싱
    args = sys.argv[1:]
    api_provider = 'anthropic'
    custom_filename = None
    save_intermediate = True
    batch_mode = False
    urls = []
    
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg == '--api':
            if i + 1 < len(args):
                api_provider = args[i + 1]
                i += 2
            else:
                print("❌ Error: --api requires a value")
                sys.exit(1)
        elif arg == '--filename':
            if i + 1 < len(args):
                custom_filename = args[i + 1]
                i += 2
            else:
                print("❌ Error: --filename requires a value")
                sys.exit(1)
        elif arg == '--no-temp':
            save_intermediate = False
            i += 1
        elif arg == '--batch':
            batch_mode = True
            i += 1
        elif arg.startswith('http'):
            urls.append(arg)
            i += 1
        else:
            print(f"❌ Error: Unknown argument '{arg}'")
            sys.exit(1)
    
    # URL 확인
    if not urls:
        print("❌ Error: No URLs provided")
        print_usage()
        sys.exit(1)
    
    # API 제공자 검증
    if api_provider not in ['anthropic', 'openai']:
        print("❌ Error: API provider must be 'anthropic' or 'openai'")
        sys.exit(1)
    
    # API 키 확인
    if api_provider == 'anthropic' and not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ Error: ANTHROPIC_API_KEY environment variable is required")
        sys.exit(1)
    elif api_provider == 'openai' and not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        sys.exit(1)
    
    # 생성기 초기화
    try:
        generator = NongbuxxGenerator(
            api_provider=api_provider,
            save_intermediate=save_intermediate
        )
        
        # 콘텐츠 생성
        if batch_mode or len(urls) > 1:
            results = generator.batch_generate(urls)
            
            # 성공한 파일들 경로 출력
            success_files = [r['output_file'] for r in results if r['success']]
            if success_files:
                print(f"\n🎉 생성된 파일들:")
                for file_path in success_files:
                    print(f"   📄 {file_path}")
        else:
            result = generator.generate_content(urls[0], custom_filename)
            
            if result['success']:
                print(f"\n🎉 콘텐츠 생성 완료!")
                print(f"   📄 생성된 파일: {result['output_file']}")
                if result['extracted_file']:
                    print(f"   📄 추출된 파일: {result['extracted_file']}")
            else:
                print(f"\n❌ 콘텐츠 생성 실패: {result['error']}")
                sys.exit(1)
        
        # 정리
        generator.cleanup()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 