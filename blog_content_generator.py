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
    
    def detect_news_source(self, extracted_data):
        """
        뉴스 출처를 감지하여 적절한 파일 형식을 결정
        
        Args:
            extracted_data: 웹에서 추출된 데이터
            
        Returns:
            dict: 출처 정보와 권장 형식
        """
        url = extracted_data.get('url', '')
        source = extracted_data.get('source', '')
        title = extracted_data.get('title', '')
        
        # URL과 소스 정보를 소문자로 변환하여 비교
        url_lower = url.lower()
        source_lower = source.lower()
        
        # 출처별 분류
        source_info = {
            'type': 'unknown',
            'name': 'Unknown',
            'recommended_formats': ['md', 'wordpress']  # 기본값
        }
        
        # 네이버 뉴스
        if ('news.naver.com' in url_lower or 
            'naver' in source_lower or
            'n.news.naver.com' in url_lower):
            source_info.update({
                'type': 'naver_news',
                'name': 'Naver News',
                'recommended_formats': ['md', 'naver']
            })
        
        # Yahoo Finance
        elif ('finance.yahoo.com' in url_lower or 
              'yahoo finance' in source_lower):
            source_info.update({
                'type': 'yahoo_finance',
                'name': 'Yahoo Finance',
                'recommended_formats': ['md', 'wordpress']
            })
        
        # 한국 주요 언론사
        elif any(domain in url_lower for domain in [
            'chosun.com', 'joongang.co.kr', 'donga.com', 'hani.co.kr',
            'khan.co.kr', 'mk.co.kr', 'edaily.co.kr', 'etnews.com',
            'mt.co.kr', 'sedaily.com', 'hankyung.com', 'newsis.com'
        ]):
            source_info.update({
                'type': 'korean_media',
                'name': 'Korean Media',
                'recommended_formats': ['md', 'naver', 'tistory']
            })
        
        # Bloomberg, Reuters 등 해외 금융/경제 뉴스
        elif any(domain in url_lower for domain in [
            'bloomberg.com', 'reuters.com', 'wsj.com', 'ft.com',
            'cnbc.com', 'marketwatch.com', 'investing.com'
        ]):
            source_info.update({
                'type': 'international_finance',
                'name': 'International Finance',
                'recommended_formats': ['md', 'wordpress']
            })
        
        # 기타 해외 뉴스
        elif any(domain in url_lower for domain in [
            'cnn.com', 'bbc.com', 'theguardian.com', 'nytimes.com',
            'washingtonpost.com', 'techcrunch.com', 'engadget.com'
        ]):
            source_info.update({
                'type': 'international_general',
                'name': 'International General',
                'recommended_formats': ['md', 'wordpress']
            })
        
        # 암호화폐/블록체인 전문 매체
        elif any(domain in url_lower for domain in [
            'coindesk.com', 'cointelegraph.com', 'decrypt.co',
            'cryptoslate.com', 'themerkle.com'
        ]):
            source_info.update({
                'type': 'crypto_media',
                'name': 'Crypto Media',
                'recommended_formats': ['md', 'wordpress']
            })
        
        # 한국어 제목이 있는 경우 한국 매체로 추정
        elif any(ord(char) >= 0xAC00 and ord(char) <= 0xD7AF for char in title):
            source_info.update({
                'type': 'korean_content',
                'name': 'Korean Content',
                'recommended_formats': ['md', 'naver', 'tistory']
            })
        
        self.logger.info(f"출처 감지 결과: {source_info['name']} → 권장 형식: {source_info['recommended_formats']}")
        return source_info

    def generate_complete_blog_content(self, extracted_data):
        """
        완성형 블로그 콘텐츠 생성 (메타 정보 없이 순수 콘텐츠만)
        
        Args:
            extracted_data: 웹에서 추출된 데이터
            
        Returns:
            str: 완성형 블로그 콘텐츠
        """
        
        # 네이버 뉴스인지 확인
        is_naver_news = 'news.naver.com' in extracted_data.get('url', '') or 'naver' in extracted_data.get('source', '').lower()
        
        if is_naver_news:
            # 네이버 뉴스는 원본 한국어 제목 그대로 사용
            prompt = f"""당신은 전문 블로그 작가입니다. 다음 네이버 뉴스 기사를 바탕으로 완성형 블로그 콘텐츠를 작성해주세요.

**🚨 필수 지시사항 - 절대 지켜야 함:**
- 네이버 뉴스는 이미 한국어이므로 제목 번역 금지

**중요: 작성 지침이나 메타 정보는 포함하지 마세요. 순수한 블로그 콘텐츠만 작성하세요.**

**제목 작성 가이드라인:**
- 원본이 한국어인 경우 한국어 제목을 그대로 사용
- 독자들의 관심을 끌만한 매력적이고 깔끔하고 임팩트 있는 제목
- 단순한 사실 전달보다는 독자의 호기심을 자극하는 제목
- 클릭하고 싶게 만드는 강력한 어필 포인트 포함
- 너무 길지 않으면서도 핵심 메시지가 명확한 제목

**콘텐츠 구조 가이드라인:**
- 5000자 이상의 완성형 블로그 포스트
- 친근하고 설득력있는 말투 ("~에요", "~해요" 사용)
- 단락 구분 없이 계속 내용을 전개하는 것이 아닌 명확한 단락형으로 제공
- 각 단락마다 명확한 소제목 (## 또는 ###) 설정
- 내용 전달과 읽는 피로도 감소, 내용 전개의 자연스러움 고려
- 지루하지 않은 콘텐츠 소비를 목표로 구성

**섹션 구성 원칙:**
- 정형화된 고정 구조(핵심 요약 → 주요 내용 → 시장 영향 → 투자 시사점)를 사용하지 말 것
- 원문의 내용과 맥락에 따라 논리적이고 자연스러운 흐름으로 섹션 구성
- 독자가 쉽고 지루하지 않게 내용을 파악할 수 있도록 구성
- 원문에서 강조하는 핵심 포인트들을 중심으로 섹션 분할
- 각 섹션은 원문의 논리적 흐름을 따라 자연스럽게 연결

**단락 구성 원칙:**
- 전체 내용을 단락 제목만 봐도 대략 이해할 수 있는 정도로 핵심적인 포인트들로 구성
- 단락 내용은 단락 제목에 걸맞게 쉽게 읽히되 내용은 잘 전달되는 내용전달력이 좋은 글로 구성
- 각 단락은 2-4개 문단으로 구성하여 적절한 길이 유지
- 단락 간 자연스러운 연결과 논리적 흐름 유지

**입력 데이터:**
제목: {extracted_data.get('title', '')}
내용: {extracted_data.get('content', '')}
요약: {extracted_data.get('description', '')}

**출력 형식:**
완성형 블로그 포스트 (제목부터 마무리까지 모든 내용 포함)"""
        else:
            # 해외 뉴스는 기존 번역 로직 적용
            prompt = f"""당신은 전문 블로그 작가입니다. 다음 뉴스 기사를 바탕으로 완성형 블로그 콘텐츠를 작성해주세요.

**🚨 필수 지시사항 - 절대 지켜야 함:**
- 제목은 100% 한국어로만 작성
- 영어 제목이 입력되어도 반드시 한국어로 번역
- 제목만 영어로 나오는 경우 절대 금지

**⚠️ 특별 주의사항:**
- 입력된 제목이 영어라면 100% 한국어로 번역하여 사용
- 원문이 영어여도 한국 독자를 위해 한국어 제목 필수

**💡 매력적인 제목 생성 가이드라인 (핵심):**
- 단순 번역이 아닌 독자의 관심을 끄는 매력적인 제목 작성
- 호기심을 자극하고 클릭하고 싶게 만드는 임팩트 있는 제목
- "왜?", "어떻게?", "무엇을?", "진짜?" 등 궁금증을 유발하는 요소 포함
- 핵심 키워드와 감정적 어필을 결합한 제목
- 숫자나 구체적 데이터 활용으로 신뢰성 증대
- 독자에게 직접적 관심사나 충격을 주는 표현 사용
- 예시 변환:
  * "Why the stock market has shrugged off Trump's latest tariff threats" 
    → "트럼프 관세 폭탄에도 주식시장이 무덤덤한 놀라운 이유"
  * "Apple announces new AI features"
    → "애플이 공개한 AI 신기능, 삼성에게는 악몽일 수밖에 없는 이유"
  * "Tesla stock rises 5%"
    → "테슬라 주가 5% 급등, 머스크가 다시 한 번 해낸 비밀 전략"

**중요: 작성 지침이나 메타 정보는 포함하지 마세요. 순수한 블로그 콘텐츠만 작성하세요.**

**제목 작성 가이드라인:**
- 독자들의 관심을 끌만한 매력적이고 깔끔하고 임팩트 있는 **한국어 제목**
- 단순한 사실 전달보다는 독자의 호기심을 자극하는 제목
- 클릭하고 싶게 만드는 강력한 어필 포인트 포함
- 너무 길지 않으면서도 핵심 메시지가 명확한 제목

**주식 관련 표기 규칙:**
- 한국 기업: 종목명 $한국코드 (예: 삼성전자 $005930.KS, SK하이닉스 $000660.KS)
- 해외 기업: 종목명 $미국심볼 (예: 테슬라 $TSLA, 애플 $AAPL)
- 거래소 접미사는 한국 기업(.KS)만 허용, 기타 거래소 접미사(.NS, .BO, .L, .TO 등) 금지
- 괄호 사용 금지: 삼성전자 $005930.KS (올바름), 삼성전자($005930.KS) (잘못됨)

**콘텐츠 구조 가이드라인:**
1. **매력적인 도입부**: 독자의 관심을 즉시 사로잡는 훅
2. **핵심 내용 전개**: 논리적이고 구조화된 정보 제공, 회사명 $SYMBOL 형식 포함
3. **시장 영향 분석**: 시장에 미치는 영향과 파급효과 분석
4. **투자 시사점**: 투자 관련 인사이트 및 분석
5. **독자 참여 요소**: 질문, 인사이트, 개인적 견해 포함
6. **강력한 마무리**: 독자가 행동하고 싶게 만드는 결론

**작성 스타일:**
- 친근하면서도 전문적인 톤
- 독자와 대화하는 듯한 자연스러운 어조
- 복잡한 내용도 쉽게 이해할 수 있게 설명
- 적절한 예시와 비유 활용

**입력 데이터:**
제목: {extracted_data['title']}
내용: {extracted_data.get('content', '')}
요약: {extracted_data.get('description', '')}

**출력 형식:**
완성형 블로그 포스트 (제목부터 마무리까지 모든 내용 포함)"""
        
        try:
            response = self.converter.call_api(prompt, max_tokens=2000)
            return self.converter.clean_response(response)
        except Exception as e:
            self.logger.error(f"완성형 블로그 콘텐츠 생성 실패: {e}")
            return f"오류: 블로그 콘텐츠를 생성할 수 없습니다. ({str(e)})"
    
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

