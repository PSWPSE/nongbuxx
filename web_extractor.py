import requests
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, cast
import logging
import time
import os
import re # Added for regex operations

class WebExtractor:
    def __init__(self, use_selenium: bool = False, save_to_file: bool = True):
        """
        웹 콘텐츠 추출기 초기화
        
        Args:
            use_selenium: Selenium 사용 여부
            save_to_file: 결과를 파일로 저장할지 여부
        """
        self.use_selenium = use_selenium
        self.save_to_file = save_to_file
        self.driver: Optional[webdriver.Chrome] = None
        self.session = requests.Session()
        self.ua = UserAgent()
        self.setup_logging()
        
        # 🚨 홍보성 콘텐츠 필터링 시스템 추가
        self.promotional_patterns = {
            # 제목 기반 홍보성 키워드
            'title_keywords': [
                # 한국어 홍보성 키워드
                '광고', '프로모션', '홍보', '선전', '어필', '추천', '소개',
                '바로가기', '더보기', '전체보기', '구독', '팔로우', '로그인', '회원가입',
                '댓글', '후원', '제휴', '협찬', '스폰서', '지원', '도움',
                '특가', '할인', '이벤트', '행사', '모집', '채용', '공고',
                '출시', '런칭', '오픈', '오픈식', '기념', '축하', '감사',
                '당첨', '당첨자', '수상', '수상자', '시상', '시상식',
                '무료', '체험', '샘플', '증정', '기프트', '선물',
                
                # 영어 홍보성 키워드
                'ad', 'advertisement', 'sponsored', 'promotion', 'promotional',
                'sponsored content', 'paid', 'partnership', 'collaboration',
                'limited time', 'special offer', 'discount', 'sale', 'deal',
                'free trial', 'free sample', 'giveaway', 'contest', 'sweepstakes',
                'launch', 'release', 'announcement', 'press release',
                'event', 'celebration', 'ceremony', 'award', 'winner',
                'subscribe', 'follow', 'sign up', 'register', 'join',
                'click here', 'learn more', 'find out more', 'get started',
                'exclusive', 'premium', 'vip', 'membership', 'loyalty',
                
                # 🚨 ETF 소개 및 투자 상품 홍보성 키워드 추가
                'etf 소개', 'etf 추천', 'etf 투자', 'etf 분석', 'etf 전략',
                '투자 레이더', '투자 기회', '투자 가치', '투자 포인트',
                '투자 고려사항', '투자 검토', '투자 평가', '투자 전망',
                'etf introduction', 'etf recommendation', 'etf investment',
                'investment radar', 'investment opportunity', 'investment value',
                'investment point', 'investment consideration', 'investment review',
                'investment evaluation', 'investment outlook',
                
                # 🚨 주식 추천 및 투자 제안 키워드 추가
                '주식 어떄', '주식 추천', '주식 투자', '주식 매수', '주식 매도',
                '투자 적기', '투자 타이밍', '투자 제안', '투자 추천',
                '매수 시점', '매도 시점', '매수 타이밍', '매도 타이밍',
                '주가 전망', '주가 예측', '주가 분석', '주가 추천',
                '종목 추천', '종목 분석', '종목 전망', '종목 투자',
                'stock recommendation', 'stock pick', 'stock analysis',
                'investment suggestion', 'investment advice', 'buy recommendation',
                'sell recommendation', 'timing', 'opportunity',
                
                # 🚨 Zacks/Automated Insights 관련 키워드 (콘텐츠 생성 시 제거용)
                'zacks', 'zacks investment research', 'zacks rank', 'zacks industry rank',
                'zacks analyst', 'zacks estimate', 'zacks rating', 'zacks ranking',
                'automated insights', 'ai generated', 'machine learning',
                '웹사이트에서 확인 가능함', '자료 사용함', '데이터 기반으로 작성됨',
            ],
            
            # 제목 패턴 기반 홍보성 필터
            'title_patterns': [
                r'\[.*광고.*\]', r'\[.*sponsored.*\]', r'\[.*ad.*\]',
                r'\(.*광고.*\)', r'\(.*sponsored.*\)', r'\(.*ad.*\)',
                r'\[.*프로모션.*\]', r'\[.*promotion.*\]',
                r'\[.*이벤트.*\]', r'\[.*event.*\]',
                r'\[.*특가.*\]', r'\[.*sale.*\]', r'\[.*할인.*\]',
                r'\[.*무료.*\]', r'\[.*free.*\]',
                r'\[.*출시.*\]', r'\[.*launch.*\]',
                r'\[.*런칭.*\]', r'\[.*release.*\]',
                r'\[.*공개.*\]', r'\[.*announcement.*\]',
                r'\[.*당첨.*\]', r'\[.*winner.*\]',
                r'\[.*수상.*\]', r'\[.*award.*\]',
                
                # 🚨 ETF 소개 및 투자 상품 홍보성 패턴 추가
                r'.*etf.*투자.*레이더.*', r'.*etf.*투자.*기회.*',
                r'.*etf.*투자.*가치.*', r'.*etf.*투자.*포인트.*',
                r'.*etf.*투자.*고려사항.*', r'.*etf.*투자.*검토.*',
                r'.*etf.*투자.*평가.*', r'.*etf.*투자.*전망.*',
                r'.*etf.*소개.*', r'.*etf.*추천.*', r'.*etf.*분석.*',
                r'.*etf.*전략.*', r'.*투자.*레이더.*', r'.*투자.*기회.*',
                r'.*투자.*가치.*', r'.*투자.*포인트.*', r'.*투자.*고려사항.*',
                r'.*투자.*검토.*', r'.*투자.*평가.*', r'.*투자.*전망.*',
                
                # 🚨 주식 추천 및 투자 제안 패턴 추가
                r'.*주식\s+어떄\?.*', r'.*주식\s+추천.*', r'.*주식\s+투자.*',
                r'.*주식\s+매수.*', r'.*주식\s+매도.*', r'.*투자\s+적기.*',
                r'.*투자\s+타이밍.*', r'.*투자\s+제안.*', r'.*투자\s+추천.*',
                r'.*매수\s+시점.*', r'.*매도\s+시점.*', r'.*매수\s+타이밍.*',
                r'.*매도\s+타이밍.*', r'.*주가\s+전망.*', r'.*주가\s+예측.*',
                r'.*주가\s+분석.*', r'.*주가\s+추천.*', r'.*종목\s+추천.*',
                r'.*종목\s+분석.*', r'.*종목\s+전망.*', r'.*종목\s+투자.*',
                
                # 🚨 Zacks/Automated Insights 관련 패턴 추가
                r'.*zacks.*', r'.*automated insights.*', r'.*ai generated.*',
                r'.*machine learning.*', r'.*웹사이트에서 확인 가능함.*',
                r'.*자료 사용함.*', r'.*데이터 기반으로 작성됨.*',
            ],
        }
        
        if use_selenium:
            self.setup_selenium()
    
    def setup_logging(self) -> None:
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_selenium(self) -> None:
        """Selenium 웹드라이버 설정"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'user-agent={self.ua.random}')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
    
    def extract_data(self, url: str) -> Dict[str, Any]:
        """
        URL에서 데이터 추출
        
        Args:
            url: 추출할 웹 페이지 URL
            
        Returns:
            추출된 데이터 딕셔너리
        """
        try:
            self.logger.info(f"페이지 로딩 중: {url}")
            
            if self.use_selenium:
                data = self._extract_with_selenium(url)
            else:
                data = self._extract_with_requests(url)
            
            if self.save_to_file and data['success']:
                self._save_to_file(data)
            
            return data
            
        except TimeoutException:
            self.logger.error("페이지 로딩 시간 초과")
            return self._error_response(url, "페이지 로딩 시간 초과")
        except WebDriverException as e:
            self.logger.error(f"웹드라이버 오류: {str(e)}")
            return self._error_response(url, f"웹드라이버 오류: {str(e)}")
        except Exception as e:
            self.logger.error(f"데이터 추출 중 오류 발생: {str(e)}")
            
            # 403 Forbidden 에러에 대한 사용자 친화적 메시지 제공
            error_str = str(e)
            if '403' in error_str and 'Forbidden' in error_str:
                return self._error_response(url, "이 사이트는 자동 콘텐츠 수집을 차단하고 있습니다. 다른 뉴스 사이트를 이용해 주세요.")
            elif '404' in error_str:
                return self._error_response(url, "페이지를 찾을 수 없습니다. URL을 확인해 주세요.")
            elif '500' in error_str:
                return self._error_response(url, "웹사이트 서버에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해 주세요.")
            elif 'timeout' in error_str.lower():
                return self._error_response(url, "페이지 로딩 시간이 초과되었습니다. 다시 시도해 주세요.")
            elif 'connection' in error_str.lower():
                return self._error_response(url, "네트워크 연결에 문제가 있습니다. 인터넷 연결을 확인해 주세요.")
            else:
                return self._error_response(url, error_str)
    
    def _extract_with_requests(self, url: str) -> Dict[str, Any]:
        """requests를 사용한 데이터 추출"""
        headers = {'User-Agent': self.ua.random}
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        return self._parse_content(soup, url)
    
    def _extract_with_selenium(self, url: str) -> Dict[str, Any]:
        """Selenium을 사용한 데이터 추출"""
        if self.driver is None:
            raise RuntimeError("Selenium driver not initialized")
            
        self.driver.get(url)
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        return self._parse_content(soup, url)
    
    def _parse_content(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """HTML 콘텐츠 파싱"""
        article = self._find_article(soup)
        if not article:
            return self._error_response(url, "기사 본문을 찾을 수 없습니다")
        
        # 🚨 홍보성 콘텐츠 필터링 적용
        title = self._get_title(soup)
        if self._is_promotional_content(title):
            return self._error_response(url, "홍보성 콘텐츠로 판단되어 제외되었습니다")
        
        # 🚨 Zacks/Automated Insights 관련 메시지 제거
        content = self._get_content(article)
        # content가 딕셔너리인 경우 text 필드 추출
        if isinstance(content, dict):
            content_text = content.get('text', '')
            content_text = self._remove_zacks_automated_insights(content_text)
            # 딕셔너리 형태 유지
            content = {
                'text': content_text,
                'paragraphs': content.get('paragraphs', [])
            }
        else:
            # 문자열인 경우 그대로 처리
            content = self._remove_zacks_automated_insights(content)
        
        return {
            'success': True,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'title': title,
            'metadata': self._get_metadata(soup),
            'content': content,
            'author': self._get_author(soup),
            'publish_date': self._get_publish_date(soup),
            'publisher': self._get_publisher(soup, url)
        }
    
    def _is_promotional_content(self, title: str) -> bool:
        """홍보성 콘텐츠인지 판단"""
        if not title:
            return False
            
        title_lower = title.lower()
        
        # 1. 제목 키워드 체크
        for keyword in self.promotional_patterns['title_keywords']:
            if keyword.lower() in title_lower:
                self.logger.info(f"🚫 홍보성 콘텐츠 제외 (키워드): {title[:50]}...")
                return True
        
        # 2. 제목 패턴 체크 (대괄호, 소괄호 안의 홍보성 키워드)
        for pattern in self.promotional_patterns['title_patterns']:
            if re.search(pattern, title, re.IGNORECASE):
                self.logger.info(f"🚫 홍보성 콘텐츠 제외 (패턴): {title[:50]}...")
                return True
        
        return False
    
    def _remove_zacks_automated_insights(self, content: str) -> str:
        """Zacks/Automated Insights 관련 메시지 제거"""
        if not content:
            return content
        
        # 🚨 Zacks/Automated Insights 관련 메시지 제거 패턴
        removal_patterns = [
            # Zacks 관련
            r'Zacks\s+웹사이트에서\s+확인\s+가능함',
            r'Zacks\s+Investment\s+Research의\s+자료\s+사용함',
            r'Zacks\s+Investment\s+Research의\s+자료\s+사용함',
            r'Zacks\s+Rank\s+시스템',
            r'Zacks\s+Industry\s+Rank',
            r'Zacks\s+애널리스트',
            r'Zacks\s+평균\s+예상치',
            r'Zacks\s+등급',
            r'Zacks\s+평가',
            r'Zacks\s+순위',
            r'Zacks\s+분석',
            
            # Automated Insights 관련
            r'Automated\s+Insights의\s+데이터\s+기반으로\s+작성됨',
            r'AI\s+generated',
            r'machine\s+learning',
            r'웹사이트에서\s+확인\s+가능함',
            r'자료\s+사용함',
            r'데이터\s+기반으로\s+작성됨',
            
            # 일반적인 패턴
            r'웹사이트에서\s+확인\s+가능함\s*Zacks\s+웹사이트에서\s+확인\s+가능함',
            r'Zacks\s+웹사이트에서\s+확인\s+가능함\s*웹사이트에서\s+확인\s+가능함',
        ]
        
        cleaned_content = content
        for pattern in removal_patterns:
            cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.IGNORECASE)
        
        # 연속된 공백 정리
        cleaned_content = re.sub(r'\s+', ' ', cleaned_content)
        cleaned_content = cleaned_content.strip()
        
        if cleaned_content != content:
            self.logger.info("🚫 Zacks/Automated Insights 관련 메시지 제거됨")
        
        return cleaned_content
    
    def _find_article(self, soup: BeautifulSoup) -> Optional[Tag]:
        """기사 본문 요소 찾기"""
        # Try different selectors for article content
        selectors = [
            'article',
            '.article',
            '.articlePage',
            '.story-body',
            '.content',
            '.post-content',
            '[class*="article"]',
            '[class*="content"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and isinstance(element, Tag):
                return element
        
        # Fallback: look for main content area
        main = soup.find('main') or soup.find('div', {'role': 'main'})
        if main and isinstance(main, Tag):
            return main
            
        return None
    
    def _get_title(self, soup: BeautifulSoup) -> str:
        """제목 추출"""
        
        # Yahoo Finance 특수 처리 (먼저 시도)
        if 'finance.yahoo.com' in str(soup):
            yahoo_selectors = [
                '.cover-title',  # Yahoo Finance 실제 기사 제목
                'title',         # Page title (정확함)
            ]
            
            for selector in yahoo_selectors:
                title = soup.select_one(selector)
                if title and isinstance(title, Tag):
                    text = title.get_text().strip()
                    # Yahoo Finance 사이트 이름 제거
                    if ' - Yahoo Finance' in text:
                        text = text.replace(' - Yahoo Finance', '')
                    elif ' | Yahoo Finance' in text:
                        text = text.replace(' | Yahoo Finance', '')
                    # 유효한 제목인지 확인
                    if text and 10 <= len(text) <= 200:
                        return text.strip()
        
        # 일반적인 제목 선택자들
        title_selectors = [
            'h1',
            '#title_area h2',  # 네이버 뉴스
            '.media_end_head_headline h2',  # 네이버 뉴스
            '#articleTitle',  # 구 네이버 뉴스 
            '.headline',
            '.title',
            '[class*="title"]',
            '[class*="headline"]',
        ]
        
        for selector in title_selectors:
            title = soup.select_one(selector)
            if title and isinstance(title, Tag):
                text = title.get_text().strip()
                if text and len(text) > 5:
                    return text
        
        # meta 태그에서 제목 추출
        meta_title = soup.find('meta', property='og:title')
        if meta_title and isinstance(meta_title, Tag):
            content = meta_title.get('content', '')
            if isinstance(content, str) and content.strip():
                return content.strip()
        
        # HTML title 태그 (fallback)
        html_title = soup.find('title')
        if html_title and isinstance(html_title, Tag):
            text = html_title.get_text().strip()
            if text:
                return text
        
        return "제목 없음"
    
    def _get_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """메타데이터 추출"""
        metadata: Dict[str, str] = {}
        meta_names = ['description', 'author', 'published_time', 'keywords']
        
        for meta in soup.find_all('meta'):
            if not isinstance(meta, Tag):
                continue
                
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')
            
            if isinstance(name, str) and isinstance(content, str):
                name_lower = name.lower()
                if name_lower in meta_names and content:
                    metadata[name_lower] = content
        
        return metadata
    
    def _get_content(self, article: Tag) -> Dict[str, Any]:
        """본문 내용 추출"""
        paragraphs = []
        
        # Find all text content elements
        content_elements = article.find_all(['p', 'h2', 'h3', 'h4', 'blockquote', 'div'])
        
        for element in content_elements:
            if not isinstance(element, Tag):
                continue
                
            text = element.get_text().strip()
            
            # Skip promotional content
            skip_keywords = [
                'recommended', 'related', 'subscribe', 'follow', 'download',
                'sign up', 'newsletter', 'advertisement', 'sponsored'
            ]
            
            if (text and 
                len(text) > 10 and 
                not any(keyword in text.lower() for keyword in skip_keywords)):
                paragraphs.append(text)
        
        return {
            'text': '\n\n'.join(paragraphs),
            'paragraphs': paragraphs
        }
    
    def _get_author(self, soup: BeautifulSoup) -> str:
        """저자 정보 추출"""
        # Try meta tag first
        author_meta = soup.find('meta', {'name': 'author'})
        if author_meta and isinstance(author_meta, Tag):
            content = author_meta.get('content', '')
            if isinstance(content, str) and content:
                return content
        
        # Try various author selectors
        author_selectors = [
            '[class*="author"]',
            '[class*="byline"]',
            '.author',
            '.byline'
        ]
        
        for selector in author_selectors:
            author = soup.select_one(selector)
            if author and isinstance(author, Tag):
                text = author.get_text().strip()
                if text and len(text) < 100:  # Reasonable author name length
                    return text
        
        return ''
    
    def _get_publish_date(self, soup: BeautifulSoup) -> str:
        """발행일 추출"""
        # Try meta tags first
        date_meta = (soup.find('meta', {'name': 'date'}) or 
                    soup.find('meta', {'property': 'article:published_time'}))
        if date_meta and isinstance(date_meta, Tag):
            content = date_meta.get('content', '')
            if isinstance(content, str) and content:
                return content
        
        # Try various date selectors
        date_selectors = [
            '[class*="date"]',
            '[class*="time"]',
            '.date',
            '.time',
            '.published'
        ]
        
        for selector in date_selectors:
            date = soup.select_one(selector)
            if date and isinstance(date, Tag):
                text = date.get_text().strip()
                if text and len(text) < 50:  # Reasonable date length
                    return text
        
        return ''
    
    def _get_publisher(self, soup: BeautifulSoup, url: str) -> str:
        """출처/발행사 정보 추출"""
        # 1. Meta 태그에서 publisher 정보 찾기
        publisher_meta = (
            soup.find('meta', {'property': 'og:site_name'}) or
            soup.find('meta', {'name': 'publisher'}) or
            soup.find('meta', {'property': 'article:publisher'})
        )
        if publisher_meta and isinstance(publisher_meta, Tag):
            content = publisher_meta.get('content', '')
            if isinstance(content, str) and content:
                return content.strip()
        
        # 2. 도메인별 하드코딩된 출처 매핑
        domain_to_publisher = {
            'bloomberg.com': 'Bloomberg',
            'wsj.com': 'WSJ',
            'reuters.com': 'Reuters',
            'ft.com': 'Financial Times',
            'cnbc.com': 'CNBC',
            'finance.yahoo.com': 'Yahoo Finance',
            'naver.com': '네이버뉴스',
            'news.naver.com': '네이버뉴스',
            'yna.co.kr': '연합뉴스',
            'bbc.com': 'BBC',
            'cnn.com': 'CNN',
            'forbes.com': 'Forbes',
            'economist.com': 'The Economist',
            'techcrunch.com': 'TechCrunch',
            'theverge.com': 'The Verge'
        }
        
        # URL에서 도메인 추출
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # www. 제거
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # 도메인 매핑에서 찾기
        for key, value in domain_to_publisher.items():
            if key in domain:
                return value
        
        # 3. HTML에서 publisher 정보 찾기
        publisher_selectors = [
            '.publisher',
            '.source',
            '[class*="publisher"]',
            '[class*="source"]',
            '.media_end_head_top_logo img',  # 네이버 뉴스 언론사 로고
            '.press_logo img'  # 네이버 뉴스 언론사 로고 (구버전)
        ]
        
        for selector in publisher_selectors:
            publisher = soup.select_one(selector)
            if publisher and isinstance(publisher, Tag):
                # 이미지인 경우 alt 텍스트 확인
                if publisher.name == 'img':
                    alt_text = publisher.get('alt', '')
                    if isinstance(alt_text, str) and alt_text:
                        return alt_text.strip()
                else:
                    text = publisher.get_text().strip()
                    if text and len(text) < 50:
                        return text
        
        # 4. 도메인명을 출처로 사용 (fallback)
        return domain.split('.')[0].title()
    
    def _error_response(self, url: str, error_message: str) -> Dict[str, Any]:
        """에러 응답 생성"""
        return {
            'success': False,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'error': error_message
        }
    
    def _save_to_file(self, data: Dict[str, Any]) -> None:
        """결과를 파일로 저장"""
        os.makedirs('extracted_articles', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        txt_path = f'extracted_articles/article_{timestamp}.txt'
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"제목: {data['title']}\n")
            f.write("="*80 + "\n\n")
            
            if data['metadata']:
                f.write("메타 정보:\n")
                for key, value in data['metadata'].items():
                    f.write(f"{key}: {value}\n")
                f.write("-"*80 + "\n\n")
            
            f.write("본문:\n")
            f.write(data['content']['text'])
        
        self.logger.info(f"텍스트 파일 저장됨: {txt_path}")
    
    def close(self) -> None:
        """리소스 정리"""
        if self.driver:
            self.driver.quit()
        self.session.close() 