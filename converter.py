import os
from datetime import datetime
from pathlib import Path
import anthropic
from openai import OpenAI
from dotenv import load_dotenv
import re

class NewsConverter:
    def __init__(self, api_provider='anthropic', api_key=None):
        load_dotenv()
        self.api_provider = api_provider.lower()
        self.anthropic_client = None
        self.openai_client = None
        
        # 사용자 제공 API 키를 우선 사용, 없으면 환경변수에서 가져오기
        # 주 API 클라이언트 초기화
        if self.api_provider == 'anthropic':
            key = api_key if api_key else os.getenv('ANTHROPIC_API_KEY')
            if key:
                self.anthropic_client = anthropic.Anthropic(api_key=key)
                
        elif self.api_provider == 'openai':
            key = api_key if api_key else os.getenv('OPENAI_API_KEY')
            if key:
                self.openai_client = OpenAI(api_key=key)
        
        # 폴백을 위한 보조 API 클라이언트 초기화 (환경변수에서만)
        if self.api_provider == 'anthropic':
            # Anthropic을 사용할 때 OpenAI 폴백을 위해 환경변수에서 OpenAI 키 확인
            openai_fallback_key = os.getenv('OPENAI_API_KEY')
            if openai_fallback_key:
                try:
                    self.openai_client = OpenAI(api_key=openai_fallback_key)
                except Exception as e:
                    print(f"[WARN] Failed to initialize OpenAI fallback client: {e}")
        elif self.api_provider == 'openai':
            # OpenAI를 사용할 때 Anthropic 폴백을 위해 환경변수에서 Anthropic 키 확인
            anthropic_fallback_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_fallback_key:
                try:
                    self.anthropic_client = anthropic.Anthropic(api_key=anthropic_fallback_key)
                except Exception as e:
                    print(f"[WARN] Failed to initialize Anthropic fallback client: {e}")
                    
        self.output_dir = Path('converted_articles')
        self.output_dir.mkdir(exist_ok=True)

    def read_txt_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse the content
        title_match = re.search(r'제목: (.*?)\n={2,}', content)
        meta_match = re.search(r'메타 정보:\ndescription: (.*?)\n-{2,}', content, re.DOTALL)
        content_match = re.search(r'본문:\n(.*?)$', content, re.DOTALL)
        
        title = title_match.group(1) if title_match else ""
        description = meta_match.group(1).strip() if meta_match else ""
        main_content = content_match.group(1).strip() if content_match else ""
        
        return {
            'title': title,
            'description': description,
            'content': main_content
        }

    def clean_response(self, response):
        """Clean the API response text"""
        # Handle different API response formats
        text = str(response)
        text = re.sub(r'\[.*?\]', '', text)
        text = text.replace('TextBlock(citations=None, text=', '')
        text = text.replace(', type=\'text\')', '')
        text = text.strip('"\'')
        text = text.lstrip('\n')
        text = text.replace('\\n', '\n')
        return text.strip()

    def call_api(self, prompt, max_tokens=2000, temperature=0):
        """Call the appropriate API based on provider, fallback to OpenAI if Anthropic fails"""
        # Try Anthropic first if selected
        if self.api_provider == 'anthropic' and self.anthropic_client:
            try:
                message = self.anthropic_client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                print("[INFO] Used Anthropic API.")
                return message.content[0]
            except Exception as e:
                print(f"[WARN] Anthropic API failed: {e}\nFalling back to OpenAI API...")
                if not self.openai_client:
                    raise RuntimeError("OpenAI API key not set. Cannot fallback.")
                # Fallback to OpenAI
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                print("[INFO] Used OpenAI API (fallback).")
                return response.choices[0].message.content
        elif self.api_provider == 'openai' and self.openai_client:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            print("[INFO] Used OpenAI API.")
            return response.choices[0].message.content
        else:
            raise RuntimeError("No valid API client available.")

    def extract_keywords(self, content):
        """Extract keywords from content using selected API"""
        prompt = f"""당신은 뉴스 기사에서 핵심 키워드를 추출하는 전문가입니다.
        다음 기사에서 5-7개의 관련 키워드를 추출하여 해시태그 형식으로 반환해주세요.
        
        규칙:
        1. 해시태그는 한글 스타일로 작성 (#키워드)
        2. 각 해시태그는 공백으로 구분
        3. 주식 종목이 언급된 경우 반드시 포함
        4. 가장 중요한 주제어 위주로 선정
        5. 다른 텍스트나 설명 없이 해시태그만 반환
        
        예시 형식:
        #키워드1 #키워드2 #키워드3 #키워드4 #키워드5
        
        Article: {content}"""
        
        response = self.call_api(prompt, max_tokens=300)
        return self.clean_response(response)

    def generate_markdown_content(self, content):
        """Generate markdown content using selected API"""
        example = """💰 크라켄, 암호화폐 시장 점유율 확대 위해 혁신적인 P2P 결제앱 출시

▶ 표결 현황:
• "vote-a-rama" 새벽까지 지속, 종료 시점 불투명
• 일출 전 최종 표결 가능성 있다고 언론 보도
• 화요일부터 계속된 수정안 표결 과정

▶ 통과 조건:
• 상원 100명 중 통상 60명 찬성 필요하지만 "reconciliation" 절차로 과반수만 필요
• 공화당 근소한 상원 장악, 민주당 강력 반대

▶ 법안 내용과 비용:
1. 2017년 트럼프 세금감면 연장
2. 신규 세금감면 도입
3. 국방·국경보안 지출 증가

▶ 내부 갈등:
• 일론 머스크 "미친 법안"이라 강력 비판, 신정당 창당 위협
• 테슬라 $TSLA 보조금 철회 위협으로 응수"""

        prompt = f"""당신은 뉴스 기사를 한국어 스타일의 마크다운 문서로 변환하는 전문가입니다.
        아래의 형식과 스타일을 정확히 따라 변환해주세요.

        필수 형식:
        1. 제목 형식: 이모지 제목내용
           예시: "💰 크라켄, 암호화폐 시장 점유율 확대 위해 혁신적인 P2P 결제앱 출시"
           - 제목 시작에 내용을 잘 표현하는 이모지 **정확히 1개만** 사용
           - 이모지는 제목의 첫 번째 문자로 위치
           - 이모지와 제목 내용 사이에 공백 하나만 사용
           - 제목은 반드시 첫 줄에 위치
           - 제목 다음에는 빈 줄 하나 추가
           - 제목은 내용을 기반으로 독자의 관심을 끌 수 있게 작성
           - 단순 사실 나열보다는 핵심 가치나 의미를 담아 작성
           - **중요**: 이모지는 반드시 1개만, 여러 개 사용 금지

        2. 섹션 구조:
           - 각 주요 섹션은 ▶로 시작
           - 섹션 제목은 명사형으로 끝남 (예: "현황:", "전망:", "영향:")
           - 섹션 제목 뒤에는 반드시 콜론(:) 사용

        3. 글머리 기호:
           - 주요 사실/현황은 • 기호 사용
           - 순차적 내용이나 상세 설명은 1. 2. 3. 번호 사용
           - 인용구나 발언은 따옴표(" ") 사용

        4. 문체와 톤:
           - 객관적이고 명확한 문체 사용
           - 문장은 간결하게, 되도록 1-2줄 이내로 작성
           - 전문 용어는 가능한 한글로 풀어서 설명
           - 숫자나 통계는 단위와 함께 명확히 표기

        5. 구조화:
           - 중요도와 시간 순서를 고려한 섹션 배치
           - 관련 내용은 같은 섹션에 모아서 정리
           - 섹션 간 적절한 줄바꿈으로 가독성 확보
           - 마지막에는 향후 전망이나 결론 포함

        6. 특별 규칙:
           - 주식 종목명이 나오면 반드시 종목명 뒤에 $심볼 표기
           - **주식 심볼은 반드시 미국 시장 기준의 표준 심볼만 사용**
           - 거래소 접미사(.NS, .BO, .L 등) 사용 금지
           - 괄호 사용하지 않고 공백으로 구분
           예: 테슬라 $TSLA, 애플 $AAPL, 릴라이언스 $RIL (단, $RELIANCE.NS 같은 형태는 금지)
           - 인도 기업의 경우 ADR 심볼이 있다면 ADR 심볼 사용, 없다면 대표적인 미국 거래소 심볼 사용
           - 심볼을 모르는 경우 $심볼 표기 생략

        7. 제외할 내용:
           - 기자 소개나 프로필 정보 (예: "에마 오커먼은 야후 파이낸스에서...")
           - 기자 연락처나 이메일 정보 (예: "emma.ockerman@yahooinc.com으로 이메일을 보내세요")
           - 기자 경력이나 소속 언론사 소개
           - 기사 마지막의 기자 정보 블록 전체
           - 기자 관련 모든 개인 정보나 연락처
           - 홍보성 메시지나 광고 문구 (예: "지금 구독하세요", "더 많은 정보를 원하시면...")
           - 뉴스레터 구독 안내나 마케팅 메시지
           - 소셜 미디어 팔로우 유도 문구
           - 앱 다운로드나 서비스 가입 권유
           - 상업적 홍보나 광고성 콘텐츠

        예시 형식:
        {example}

        입력 데이터:
        제목: {content['title']}
        설명: {content['description']}
        본문: {content['content']}

        제목은 반드시 첫 줄에 위치하고, 내용을 잘 표현하는 이모지 하나를 시작에 넣어주세요.
        제목은 단순히 사실을 나열하는 것이 아니라, 내용의 핵심 가치나 의미를 담아 독자의 관심을 끌 수 있게 작성해주세요.
        
        이모지 선택 가이드:
        - 금융/투자 관련: 💰 💵 📈 📊
        - 기술/혁신 관련: 🚀 💡 🔧 🌟
        - 정책/규제 관련: ⚖️ 📜 🏛️ 🔨
        - 갈등/경쟁 관련: 🔥 ⚔️ 🎯 🎲
        - 협력/계약 관련: 🤝 📝 🎊 🌈
        - 성장/발전 관련: 🌱 🎉 💪 ⭐
        """
        
        response = self.call_api(prompt, max_tokens=2000)
        response = self.clean_response(response)
        
        # Ensure the title is properly formatted with exactly one emoji
        lines = response.split('\n')
        title_line = lines[0].strip()
        
        # Simple emoji detection and formatting
        import re
        
        # Check if title starts with an emoji (common emoji ranges)
        emoji_chars = ['💰', '💵', '📈', '📊', '🚀', '💡', '🔧', '🌟', '⚖️', '📜', '🏛️', '🔨', '🔥', '⚔️', '🎯', '🎲', '🤝', '📝', '🎊', '🌈', '🌱', '🎉', '💪', '⭐', '📰', '⚠️', '💱', '🚗', '⛽', '🤖', '💻', '📱', '🏦', '🏢', '🌍', '🇺🇸', '🇨🇳', '🇯🇵', '🇰🇷', '🇪🇺']
        
        # Count emojis in title
        emoji_count = sum(1 for emoji in emoji_chars if emoji in title_line)
        
        if emoji_count == 0:
            # No emoji found, add default emoji
            title = title_line if len(title_line) > 10 else content['title']
            formatted_title = f"📰 {title}\n"
            response = formatted_title + '\n'.join(lines[1:])
        elif emoji_count > 1:
            # Multiple emojis found, keep only the first one
            for emoji in emoji_chars:
                if emoji in title_line:
                    # Remove all emojis and add back only the first one
                    text_without_emojis = title_line
                    for e in emoji_chars:
                        text_without_emojis = text_without_emojis.replace(e, '')
                    formatted_title = f"{emoji} {text_without_emojis.strip()}\n"
                    response = formatted_title + '\n'.join(lines[1:])
                    break
        
        # Fix stock symbol format (remove parentheses)
        response = re.sub(r'(\w+)\((\$[A-Z]+)\)', r'\1 \2', response)
        
        # First, handle specific symbol replacements that need special mapping
        specific_replacements = {
            '$RELIANCE.NS': '$RELI',  # Reliance Industries US symbol
            '$JIOFIN.NS': '$JIO',    # Use simplified symbol for Jio Financial
        }
        
        for old_symbol, new_symbol in specific_replacements.items():
            response = response.replace(old_symbol, new_symbol)
        
        # Then, remove all remaining exchange suffixes like .NS, .BO, .L, etc.
        response = re.sub(r'\$([A-Z]+)\.[A-Z]+', r'$\1', response)
        
        return response

    def generate_blog_content(self, content):
        """Generate blog-style content using selected API"""
        prompt = f"""다음 뉴스 기사를 바탕으로 블로그용 콘텐츠를 작성해주세요.

**제목 작성 가이드라인:**
- 독자들의 관심을 끌만한 매력적이고 깔끔하고 임팩트 있는 제목
- 단순한 사실 전달보다는 독자의 호기심을 자극하는 제목
- 클릭하고 싶게 만드는 강력한 어필 포인트 포함
- 너무 길지 않으면서도 핵심 메시지가 명확한 제목

**콘텐츠 구조 가이드라인:**
- 5000자 이상의 완성형 블로그 콘텐츠 (필수)
- 친근하고 설득력있는 말투 ("~에요", "~해요" 사용)
- 단락 구분 없이 계속 내용을 전개하는 것이 아닌 명확한 단락형으로 제공
- 각 단락마다 명확한 소제목 (## 또는 ###) 설정
- 내용 전달과 읽는 피로도 감소, 내용 전개의 자연스러움 고려
- 지루하지 않은 콘텐츠 소비를 목표로 구성

**단락 구성 원칙:**
- 전체 내용을 단락 제목만 봐도 대략 이해할 수 있는 정도로 핵심적인 포인트들로 구성
- 단락 내용은 단락 제목에 걸맞게 쉽게 읽히되 내용은 잘 전달되는 내용전달력이 좋은 글로 구성
- 각 단락은 2-4개 문단으로 구성하여 적절한 길이 유지
- 단락 간 자연스러운 연결과 논리적 흐름 유지

**구성 순서:**
1. 매력적이고 임팩트 있는 제목 (한 줄)
2. 한 줄 요약 (독자의 관심을 끄는 핵심 메시지)
3. 서론 (독자 관심 유발, 2-3 문단)
4. 본문 (명확한 소제목으로 구분된 단락형 구성):
   - ## 핵심 포인트 1 (단락 제목만 봐도 내용 파악 가능)
   - ## 핵심 포인트 2 (단락 제목만 봐도 내용 파악 가능)
   - ## 핵심 포인트 3 (단락 제목만 봐도 내용 파악 가능)
   - ## 시장 반응 및 전망 (단락 제목만 봐도 내용 파악 가능)
5. 결론 (2-3 문단, 핵심 메시지 재강조)

**추가 요구사항:**
- 추출된 내용 외 추가 리서치를 통한 분석과 전망 제공
- SEO 최적화 고려
- 독자의 관심과 공감을 유발하는 내용 포함
- 각 단락의 내용전달력을 극대화

**스타일 가이드:**
- 제목: 매력적이고 클릭을 유도하는 제목
- 헤드라인: ## 또는 ### 사용하여 명확한 구조 제공
- 인용문: > 기호로 중요한 내용 강조
- 강조: **굵은 글씨**로 핵심 포인트 하이라이트
- 리스트: - 또는 1. 사용하여 정보 정리
- 주식 심볼: 종목명 뒤에 $심볼 표기 (예: 테슬라 $TSLA)

**톤앤매너:**
- 친절하고 설득력있는 말투, 친근한 말투 (필수)
- 친근하고 접근하기 쉬운 문체 - "~에요", "~해요" 같은 친근한 종결어미 사용
- 전문적이지만 이해하기 쉬운 설명 - 독자를 배려하는 따뜻한 어조
- 독자의 입장에서 궁금해할 점들을 미리 해결하는 세심함
- 억지스럽지 않은 자연스러운 스토리텔링
- 독자와 소통하는 느낌, 마치 친구가 설명해주는 듯한 분위기

**입력 데이터:**
제목: {content['title']}
설명: {content['description']}
본문: {content['content']}

위 내용을 바탕으로 독자가 끝까지 흥미롭게 읽을 수 있는 블로그 콘텐츠를 작성해주세요.

**최종 체크사항:**
1. 5000자 이상인지 확인 (필수조건)
2. 5000자 미달 시 관련 배경정보, 시장 분석, 전문가 의견, 유사 사례 등으로 내용 보강
3. 친근하고 설득력있는 말투 적용 확인
4. 각 단락의 내용전달력과 가독성 확인
5. 단락 제목만 봐도 내용을 파악할 수 있는지 확인

독자가 마지막까지 재미있게 읽고, 도움이 되는 정보를 얻을 수 있도록 친근하면서도 전문적인 콘텐츠를 작성해주세요."""
        
        response = self.call_api(prompt, max_tokens=4000)
        return self.clean_response(response)

    def generate_threads_content(self, content):
        """Generate Threads-style content using selected API (490자 미만)"""
        prompt = f"""다음 뉴스 기사를 바탕으로 Threads용 짧은 콘텐츠를 작성해주세요.

**Threads 콘텐츠 가이드라인:**
- **글자수 제한: 490자 미만 (필수)**
- 마크다운과 동일한 구조화된 스타일 적용
- 핵심 정보만 간결하게 전달
- 소셜 미디어 친화적인 톤앤매너

**필수 형식:**
1. 제목 형식: 이모지 제목내용
   예시: "💰 크라켄, 암호화폐 시장 점유율 확대 위해 혁신적인 P2P 결제앱 출시"
   - 제목 시작에 내용을 잘 표현하는 이모지 **정확히 1개만** 사용
   - 이모지와 제목 내용 사이에 공백 하나만 사용

2. 핵심 포인트 구조:
   - ▶ 섹션명: 으로 주요 정보 구분
   - • 글머리 기호로 핵심 사실 나열
   - 1. 2. 3. 번호로 순차적 내용 설명

3. 문체와 톤:
   - 간결하고 임팩트 있는 문장
   - 핵심 메시지만 선별적으로 포함
   - 읽기 쉬운 구조화된 형태

4. 특별 규칙:
   - 주식 종목명이 나오면 반드시 종목명 뒤에 $심볼 표기
   - 제외할 내용: 기자 소개, 연락처, 홍보성 메시지

**490자 이내 예시:**
💰 크라켄, 암호화폐 시장 점유율 확대 위해 혁신적인 P2P 결제앱 출시

▶ 주요 현황:
• "vote-a-rama" 새벽까지 지속, 종료 시점 불투명
• 상원 100명 중 과반수만 필요

▶ 법안 내용:
1. 2017년 트럼프 세금감면 연장
2. 신규 세금감면 도입
3. 국방·국경보안 지출 증가

▶ 내부 갈등:
• 일론 머스크 "미친 법안"이라 강력 비판
• 테슬라 $TSLA 보조금 철회 위협으로 응수

**입력 데이터:**
제목: {content['title']}
설명: {content['description']}
본문: {content['content']}

**중요**: 반드시 490자 미만으로 작성하고, 핵심 정보만 선별하여 포함해주세요.
490자를 초과하면 안 됩니다. 글자수를 반드시 확인하세요."""
        
        response = self.call_api(prompt, max_tokens=800)
        cleaned_response = self.clean_response(response)
        
        # 글자수 체크 및 필요시 자동 단축
        char_count = len(cleaned_response)
        if char_count >= 490:
            # 490자 미만으로 단축
            lines = cleaned_response.split('\n')
            shortened_content = []
            current_length = 0
            
            for line in lines:
                if current_length + len(line) + 1 < 490:  # +1 for newline
                    shortened_content.append(line)
                    current_length += len(line) + 1
                else:
                    # 마지막 라인은 생략 표시로 대체
                    if shortened_content:
                        shortened_content.append("...")
                    break
            
            cleaned_response = '\n'.join(shortened_content)
        
        return cleaned_response

    def convert_from_data(self, extracted_data):
        """
        추출된 데이터를 직접 마크다운으로 변환 (최적화된 메서드)
        
        Args:
            extracted_data: WebExtractor에서 추출된 데이터 구조
            
        Returns:
            str: 변환된 마크다운 콘텐츠
        """
        # 추출된 데이터를 변환기가 이해할 수 있는 형태로 변환
        content_text = extracted_data['content']['text']
        
        # 제목과 설명 추출
        title = extracted_data['title']
        description = extracted_data.get('description', '')
        
        # 변환용 데이터 구조 생성
        data = {
            'title': title,
            'description': description,
            'content': content_text
        }
        
        # 마크다운 생성
        markdown_content = self.generate_markdown_content(data)
        
        # 키워드 추출
        keywords = self.extract_keywords(f"{title}\n{description}\n{content_text}")
        
        # 최종 콘텐츠 (마크다운 + 키워드)
        final_content = f"{markdown_content}\n\n{keywords}"
        
        return final_content

    def convert_from_data_blog(self, extracted_data):
        """
        추출된 데이터를 블로그 스타일 마크다운으로 변환
        
        Args:
            extracted_data: WebExtractor에서 추출된 데이터 구조
            
        Returns:
            str: 변환된 블로그 마크다운 콘텐츠
        """
        # 추출된 데이터를 변환기가 이해할 수 있는 형태로 변환
        content_text = extracted_data['content']['text']
        
        # 제목과 설명 추출
        title = extracted_data['title']
        description = extracted_data.get('description', '')
        
        # 변환용 데이터 구조 생성
        data = {
            'title': title,
            'description': description,
            'content': content_text
        }
        
        # 블로그 마크다운 생성
        blog_content = self.generate_blog_content(data)
        
        # 키워드 추출
        keywords = self.extract_keywords(f"{title}\n{description}\n{content_text}")
        
        # 최종 콘텐츠 (블로그 마크다운 + 키워드)
        final_content = f"{blog_content}\n\n---\n\n**키워드:** {keywords}"
        
        return final_content

    def convert_to_markdown(self, data):
        """Convert parsed data to markdown format"""
        # Generate markdown content
        markdown_content = self.generate_markdown_content(data)
        
        # Extract keywords
        keywords = self.extract_keywords(f"{data['title']}\n{data['description']}\n{data['content']}")
        
        # Combine content and keywords with proper spacing
        final_content = f"{markdown_content}\n\n{keywords}"
        
        return final_content

    def process_file(self, file_path):
        """Process a single TXT file"""
        print(f"Processing {file_path} with {self.api_provider} API...")
        data = self.read_txt_file(file_path)
        markdown_content = self.convert_to_markdown(data)
        
        # Create output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{Path(file_path).stem}_{timestamp}.md"
        output_path = self.output_dir / output_filename
        
        # Save markdown content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Created {output_path}")

    def process_directory(self, directory_path):
        """Process all TXT files in a directory"""
        directory = Path(directory_path)
        for txt_file in directory.glob('*.txt'):
            self.process_file(txt_file)

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python converter.py <txt_file_or_directory> [api_provider]")
        print("api_provider options: anthropic (default) or openai")
        print("\nExamples:")
        print("  python converter.py article.txt")
        print("  python converter.py article.txt openai")
        print("  python converter.py ./articles/")
        print("  python converter.py ./articles/ openai")
        sys.exit(1)
    
    path = sys.argv[1]
    api_provider = sys.argv[2] if len(sys.argv) > 2 else 'anthropic'
    
    # Validate API provider
    if api_provider not in ['anthropic', 'openai']:
        print("Error: api_provider must be 'anthropic' or 'openai'")
        sys.exit(1)
    
    # Check if required API key is set
    if api_provider == 'anthropic' and not os.getenv('ANTHROPIC_API_KEY'):
        print("Error: ANTHROPIC_API_KEY environment variable is required")
        print("Please set your Anthropic API key in the .env file")
        sys.exit(1)
    elif api_provider == 'openai' and not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable is required")
        print("Please set your OpenAI API key in the .env file")
        sys.exit(1)
    
    converter = NewsConverter(api_provider=api_provider)
    
    if os.path.isfile(path):
        converter.process_file(path)
    elif os.path.isdir(path):
        converter.process_directory(path)
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)

if __name__ == '__main__':
    main() 