**🚨 필수 지시사항 - 절대 지켜야 함:**
- 제목은 100% 한국어로만 작성
- 영어 제목이 입력되어도 반드시 한국어로 번역
- 네이버, 조선일보 등 한국 뉴스는 이미 한국어이므로 한국어 제목 유지
- 제목만 영어로 나오는 경우 절대 금지

**💡 매력적인 제목 생성 가이드라인 (핵심):**
- 단순 번역이 아닌 독자의 관심을 끄는 매력적인 제목 작성
- 호기심을 자극하고 클릭하고 싶게 만드는 임팩트 있는 제목
- "왜?", "어떻게?", "무엇을?", "진짜?" 등 궁금증을 유발하는 요소 포함
- 핵심 키워드와 감정적 어필을 결합한 제목
- 숫자나 구체적 데이터 활용으로 신뢰성 증대
- 독자에게 직접적 관심사나 충격을 주는 표현 사용
- 예시 변환:
  * "Why the stock market has shrugged off Trump's latest tariff threats" 
    → "트럼프 관세 폭탄에도 주식시장이 무덤덤한 놀라운 이유"
  * "Apple announces new AI features"
    → "애플이 공개한 AI 신기능, 삼성에게는 악몽일 수밖에 없는 이유"

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

**🔥 다시 한번 강조: 제목은 무조건 매력적인 한국어로만 작성하세요!**

