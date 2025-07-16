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
        
        return {
            'success': True,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'title': self._get_title(soup),
            'metadata': self._get_metadata(soup),
            'content': self._get_content(article),
            'author': self._get_author(soup),
            'publish_date': self._get_publish_date(soup)
        }
    
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
    
    def _error_response(self, url: str, error: str) -> Dict[str, Any]:
        """에러 응답 생성"""
        return {
            'success': False,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'error': error
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