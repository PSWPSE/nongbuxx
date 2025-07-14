#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from pathlib import Path
import json
import logging

# Import our existing modules
from converter import NewsConverter

class BlogContentGenerator:
    def __init__(self, api_provider='anthropic', api_key=None):
        """
        완성형 블로그 콘텐츠 생성기
        
        Args:
            api_provider: 'anthropic' 또는 'openai'
            api_key: 사용자 제공 API 키
        """
        self.api_provider = api_provider
        self.api_key = api_key
        self.converter = NewsConverter(api_provider=api_provider, api_key=api_key)
        
        # 출력 디렉토리 설정
        self.output_dir = Path('generated_content')
        self.output_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def generate_complete_blog_content(self, extracted_data):
        """
        완성형 블로그 콘텐츠 생성 (메타 정보 없이 순수 콘텐츠만)
        
        Args:
            extracted_data: 웹에서 추출된 데이터
            
        Returns:
            str: 완성형 블로그 콘텐츠
        """
        
        # 완성형 콘텐츠를 위한 개선된 프롬프트
        prompt = f"""당신은 전문 블로그 작가입니다. 다음 뉴스 기사를 바탕으로 완성형 블로그 콘텐츠를 작성해주세요.

**중요: 작성 지침이나 메타 정보는 포함하지 마세요. 순수한 블로그 콘텐츠만 작성하세요.**

**콘텐츠 요구사항:**
- 5000자 이상의 완성형 블로그 포스트
- 친근하고 설득력있는 말투 ("~에요", "~해요" 사용)
- 읽기 쉬운 문단 구성
- 추가 배경 정보와 분석 포함
- SEO 최적화 고려
- 독자의 관심과 공감을 유발하는 내용

**구성 순서:**
1. 매력적인 제목 (한 줄)
2. 한 줄 요약
3. 서론 (독자 관심 유발)
4. 본문 (논리적 구성)
5. 추가 분석 및 전망
6. 결론

**원문 정보:**
제목: {extracted_data['title']}
설명: {extracted_data.get('description', '')}
본문: {extracted_data['content']['text']}

위 내용을 바탕으로 독자가 끝까지 흥미롭게 읽을 수 있는 완성형 블로그 콘텐츠를 작성해주세요."""

        response = self.converter.call_api(prompt, max_tokens=4000)
        return self.converter.clean_response(response)
    
    def generate_html_blog_content(self, extracted_data):
        """
        HTML 형식의 블로그 콘텐츠 생성 (포맷팅 유지)
        
        Args:
            extracted_data: 웹에서 추출된 데이터
            
        Returns:
            str: HTML 형식의 블로그 콘텐츠
        """
        
        # HTML 형식 콘텐츠를 위한 프롬프트
        prompt = f"""당신은 전문 블로그 작가입니다. 다음 뉴스 기사를 바탕으로 HTML 형식의 완성형 블로그 콘텐츠를 작성해주세요.

**중요: 작성 지침이나 메타 정보는 포함하지 마세요. 순수한 HTML 블로그 콘텐츠만 작성하세요.**

**HTML 스타일 가이드:**
- 제목: <h1> 태그 사용
- 소제목: <h2>, <h3> 태그 사용
- 본문: <p> 태그로 문단 구분
- 강조: <strong> 또는 <em> 태그 사용
- 목록: <ul>, <ol>, <li> 태그 사용
- 인용: <blockquote> 태그 사용
- 중요 정보: <div class="highlight"> 또는 <aside> 태그 사용

**CSS 스타일 포함:**
- 기본적인 인라인 스타일 또는 내부 CSS 스타일 시트 포함
- 읽기 쉬운 폰트 크기 및 줄 간격
- 색상 및 여백 조정
- 모바일 친화적 스타일

**콘텐츠 요구사항:**
- 5000자 이상의 완성형 블로그 포스트
- 친근하고 설득력있는 말투 ("~에요", "~해요" 사용)
- 읽기 쉬운 문단 구성
- 추가 배경 정보와 분석 포함
- SEO 최적화 고려
- 독자의 관심과 공감을 유발하는 내용

**원문 정보:**
제목: {extracted_data['title']}
설명: {extracted_data.get('description', '')}
본문: {extracted_data['content']['text']}

완성형 HTML 블로그 콘텐츠를 작성해주세요. 블로그 에디터에 복사-붙여넣기 했을 때 포맷팅이 그대로 유지되도록 작성하세요."""

        response = self.converter.call_api(prompt, max_tokens=4000)
        return self.converter.clean_response(response)
    
    def generate_rich_text_blog_content(self, extracted_data):
        """
        Rich Text 형식의 블로그 콘텐츠 생성 (다양한 블로그 플랫폼 지원)
        
        Args:
            extracted_data: 웹에서 추출된 데이터
            
        Returns:
            dict: 다양한 형식의 블로그 콘텐츠
        """
        
        # 기본 완성형 콘텐츠 생성
        markdown_content = self.generate_complete_blog_content(extracted_data)
        
        # HTML 형식 콘텐츠 생성
        html_content = self.generate_html_blog_content(extracted_data)
        
        # 플랫폼별 최적화된 콘텐츠 생성
        platform_optimized = self.generate_platform_optimized_content(extracted_data)
        
        return {
            'markdown': markdown_content,
            'html': html_content,
            'platform_optimized': platform_optimized,
            'meta_info': {
                'title': extracted_data['title'],
                'description': extracted_data.get('description', ''),
                'created_at': datetime.now().isoformat(),
                'word_count': len(markdown_content.split())
            }
        }
    
    def generate_platform_optimized_content(self, extracted_data):
        """
        다양한 블로그 플랫폼에 최적화된 콘텐츠 생성
        
        Args:
            extracted_data: 웹에서 추출된 데이터
            
        Returns:
            dict: 플랫폼별 최적화된 콘텐츠
        """
        
        # 워드프레스용 콘텐츠
        wordpress_prompt = f"""워드프레스 블로그에 최적화된 HTML 콘텐츠를 작성해주세요.

**워드프레스 스타일 가이드:**
- Gutenberg 블록 에디터 호환
- 기본 워드프레스 스타일 활용
- 반응형 디자인 고려
- SEO 최적화 (메타 태그 제안)

**원문 정보:**
제목: {extracted_data['title']}
설명: {extracted_data.get('description', '')}
본문: {extracted_data['content']['text']}

워드프레스에 바로 붙여넣을 수 있는 HTML 콘텐츠를 작성해주세요."""

        wordpress_content = self.converter.call_api(wordpress_prompt, max_tokens=4000)
        
        # 티스토리용 콘텐츠
        tistory_prompt = f"""티스토리 블로그에 최적화된 HTML 콘텐츠를 작성해주세요.

**티스토리 스타일 가이드:**
- 티스토리 에디터 호환
- 한국어 블로그 독자 친화적
- 모바일 최적화
- 카카오 검색 최적화

**원문 정보:**
제목: {extracted_data['title']}
설명: {extracted_data.get('description', '')}
본문: {extracted_data['content']['text']}

티스토리에 바로 붙여넣을 수 있는 HTML 콘텐츠를 작성해주세요."""

        tistory_content = self.converter.call_api(tistory_prompt, max_tokens=4000)
        
        # 네이버 블로그용 콘텐츠
        naver_prompt = f"""네이버 블로그에 최적화된 콘텐츠를 작성해주세요.

**네이버 블로그 스타일 가이드:**
- 네이버 블로그 에디터 호환
- 네이버 검색 최적화
- 한국어 독자 친화적
- 스마트 에디터 활용

**원문 정보:**
제목: {extracted_data['title']}
설명: {extracted_data.get('description', '')}
본문: {extracted_data['content']['text']}

네이버 블로그에 바로 붙여넣을 수 있는 콘텐츠를 작성해주세요."""

        naver_content = self.converter.call_api(naver_prompt, max_tokens=4000)
        
        return {
            'wordpress': self.converter.clean_response(wordpress_content),
            'tistory': self.converter.clean_response(tistory_content),
            'naver': self.converter.clean_response(naver_content)
        }
    
    def save_blog_content(self, content_data, filename_prefix=None):
        """
        생성된 블로그 콘텐츠를 파일로 저장
        
        Args:
            content_data: 생성된 콘텐츠 데이터
            filename_prefix: 파일명 접두사
            
        Returns:
            dict: 저장된 파일 정보
        """
        
        if filename_prefix is None:
            filename_prefix = f"blog_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        saved_files = {}
        
        # 마크다운 파일 저장
        markdown_file = self.output_dir / f"{filename_prefix}.md"
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(content_data['markdown'])
        saved_files['markdown'] = str(markdown_file)
        
        # HTML 파일 저장
        html_file = self.output_dir / f"{filename_prefix}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content_data['html'])
        saved_files['html'] = str(html_file)
        
        # 플랫폼별 파일 저장
        for platform, content in content_data['platform_optimized'].items():
            platform_file = self.output_dir / f"{filename_prefix}_{platform}.html"
            with open(platform_file, 'w', encoding='utf-8') as f:
                f.write(content)
            saved_files[platform] = str(platform_file)
        
        # 메타 정보 저장
        meta_file = self.output_dir / f"{filename_prefix}_meta.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(content_data['meta_info'], f, ensure_ascii=False, indent=2)
        saved_files['meta'] = str(meta_file)
        
        return saved_files

def main():
    """테스트 및 독립 실행을 위한 메인 함수"""
    
    # 샘플 데이터로 테스트
    sample_data = {
        'title': '테스트 뉴스 제목',
        'description': '테스트 뉴스 설명',
        'content': {
            'text': '테스트 뉴스 본문 내용입니다.'
        }
    }
    
    # 블로그 콘텐츠 생성기 초기화
    generator = BlogContentGenerator()
    
    # 완성형 블로그 콘텐츠 생성
    result = generator.generate_rich_text_blog_content(sample_data)
    
    # 결과 저장
    saved_files = generator.save_blog_content(result)
    
    print("✅ 완성형 블로그 콘텐츠 생성 완료!")
    print(f"📁 저장된 파일: {saved_files}")

if __name__ == "__main__":
    main() 