**원문 정보:**
제목: {extracted_data['title']}
설명: {extracted_data.get('description', '')}
본문: {extracted_data['content']['text']}

**마무리 요구사항:**
- 글의 마지막에는 반드시 글의 내용을 핵심적으로 표현할 수 있는 해시태그를 정확히 5개 추가해주세요.
- 해시태그 형식: #키워드1 #키워드2 #키워드3 #키워드4 #키워드5
- 해시태그는 글의 핵심 주제, 관련 기업, 산업 분야, 주요 키워드 등을 포함해야 합니다.
- 해시태그 앞에 "**태그:**"라는 제목을 붙여주세요.

완성형 HTML 블로그 콘텐츠를 작성해주세요. 제목은 반드시 매력적인 한국어로! 블로그 에디터에 복사-붙여넣기 했을 때 포맷팅이 그대로 유지되도록 작성하세요."""

        response = self.converter.call_api(prompt, max_tokens=4000)
        return self.converter.clean_response(response)
    
    def generate_rich_text_blog_content(self, extracted_data, wordpress_type='text'):
        """
        Rich Text 형식의 블로그 콘텐츠 생성 (다양한 블로그 플랫폼 지원)
        
        Args:
            extracted_data: 웹에서 추출된 데이터
            wordpress_type: 워드프레스 형식 ('text' 또는 'html')
            
        Returns:
            dict: 다양한 형식의 블로그 콘텐츠
        """
        
        # 기본 완성형 콘텐츠 생성
        markdown_content = self.generate_complete_blog_content(extracted_data)
        
        # HTML 형식 콘텐츠 생성
        html_content = self.generate_html_blog_content(extracted_data)
        
        # 플랫폼별 최적화된 콘텐츠 생성
        platform_optimized = self.generate_platform_optimized_content(extracted_data, wordpress_type)
        
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
    
    def generate_platform_optimized_content(self, extracted_data, wordpress_type='text'):
        """
        다양한 블로그 플랫폼에 최적화된 콘텐츠 생성
        
        Args:
            extracted_data: 웹에서 추출된 데이터
            wordpress_type: 워드프레스 형식 ('text' 또는 'html')
            
        Returns:
            dict: 플랫폼별 최적화된 콘텐츠
        """
        
        # 워드프레스용 콘텐츠 (텍스트/HTML 선택)
        if wordpress_type == 'text':
            # 텍스트 기반 워드프레스 콘텐츠
            wordpress_prompt = f"""워드프레스 블로그에 최적화된 텍스트 기반 콘텐츠를 작성해주세요.

