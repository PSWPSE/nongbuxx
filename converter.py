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
        prompt = f"""기사에서 5개 핵심 키워드를 해시태그로 추출하세요:

규칙:
- 한글 해시태그 (#키워드)
- 공백으로 구분
- 주식 종목 포함
- 해시태그만 반환

Article: {content}"""
        
        response = self.call_api(prompt, max_tokens=300)
        return self.clean_response(response)

    def generate_markdown_content(self, content):
        """Generate markdown content using selected API"""
        
        # 네이버 뉴스인지 확인
        is_naver_news = 'news.naver.com' in content.get('url', '') or 'naver' in content.get('source', '').lower()
        
        if is_naver_news:
            # 네이버 뉴스는 원본 한국어 제목 그대로 사용
            prompt = f"""네이버 뉴스를 한국어 마크다운으로 변환하세요:

**🚨 필수 지시사항 - 절대 지켜야 함:**
- 제목은 원본 그대로 사용 (번역하지 말 것)
- 제목 앞에 적절한 이모지 1개 추가
- 네이버 뉴스는 이미 한국어이므로 제목 번역 금지

**형식 규칙:**
- 제목: 이모지 + 원본 한국어 제목 그대로
- 섹션: ▶ 섹션명: 
- 항목: • 내용 또는 1. 내용

**주식 심볼 처리 규칙 (X 콘텐츠 전용):**
- 한국 기업: 종목명 $한국코드 (예: 삼성전자 $005930.KS, SK하이닉스 $000660.KS)
- 해외 기업: 종목명 $미국심볼 (예: 테슬라 $TSLA, 애플 $AAPL)
- 거래소 접미사는 한국 기업(.KS)만 허용, 기타 거래소 접미사(.NS, .BO, .L, .TO 등) 금지
- 괄호 사용 금지: 삼성전자 $005930.KS (올바름), 삼성전자($005930.KS) (잘못됨)
- **X 전용 공백 규칙**: $심볼 앞뒤로 반드시 한 칸의 공백 확보 (예: 삼성전자 $005930.KS , 테슬라 $TSLA 등)

입력:
제목: {content.get('title', '')}
내용: {content.get('body', '')}

출력:"""
        else:
            # 해외 뉴스는 기존 번역 로직 적용
            prompt = f"""뉴스를 한국어 마크다운으로 변환하세요:

**🚨 필수 지시사항 - 절대 지켜야 함:**
- 제목은 100% 한국어로만 작성
- 영어 제목이 입력되어도 반드시 한국어로 번역
- 제목 앞에 적절한 이모지 1개 추가

**💡 매력적인 제목 생성 가이드라인:**
- 단순 번역이 아닌 독자의 관심을 끄는 매력적인 제목 작성
- 호기심을 자극하고 클릭하고 싶게 만드는 임팩트 있는 제목
- "왜?", "어떻게?", "무엇을?" 등 궁금증을 유발하는 요소 포함
- 핵심 키워드와 감정적 어필을 결합한 제목
- 예시: "Why the stock market has shrugged off Trump's latest tariff threats" 
  → "🔥 트럼프 관세 위협에도 주식시장이 꿈쩍 않는 놀라운 이유"

**이모지 선택 가이드:**
- 금융/투자: 💰 💵 📈 📊 🔥
- 기술/혁신: 🚀 💡 🔧 🌟 ⚡
- 정책/규제: ⚖️ 📜 🏛️ 🔨 🚨
- 갈등/경쟁: 🔥 ⚔️ 🎯 🎲 💥
- 협력/계약: 🤝 📝 🎊 🌈 ✨
- 성장/발전: 🌱 🎉 💪 ⭐ 🎯

**형식 규칙:**
- 제목: 이모지 + 매력적인 한국어 제목 (예: 🔥 트럼프 관세 위협에도 주식시장이 꿈쩍 않는 놀라운 이유)
- 섹션: ▶ 섹션명:
- 항목: • 내용 또는 1. 내용

**주식 심볼 처리 규칙 (X 콘텐츠 전용):**
- 한국 기업: 종목명 $한국코드 (예: 삼성전자 $005930.KS, SK하이닉스 $000660.KS)
- 해외 기업: 종목명 $미국심볼 (예: 테슬라 $TSLA, 애플 $AAPL)
- 거래소 접미사는 한국 기업(.KS)만 허용, 기타 거래소 접미사(.NS, .BO, .L, .TO 등) 금지
- 괄호 사용 금지: 테슬라 $TSLA (올바름), 테슬라($TSLA) (잘못됨)
- **X 전용 공백 규칙**: $심볼 앞뒤로 반드시 한 칸의 공백 확보 (예: 삼성전자 $005930.KS , 테슬라 $TSLA 등)

입력:
제목: {content.get('title', '')}
내용: {content.get('body', '')}

출력:"""

        response = self.call_api(prompt, max_tokens=800)
        return self.clean_response(response)
    
    def _has_english(self, text: str) -> bool:
        """텍스트에 영어가 포함되어 있는지 확인"""
        return bool(re.search(r'[a-zA-Z]', text))
    
    def _has_too_much_english(self, text: str) -> bool:
        """텍스트에 영어가 너무 많이 포함되어 있는지 확인 (50% 이상)"""
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(text.strip())
        return total_chars > 0 and (english_chars / total_chars) > 0.5
    
    def _translate_title_to_korean(self, title: str) -> str:
        """제목을 한국어로 번역"""
        try:
            prompt = f"""다음 영어 제목을 자연스러운 한국어로 번역하세요. 뉴스 제목으로 적합하게 번역해주세요:

영어 제목: {title}

한국어 번역:"""
            
            response = self.call_api(prompt, max_tokens=100)
            korean_title = self.clean_response(response).strip()
            
            # 번역 결과 검증
            if korean_title and len(korean_title) > 3:
                return korean_title
            else:
                return title  # 번역 실패 시 원본 반환
                
        except Exception as e:
            print(f"[WARN] 제목 번역 실패: {e}")
            return title  # 에러 시 원본 반환

    def generate_blog_content(self, content):
        """Generate blog-style content using selected API"""
        prompt = f"""뉴스를 블로그 스타일로 작성하세요:

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

**블로그 콘텐츠 작성 요구사항:**
- 4000자 내외의 블로그 콘텐츠
- 논리적인 문단 구성으로 친절하고 친근하게 설명
- 추출된 내용 외 추가 리서치를 통한 분석과 전망 제공
- SEO 최적화 고려
- 제목, 헤드라인, 인용문, 강조 등 다양한 스타일 활용
- 독자의 관심과 공감을 유발하는 내용 포함

**기본 요구사항:**
- 5000자 이상
- 친근한 말투 ("~에요", "~해요")
- ## 소제목으로 구분 (블로그는 ## 사용 허용)
- **매력적인 한국어 제목** (영어 제목은 한국어로 번역)
- 주식 심볼 포함 ($심볼, 미국 시장 기준)

**구성:**
- 매력적인 제목
- 한줄 요약
- 서론 (독자 관심 유발)
- 본문 (논리적 문단 구성)
- 추가 분석 및 전망
- 결론 및 마무리
- **해시태그 5개 (필수)**: 글의 내용을 핵심적으로 표현하는 해시태그

**구조:**
1. 임팩트 있는 **매력적인 한국어 제목**
2. 한 줄 요약  
3. 서론 (2-3 문단)
4. 본문 (## 소제목별 구분)
5. 결론

**🔥 다시 한번 강조: 제목은 무조건 매력적인 한국어로만 작성하세요!**

**마무리 요구사항:**
- 글의 마지막에는 반드시 글의 내용을 핵심적으로 표현할 수 있는 해시태그를 정확히 5개 추가
- 해시태그 형식: #키워드1 #키워드2 #키워드3 #키워드4 #키워드5
- 해시태그는 글의 핵심 주제, 관련 기업, 산업 분야, 주요 키워드 등을 포함
- 해시태그 앞에 "**태그:**"라는 제목을 붙임

입력:
제목: {content['title']}
설명: {content['description']}
본문: {content['content']}

독자가 끝까지 흥미롭게 읽을 수 있는 5000자 이상 한국어 블로그를 작성하세요. 제목은 반드시 매력적인 한국어로!"""
        
        response = self.call_api(prompt, max_tokens=4000)
        return self.clean_response(response)

    def generate_threads_content(self, content):
        """Generate Threads-style content using selected API (490자 미만)"""
        prompt = f"""뉴스를 Threads용 짧은 콘텐츠로 작성하세요:

**🚨 필수 지시사항 - 절대 지켜야 함:**
- 제목은 100% 한국어로만 작성
- 영어 제목이 입력되어도 반드시 한국어로 번역
- 네이버, 조선일보 등 한국 뉴스는 이미 한국어이므로 한국어 제목 유지

**💡 매력적인 제목 생성 가이드라인:**
- 단순 번역이 아닌 독자의 관심을 끄는 매력적인 제목 작성
- 호기심을 자극하고 클릭하고 싶게 만드는 임팩트 있는 제목
- "왜?", "어떻게?", "진짜?" 등 궁금증을 유발하는 요소 포함
- 예시: "Why the stock market..." → "🔥 트럼프 관세 위협에도 주식시장이 꿈쩍 않는 이유"

**📱 Threads 전용 자연스러운 반말 톤앤매너:**
- **자연스러운 반말 사용**: 존댓말 사용하지 않되, 억지스럽지 않게
- **차근차근 설명하는 톤**: 친근하면서도 신뢰할 수 있는 느낌
- **자연스러운 반말 패턴**:
  * "~다" / "~지" / "~해" / "~네" / "~거야" / "~는 거야"
  * "이게 중요한 포인트야" / "상황이 이렇다" / "결과적으로는 이런 거지"
  * "보면" / "그런데" / "근데" / "그래서" / "결국은"
- **오버하지 않는 표현**: "대박", "완전", "헐" 등 과한 표현 자제
- **설명하는 느낌**: 뉴스를 차근차근 정리해서 알려주는 톤
- **간결하면서도 명확한 문장**: 필요한 내용은 놓치지 않되 간결하게

**💬 자연스러운 설명체 가이드라인:**
- **논리적 순서로 설명**: 상황 → 원인 → 결과 순으로 자연스럽게
- **적절한 연결어 사용**: "그런데", "근데", "그래서", "결국", "보면" 등
- **강조할 때는 차분하게**: "이게 핵심이다", "중요한 건", "주목할 점은" 등
- **질문 형태 자제**: "알겠지?", "어때?" 같은 표현 최소화

**🔥 자연스러운 반말 예시:**
- ❌ "이거 진짜 중요해!" → ✅ "이게 중요한 포인트다"
- ❌ "주가 완전 올랐어!" → ✅ "주가가 많이 올랐네"  
- ❌ "완전 영향 줄 것 같아!" → ✅ "영향을 줄 것 같다"
- ❌ "이거 꼭 봐야 해!" → ✅ "주목해볼 만하다"

**💬 자연스러운 설명 예시:**
- ❌ "이 회사가 뭐 하는 곳이냐면. 전기차 배터리 만드는 회사야. 근데 이번에 500만 달러짜리 계약 따냈어"
- ✅ "이 회사는 전기차 배터리 소재를 만드는 곳이다. 이번에 500만 달러 규모의 계약을 체결했네"

**이모지 선택 가이드:**
- 금융/투자: 💰 💵 📈 📊 🔥
- 기술/혁신: 🚀 💡 🔧 🌟 ⚡
- 정책/규제: ⚖️ 📜 🏛️ 🔨 🚨
- 갈등/경쟁: 🔥 ⚔️ 🎯 🎲 💥
- 협력/계약: 🤝 📝 🎊 🌈 ✨

**제약사항:**
- 490자 미만 (필수)
- 이모지 + 매력적인 한국어 제목 (예: 🔥 트럼프 관세 위협에도 주식시장이 꿈쩍 않는 이유)
- ▶ 섹션: (완전 반말로 섹션명 작성 - "무슨 일이야?", "왜 중요해?", "어떻게 될까?" 등)
- • 주요 내용 (모든 설명을 짧은 반말 대화체로 작성)
- 글자수 정보나 메타 정보는 절대 포함하지 않기

**주식 심볼 처리 규칙:**
- 한국 기업: 종목명 $한국코드 (예: 삼성전자 $005930.KS, SK하이닉스 $000660.KS)
- 해외 기업: 종목명 $미국심볼 (예: 테슬라 $TSLA, 애플 $AAPL)
- 거래소 접미사는 한국 기업(.KS)만 허용, 기타 거래소 접미사(.NS, .BO, .L, .TO 등) 금지
- 괄호 사용 금지: 삼성전자 $005930.KS (올바름), 삼성전자($005930.KS) (잘못됨)

**자연스러운 반말 형식 예시:**
🔥 [매력적인 한국어 제목]

▶ 상황 정리:
• 이 회사가 큰 계약을 체결했다
• 시장에서 주목받고 있는 상황이네

▶ 핵심 포인트:
• 이게 중요한 이유는 이거다
• 앞으로 이런 영향을 줄 것 같다

**🔥 핵심: 자연스러운 반말로 차근차근 설명하되, 오버하지 않게!**

입력:
제목: {content['title']}
설명: {content['description']}
본문: {content['content']}

490자 미만으로 핵심 내용을 자연스러운 반말로 차근차근 정리해서 작성해. 오버하지 않되 친근한 톤으로!"""
        
        response = self.call_api(prompt, max_tokens=800)
        cleaned_response = self.clean_response(response)
        
        # 글자수 체크 및 필요시 자동 단축 (글자수 정보는 콘텐츠에 포함하지 않음)
        char_count = len(cleaned_response)
        if char_count >= 490:
            lines = cleaned_response.split('\n')
            shortened_content = []
            current_length = 0
            
            for line in lines:
                if current_length + len(line) + 1 < 490:
                    shortened_content.append(line)
                    current_length += len(line) + 1
                else:
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