#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

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
        
        # 출력 디렉토리 설정
        self.generated_dir = Path('generated_content')
        self.extracted_dir = Path('extracted_articles')
        
        # 디렉토리 생성
        self.generated_dir.mkdir(exist_ok=True)
        if save_intermediate:
            self.extracted_dir.mkdir(exist_ok=True)
        
        # 모듈 초기화
        self.extractor = WebExtractor(use_selenium=False, save_to_file=save_intermediate)
        self.converter = NewsConverter(api_provider=api_provider, api_key=api_key)
        self.blog_generator = BlogContentGenerator(api_provider=api_provider, api_key=api_key)
        
        key_status = "사용자 제공" if api_key else "환경변수"
        print(f"NONGBUXX Generator 초기화 완료 (API: {api_provider}, 키: {key_status})")
    
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
    
    def generate_content(self, url, custom_filename=None, content_type='standard'):
        """
        URL에서 콘텐츠를 추출하고 마크다운으로 변환 (최적화된 버전)
        
        Args:
            url: 추출할 뉴스 기사 URL
            custom_filename: 사용자 지정 파일명 (선택사항)
            content_type: 콘텐츠 타입 ('standard' 또는 'blog')
            
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
        
        # 웹 추출
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
            # 새로운 완성형 블로그 콘텐츠 생성
            rich_content = self.blog_generator.generate_rich_text_blog_content(extracted_content)
            converted_content = rich_content['markdown']  # 기본적으로 마크다운 반환
            
            # 추가 형식들도 파일로 저장
            domain = self.extract_domain_name(url)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_prefix = f"{domain}_{timestamp}_enhanced_blog"
            
            self.blog_generator.save_blog_content(rich_content, filename_prefix)
            print(f"✅ 완성형 블로그 콘텐츠 생성 완료 (HTML, 플랫폼별 최적화 포함)")
            
        elif content_type == 'blog':
            converted_content = self.converter.convert_from_data_blog(extracted_content)
        else:
            converted_content = self.converter.convert_from_data(extracted_content)
        
        if not converted_content or not isinstance(converted_content, str):
            return {
                'success': False,
                'error': f'AI conversion failed: Invalid response format',
                'url': url
            }
        
        conversion_time = time.time() - conversion_start
        print(f"✅ AI 변환 완료 ({conversion_time:.2f}초)")
        
        # Step 3: 파일명 생성 및 저장
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
    
    def batch_generate(self, urls, content_type='standard', max_workers=3):
        """
        다중 URL에서 콘텐츠를 병렬로 생성 (성능 최적화)
        
        Args:
            urls: URL 목록
            content_type: 콘텐츠 타입 ('standard' 또는 'blog')
            max_workers: 최대 병렬 처리 수 (기본값: 3)
            
        Returns:
            list: 각 URL의 결과 목록
        """
        if not urls:
            return []
        
        print(f"\n🚀 병렬 배치 생성 시작: {len(urls)}개 URL (타입: {content_type})")
        print(f"⚡ 최대 병렬 처리 수: {max_workers}")
        
        start_time = time.time()
        results = []
        
        # 병렬 처리
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 각 URL에 대한 future 생성
            future_to_url = {
                executor.submit(self.generate_content, url, None, content_type): url 
                for url in urls
            }
            
            # 결과 수집
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result['success']:
                        print(f"✅ 성공: {url}")
                    else:
                        print(f"❌ 실패: {url} - {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"❌ 예외 발생: {url} - {str(e)}")
                    results.append({
                        'success': False,
                        'error': str(e),
                        'url': url
                    })
        
        # 결과 통계
        success_count = sum(1 for r in results if r['success'])
        total_time = time.time() - start_time
        
        print(f"\n📊 배치 생성 완료:")
        print(f"   • 성공: {success_count}/{len(urls)}")
        print(f"   • 총 소요 시간: {total_time:.2f}초")
        print(f"   • 평균 시간: {total_time/len(urls):.2f}초/URL")
        
        return results
    
    def cleanup(self):
        """리소스 정리"""
        if hasattr(self.extractor, 'cleanup'):
            self.extractor.cleanup()
        if hasattr(self.converter, 'cleanup'):
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