**🚨 필수 지시사항 - 절대 지켜야 함:**
- 제목은 100% 한국어로만 작성
- 영어 제목이 입력되어도 반드시 한국어로 번역
- 네이버, 조선일보 등 한국 뉴스는 이미 한국어이므로 한국어 제목 유지

**💡 매력적인 제목 생성 가이드라인 (핵심):**
- 단순 번역이 아닌 독자의 관심을 끄는 매력적인 제목 작성
- 호기심을 자극하고 클릭하고 싶게 만드는 임팩트 있는 제목
- "왜?", "어떻게?", "무엇을?", "진짜?" 등 궁금증을 유발하는 요소 포함
- 핵심 키워드와 감정적 어필을 결합한 제목
- 예시: "Why the stock market..." → "트럼프 관세 폭탄에도 주식시장이 무덤덤한 놀라운 이유"

**🔍 워드프레스 SEO 최적화 전략 (상세):**

### 📋 메타 정보 최적화
- **SEO 제목**: 주 키워드를 앞쪽에 배치한 60자 이내 제목
- **메타 설명**: 핵심 키워드 포함 155자 이내 요약문
- **포커스 키워드**: 글의 주요 키워드 1개 선정
- **URL 슬러그**: 영문 키워드 3-5개로 구성된 SEO 친화적 URL

### 🏷️ 헤딩 구조 최적화
- **H1**: 제목에만 사용 (주 키워드 포함)
- **H2**: 주요 섹션 제목 (관련 키워드 포함)
- **H3**: 세부 소제목 (롱테일 키워드 포함)
- **논리적 계층구조**: H1 → H2 → H3 순서 준수

### 📝 콘텐츠 구조 최적화
- **서론**: 첫 문단에 포커스 키워드 자연스럽게 포함
- **본문**: 4000-5000자 이상의 충분한 분량
- **키워드 밀도**: 전체 텍스트의 1-3% 내외
- **관련 키워드**: LSI 키워드 및 동의어 활용
- **내부 링크**: 관련 포스트 연결 제안
- **외부 링크**: 신뢰할 수 있는 출처 링크

### 🎯 사용자 경험 최적화
- **읽기 쉬운 문단**: 3-4줄 이내 문단 구성
- **불릿 포인트**: 핵심 정보 목록화
- **이미지 alt 태그**: 키워드 포함 이미지 설명
- **모바일 최적화**: 반응형 디자인 고려

### 🔗 링크 최적화
- **앵커 텍스트**: 키워드 포함 자연스러운 링크 텍스트
- **관련 글 제안**: 내부 링크 3-5개 포함
- **출처 링크**: 신뢰성 있는 외부 소스 연결

