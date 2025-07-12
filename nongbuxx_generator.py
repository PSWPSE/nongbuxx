#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# Import our existing modules
from web_extractor import WebExtractor
from converter import NewsConverter

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
        try:
            extracted_data = self.extractor.extract_data(url)
            
            if not extracted_data.get('success'):
                error_msg = extracted_data.get('error', '알 수 없는 오류')
                # 이미 사용자 친화적인 메시지인 경우 그대로 반환
                if any(keyword in error_msg for keyword in ['차단', '찾을 수 없습니다', '시간 초과', '네트워크', '서버']):
                    return {
                        'success': False,
                        'error': error_msg,
                        'url': url
                    }
                else:
                    return {
                        'success': False,
                        'error': f"콘텐츠 추출 실패: {error_msg}",
                        'url': url
                    }
            
            print("✅ 웹 콘텐츠 추출 완료")
            
        except Exception as e:
            return {
                'success': False,
                'error': f"추출 중 오류 발생: {str(e)}",
                'url': url
            }
        
        # Step 2: 콘텐츠 타입에 따라 다른 변환 방식 사용
        if content_type == 'blog':
            print(f"🔄 블로그 콘텐츠 변환 중 (API: {self.api_provider})...")
            try:
                # 블로그 콘텐츠 변환 메서드 사용
                markdown_content = self.converter.convert_from_data_blog(extracted_data)
                conversion_type = "blog"
            except Exception as e:
                return {
                    'success': False,
                    'error': f"블로그 변환 중 오류 발생: {str(e)}",
                    'url': url
                }
        else:
            print(f"🔄 표준 마크다운 변환 중 (API: {self.api_provider})...")
            try:
                # 기존 표준 변환 메서드 사용
                markdown_content = self.converter.convert_from_data(extracted_data)
                conversion_type = "standard"
            except Exception as e:
                return {
                    'success': False,
                    'error': f"표준 변환 중 오류 발생: {str(e)}",
                    'url': url
                }
        
        # Step 3: 파일 저장
        try:
            # 파일명 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            domain = self.extract_domain_name(url)
            
            # 콘텐츠 타입에 따라 파일명 구분
            type_prefix = "blog_" if content_type == 'blog' else ""
            
            if custom_filename:
                output_filename = f"{type_prefix}{custom_filename}_{timestamp}.md"
            else:
                output_filename = f"{type_prefix}{domain}_{timestamp}.md"
            
            output_path = self.generated_dir / output_filename
            
            # 최종 마크다운 파일 저장
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"✅ {conversion_type} 마크다운 생성 완료: {output_path}")
            
            # 중간 파일 저장 옵션이 있는 경우에만 원본 데이터 저장
            extracted_file_path = None
            if self.save_intermediate:
                temp_filename = f"{type_prefix}{domain}_{timestamp}.txt"
                temp_txt_path = self.extracted_dir / temp_filename
                
                with open(temp_txt_path, 'w', encoding='utf-8') as f:
                    f.write(f"제목: {extracted_data['title']}\n")
                    f.write("="*80 + "\n\n")
                    
                    if extracted_data['metadata']:
                        f.write("메타 정보:\n")
                        for key, value in extracted_data['metadata'].items():
                            f.write(f"{key}: {value}\n")
                        f.write("-"*80 + "\n\n")
                    
                    f.write("본문:\n")
                    f.write(extracted_data['content']['text'])
                
                extracted_file_path = temp_txt_path
                print(f"📝 원본 데이터 저장: {temp_txt_path}")
            
            return {
                'success': True,
                'url': url,
                'output_file': output_path,
                'extracted_file': extracted_file_path,
                'title': extracted_data['title'],
                'timestamp': timestamp,
                'content_type': content_type
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"파일 저장 중 오류 발생: {str(e)}",
                'url': url
            }
    
    def batch_generate(self, urls, custom_filenames=None, content_type='standard'):
        """
        여러 URL을 일괄 처리
        
        Args:
            urls: URL 리스트
            custom_filenames: 사용자 지정 파일명 리스트 (선택사항)
            content_type: 콘텐츠 타입 ('standard' 또는 'blog')
            
        Returns:
            list: 각 URL의 처리 결과 리스트
        """
        results = []
        
        print(f"\n📋 일괄 처리 시작 ({len(urls)}개 URL, 타입: {content_type})")
        
        for i, url in enumerate(urls):
            filename = custom_filenames[i] if custom_filenames and i < len(custom_filenames) else None
            
            print(f"\n--- {i+1}/{len(urls)} ---")
            result = self.generate_content(url, filename, content_type)
            results.append(result)
            
            if result['success']:
                print(f"✅ 성공: {result['output_file']}")
            else:
                print(f"❌ 실패: {result['error']}")
        
        # 결과 요약
        success_count = sum(1 for r in results if r['success'])
        print(f"\n📊 일괄 처리 완료: {success_count}/{len(urls)} 성공")
        
        return results
    
    def cleanup(self):
        """리소스 정리"""
        if hasattr(self.extractor, 'close'):
            self.extractor.close()

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