**워드프레스 스타일 가이드:**
- Gutenberg 블록 에디터 호환 HTML 구조
- Yoast SEO 플러그인 호환성 고려
- 반응형 디자인 최적화
- 페이지 로딩 속도 최적화를 위한 깔끔한 코드

**원문 정보:**
제목: {extracted_data['title']}
설명: {extracted_data.get('description', '')}
본문: {extracted_data['content']['text']}

**마무리 요구사항:**
- **SEO 메타 정보 제안**: 포커스 키워드, 메타 설명, URL 슬러그 포함
- 글의 마지막에는 반드시 글의 내용을 핵심적으로 표현할 수 있는 해시태그를 정확히 5개 추가
- 해시태그 형식: #키워드1 #키워드2 #키워드3 #키워드4 #키워드5
- 해시태그는 글의 핵심 주제, 관련 기업, 산업 분야, 주요 키워드 등을 포함
- 해시태그 앞에 "**태그:**"라는 제목을 붙임

워드프레스에 바로 붙여넣을 수 있는 텍스트 기반 콘텐츠를 작성해주세요. 제목은 반드시 매력적인 한국어로!"""
        else:
            # HTML 기반 워드프레스 콘텐츠
            wordpress_prompt = f"""워드프레스 블로그에 최적화된 HTML 콘텐츠를 작성해주세요.

**중요: HTML 태그를 포함한 완전한 HTML 콘텐츠를 작성하세요. Gutenberg 블록 에디터에서 사용할 수 있는 형식입니다.**

**HTML 구조 가이드:**
- <h1>제목</h1> - 메인 제목
- <h2>소제목</h2> - 주요 섹션
- <h3>부제목</h3> - 세부 섹션
- <p>본문 문단</p> - 각 문단
- <strong>강조</strong> 또는 <em>이탤릭</em>
- <ul><li>목록 항목</li></ul> - 순서 없는 목록
- <ol><li>번호 목록</li></ol> - 순서 있는 목록
- <blockquote>인용문</blockquote> - 인용 블록
- <div class="wp-block-group">그룹화된 콘텐츠</div>

**🚨 필수 지시사항 - 절대 지켜야 함:**
- 제목은 100% 한국어로만 작성
- 영어 제목이 입력되어도 반드시 한국어로 번역
- 네이버, 조선일보 등 한국 뉴스는 이미 한국어이므로 한국어 제목 유지

**💡 매력적인 제목 생성 가이드라인 (핵심):**
- 단순 번역이 아닌 독자의 관심을 끄는 매력적인 제목 작성
- 호기심을 자극하고 클릭하고 싶게 만드는 임팩트 있는 제목
- "왜?", "어떻게?", "무엇을?", "진짜?" 등 궁금증을 유발하는 요소 포함
- 핵심 키워드와 감정적 어필을 결합한 제목
- 예시: "Why the stock market..." → "트럼프 관세 폭탄에도 주식시장이 무덤덤한 놀라운 이유"

**🔍 워드프레스 SEO 최적화 전략 (상세):**

### 📋 메타 정보 최적화
- **SEO 제목**: 주 키워드를 앞쪽에 배치한 60자 이내 제목
- **메타 설명**: 핵심 키워드 포함 155자 이내 요약문
- **포커스 키워드**: 글의 주요 키워드 1개 선정
- **URL 슬러그**: 영문 키워드 3-5개로 구성된 SEO 친화적 URL

### 🏷️ 헤딩 구조 최적화
- **H1**: 제목에만 사용 (주 키워드 포함)
- **H2**: 주요 섹션 제목 (관련 키워드 포함)
- **H3**: 세부 소제목 (롱테일 키워드 포함)
- **논리적 계층구조**: H1 → H2 → H3 순서 준수

### 📝 콘텐츠 구조 최적화
- **서론**: 첫 문단에 포커스 키워드 자연스럽게 포함
- **본문**: 4000-5000자 이상의 충분한 분량
- **키워드 밀도**: 전체 텍스트의 1-3% 내외
- **관련 키워드**: LSI 키워드 및 동의어 활용
- **내부 링크**: 관련 포스트 연결 제안
- **외부 링크**: 신뢰할 수 있는 출처 링크

### 🎯 사용자 경험 최적화
- **읽기 쉬운 문단**: 3-4줄 이내 문단 구성
- **불릿 포인트**: 핵심 정보 목록화
- **이미지 alt 태그**: 키워드 포함 이미지 설명
- **모바일 최적화**: 반응형 디자인 고려

### 🔗 링크 최적화
- **앵커 텍스트**: 키워드 포함 자연스러운 링크 텍스트
- **관련 글 제안**: 내부 링크 3-5개 포함
- **출처 링크**: 신뢰성 있는 외부 소스 연결

**워드프레스 스타일 가이드:**
- Gutenberg 블록 에디터 호환 HTML 구조
- Yoast SEO 플러그인 호환성 고려
- 반응형 디자인 최적화
- 페이지 로딩 속도 최적화를 위한 깔끔한 코드

**원문 정보:**
제목: {extracted_data['title']}
설명: {extracted_data.get('description', '')}
본문: {extracted_data['content']['text']}

**마무리 요구사항:**
- **SEO 메타 정보 제안**: 포커스 키워드, 메타 설명, URL 슬러그 포함
- 글의 마지막에는 반드시 글의 내용을 핵심적으로 표현할 수 있는 해시태그를 정확히 5개 추가
- 해시태그 형식: #키워드1 #키워드2 #키워드3 #키워드4 #키워드5
- 해시태그는 글의 핵심 주제, 관련 기업, 산업 분야, 주요 키워드 등을 포함
- 해시태그 앞에 "**태그:**"라는 제목을 붙임

워드프레스 Gutenberg 에디터에 바로 붙여넣을 수 있는 SEO 최적화된 HTML 콘텐츠를 작성해주세요. HTML 태그를 포함한 완전한 HTML 구조로 작성하세요. 제목은 반드시 매력적인 한국어로!"""

        wordpress_content = self.converter.call_api(wordpress_prompt, max_tokens=4000)
        
        # 티스토리용 콘텐츠
        tistory_prompt = f"""티스토리 블로그에 최적화된 HTML 콘텐츠를 작성해주세요.

**🚨 필수 지시사항 - 절대 지켜야 함:**
- 제목은 100% 한국어로만 작성
- 영어 제목이 입력되어도 반드시 한국어로 번역
- 네이버, 조선일보 등 한국 뉴스는 이미 한국어이므로 한국어 제목 유지

**💡 매력적인 제목 생성 가이드라인 (핵심):**
- 단순 번역이 아닌 독자의 관심을 끄는 매력적인 제목 작성
- 호기심을 자극하고 클릭하고 싶게 만드는 임팩트 있는 제목
- "왜?", "어떻게?", "무엇을?", "진짜?" 등 궁금증을 유발하는 요소 포함
- 핵심 키워드와 감정적 어필을 결합한 제목
- 예시: "Why the stock market..." → "트럼프 관세 폭탄에도 주식시장이 무덤덤한 놀라운 이유"

**🔍 티스토리 SEO 최적화 전략 (상세):**

### 📋 카카오 검색 최적화
- **제목 최적화**: 카카오 검색에 유리한 한국어 키워드 중심 제목
- **첫 문단**: 핵심 키워드를 첫 150자 내에 자연스럽게 포함
- **키워드 선택**: 한국인이 자주 검색하는 용어 우선 사용
- **지역화**: 한국 시장에 특화된 정보 및 용어 활용

### 🏷️ 티스토리 에디터 최적화
- **카테고리 활용**: 관련 카테고리 제안 (IT/테크, 경제/금융 등)
- **태그 최적화**: 검색량이 많은 한국어 태그 5-10개 제안
- **요약**: 티스토리 요약란에 적합한 100자 내외 요약문
- **썸네일**: 대표 이미지에 대한 설명 및 alt 텍스트 제안

### 📝 콘텐츠 구조 최적화
- **서론**: 독자의 호기심을 즉시 끄는 도입부
- **본문**: 2000-3000자 이상의 충실한 내용
- **키워드 배치**: 제목, 소제목, 본문에 균형 있게 분산
- **이미지 활용**: 시각적 요소로 가독성 향상
- **목록 활용**: 정보 전달력 향상을 위한 불릿 포인트

### 🎯 사용자 참여도 최적화
- **질문형 제목**: 독자 참여를 유도하는 제목 구성
- **댓글 유도**: 독자 의견을 묻는 마무리 문구
- **공유 유도**: SNS 공유에 적합한 한 줄 요약
- **연관 글**: 관련 주제 글 연결 제안

### 📱 모바일 최적화
- **짧은 문단**: 모바일 화면에 적합한 2-3줄 문단
- **읽기 쉬운 구조**: 스크롤 피로도 최소화
- **시각적 구성**: 이모지와 기호를 활용한 가독성 향상

**티스토리 스타일 가이드:**
- 티스토리 에디터 호환 HTML 구조
- 한국어 블로그 독자 친화적 표현
- 카카오 생태계 최적화
- 모바일 최우선 디자인

**원문 정보:**
제목: {extracted_data['title']}
설명: {extracted_data.get('description', '')}
본문: {extracted_data['content']['text']}

**마무리 요구사항:**
- **티스토리 SEO 정보**: 카테고리, 태그, 요약 제안 포함
- 글의 마지막에는 반드시 글의 내용을 핵심적으로 표현할 수 있는 해시태그를 정확히 5개 추가
- 해시태그 형식: #키워드1 #키워드2 #키워드3 #키워드4 #키워드5
- 해시태그는 글의 핵심 주제, 관련 기업, 산업 분야, 주요 키워드 등을 포함
- 해시태그 앞에 "**태그:**"라는 제목을 붙임

티스토리에 바로 붙여넣을 수 있는 SEO 최적화된 HTML 콘텐츠를 작성해주세요. 제목은 반드시 매력적인 한국어로!"""

        tistory_content = self.converter.call_api(tistory_prompt, max_tokens=4000)
        
        # 네이버 블로그용 콘텐츠
        naver_prompt = f"""네이버 블로그에 최적화된 콘텐츠를 작성해주세요.

**🚨 필수 지시사항 - 절대 지켜야 함:**
- 제목은 100% 한국어로만 작성
- 영어 제목이 입력되어도 반드시 한국어로 번역
- 네이버, 조선일보 등 한국 뉴스는 이미 한국어이므로 한국어 제목 유지

**💡 매력적인 제목 생성 가이드라인 (핵심):**
- 단순 번역이 아닌 독자의 관심을 끄는 매력적인 제목 작성
- 호기심을 자극하고 클릭하고 싶게 만드는 임팩트 있는 제목
- "왜?", "어떻게?", "무엇을?", "진짜?" 등 궁금증을 유발하는 요소 포함
- 핵심 키워드와 감정적 어필을 결합한 제목
- 예시: "Why the stock market..." → "트럼프 관세 폭탄에도 주식시장이 무덤덤한 놀라운 이유"

**🔍 네이버 블로그 SEO 최적화 전략 (상세):**

### 📋 네이버 검색 알고리즘 최적화
- **제목 최적화**: 네이버 검색에 노출되기 쉬운 키워드 중심 제목
- **키워드 밀도**: 네이버 최적화를 위한 2-4% 키워드 밀도
- **연관 검색어**: 네이버 연관 검색어 기반 키워드 포함
- **검색 의도**: 정보성, 상업성, 탐색성 검색 의도 고려

### 🏷️ 네이버 블로그 에디터 최적화
- **카테고리**: 적절한 네이버 블로그 카테고리 선택 제안
- **태그**: 네이버 내 검색량이 높은 태그 5-8개 제안
- **요약**: 네이버 포스트 요약에 적합한 2-3줄 요약
- **대표 이미지**: 클릭률 향상을 위한 이미지 가이드

### 📝 콘텐츠 최적화 전략
- **도입부**: 핵심 키워드를 첫 100자 내에 포함
- **본문 구성**: 1500-3000자의 적정 분량
- **정보 밀도**: 실용적이고 구체적인 정보 제공
- **신뢰성**: 출처와 데이터 기반 내용 구성
- **가독성**: 짧은 문단과 명확한 구조

### 🎯 네이버 생태계 최적화
- **네이버 뉴스**: 관련 네이버 뉴스 언급 및 연결
- **지식iN**: 독자들이 궁금해할 만한 Q&A 포함
- **실시간 검색어**: 트렌딩 키워드 반영
- **네이버 쇼핑**: 관련 상품 정보 연결 (해당시)

### 📱 네이버 모바일 최적화
- **스마트 에디터**: 네이버 스마트 에디터 호환 구조
- **모바일 가독성**: 짧은 문장과 문단 구성
- **시각적 요소**: 이미지, 표, 차트 등 활용
- **앱 최적화**: 네이버 앱에서의 표시 최적화

### 🔗 링크 및 참조 최적화
- **내부 링크**: 자신의 다른 포스트 연결
- **외부 링크**: 신뢰할 수 있는 네이버 컨텐츠 우선
- **출처 표기**: 명확한 출처 및 참고 자료 표시
- **관련 포스트**: 비슷한 주제의 글 추천

**네이버 블로그 스타일 가이드:**
- 네이버 스마트 에디터 호환성
- 한국어 독자 친화적 어조
- 네이버 검색 최적화
- 정보성과 신뢰성 중시

**원문 정보:**
제목: {extracted_data['title']}
설명: {extracted_data.get('description', '')}
본문: {extracted_data['content']['text']}

**마무리 요구사항:**
- **네이버 SEO 정보**: 카테고리, 태그, 요약, 연관 키워드 제안 포함
- 글의 마지막에는 반드시 글의 내용을 핵심적으로 표현할 수 있는 해시태그를 정확히 5개 추가
- 해시태그 형식: #키워드1 #키워드2 #키워드3 #키워드4 #키워드5
- 해시태그는 글의 핵심 주제, 관련 기업, 산업 분야, 주요 키워드 등을 포함
- 해시태그 앞에 "**태그:**"라는 제목을 붙임

네이버 블로그에 바로 붙여넣을 수 있는 SEO 최적화된 콘텐츠를 작성해주세요. 제목은 반드시 매력적인 한국어로!"""

        naver_content = self.converter.call_api(naver_prompt, max_tokens=4000)
        
        return {
            'wordpress': self.converter.clean_response(wordpress_content),
            'tistory': self.converter.clean_response(tistory_content),
            'naver': self.converter.clean_response(naver_content)
        }
    
    def save_blog_content(self, content_data, filename_prefix=None, selected_formats=None, extracted_data=None, wordpress_type='text'):
        """
        생성된 블로그 콘텐츠를 선택된 형식으로 저장 (출처별 최적화)
        
        Args:
            content_data: 생성된 콘텐츠 데이터
            filename_prefix: 파일명 접두사
            selected_formats: 저장할 파일 형식 목록 (None이면 출처에 따라 자동 결정)
            extracted_data: 원본 뉴스 데이터 (출처 감지용)
            wordpress_type: 워드프레스 형식 ('text' 또는 'html')
            
        Returns:
            dict: 저장된 파일 정보
        """
        
        if filename_prefix is None:
            filename_prefix = f"blog_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 출처별 적절한 형식 자동 결정 (selected_formats가 None인 경우에만)
        if selected_formats is None:
            if extracted_data:
                source_info = self.detect_news_source(extracted_data)
                selected_formats = source_info['recommended_formats']
                self.logger.info(f"출처 기반 자동 형식 선택: {source_info['name']} → {selected_formats}")
            else:
                # 추출 데이터가 없는 경우 기본값 사용
                selected_formats = ['md', 'wordpress']
                self.logger.info(f"기본 형식 사용: {selected_formats}")
        else:
            # selected_formats가 전달된 경우 그대로 사용
            self.logger.info(f"사용자 선택 형식 사용: {selected_formats}")
        
        saved_files = {}
        
        # 마크다운 파일 저장 (selected_formats에 포함된 경우에만)
        if 'md' in selected_formats:
            markdown_file = self.output_dir / f"{filename_prefix}.md"
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(content_data['markdown'])
            saved_files['md'] = str(markdown_file)
            self.logger.info(f"마크다운 파일 저장: {markdown_file}")
        
        # 플랫폼별 파일 저장 (기본 HTML 제거)
        platform_mapping = {
            'naver': 'naver',
            'tistory': 'tistory', 
            'wordpress': 'wordpress'
        }
        
        for format_key, platform_key in platform_mapping.items():
            if format_key in selected_formats and platform_key in content_data['platform_optimized']:
                # 워드프레스는 선택된 형식에 따라 확장자 결정
                if format_key == 'wordpress' and wordpress_type == 'html':
                    extension = '.html'
                elif format_key == 'wordpress' and wordpress_type == 'text':
                    extension = '.txt'
                else:
                    # 네이버와 티스토리는 항상 HTML
                    extension = '.html'
                
                platform_file = self.output_dir / f"{filename_prefix}_{platform_key}{extension}"
                with open(platform_file, 'w', encoding='utf-8') as f:
                    f.write(content_data['platform_optimized'][platform_key])
                saved_files[format_key] = str(platform_file)
        
        # 메타 정보와 기본 HTML 파일 생성 제거됨
        
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
    
    # 결과 저장 (테스트용이므로 extracted_data 없이 저장)
    saved_files = generator.save_blog_content(result, extracted_data=sample_data)
    
    print("✅ 완성형 블로그 콘텐츠 생성 완료!")
    print(f"📁 저장된 파일: {saved_files}")

if __name__ == "__main__":
    main() 