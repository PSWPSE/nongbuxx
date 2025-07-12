import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random
from typing import List, Dict, Optional, Any
import logging
from fake_useragent import UserAgent
import re
from urllib.parse import urljoin, urlparse
import hashlib

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizedNewsExtractor:
    """빠르고 가벼운 뉴스 추출기"""
    
    def __init__(self, base_url: str, search_keywords: Optional[str] = None, max_news: int = 10):
        self.base_url = base_url
        self.search_keywords = search_keywords
        self.max_news = max_news
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # 성능 최적화를 위한 설정
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 요청 타임아웃 설정 (성능 최적화)
        self.timeout = 10
        
        # 잘못된 링크 패턴 (주식 ticker 등)
        self.invalid_patterns = [
            r'/quote/[A-Z0-9]+-USD',  # 암호화폐 ticker
            r'/quote/[A-Z0-9]+\..*',  # 주식 ticker with exchange
            r'/quote/[A-Z]{1,5}$',    # 주식 ticker
            r'/symbol/[A-Z0-9]+',     # 심볼 페이지
            r'/lookup/',              # 검색 페이지
            r'/calendar/',            # 캘린더
            r'/screener/',            # 스크리너
            r'/research/',            # 리서치
            r'/premium/',             # 프리미엄
            r'/video/',               # 비디오
            r'/author/',              # 저자 페이지
            r'/topic/[^/]+/$',        # 토픽 메인 페이지 (뉴스 아님)
        ]
    
    def extract_news(self) -> List[Dict[str, Any]]:
        """뉴스 추출 메인 함수"""
        try:
            print(f"뉴스 추출 시작: {self.base_url}")
            
            # 빠른 HTML 요청
            html_content = self._fetch_html()
            if not html_content:
                return []
            
            # 뉴스 링크 추출
            news_links = self._extract_news_links(html_content)
            
            # 뉴스 아이템 생성
            news_items = self._create_news_items(news_links)
            
            print(f"HTML 파싱에서 {len(news_items)}개 뉴스 추출 완료")
            return news_items[:self.max_news]
            
        except Exception as e:
            logger.error(f"뉴스 추출 오류: {e}")
            return []
    
    def _extract_news_links(self, html: str) -> List[Dict[str, str]]:
        """HTML에서 뉴스 링크 추출 (성능 최적화)"""
        soup = BeautifulSoup(html, 'html.parser')
        news_links = []
        
        # Yahoo Finance 뉴스 링크 추출 (실제 구조 기반)
        if 'finance.yahoo.com' in self.base_url:
            # 모든 링크를 확인하고 뉴스 기사 링크만 필터링
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                # 필요한 개수만큼 추출되면 중단 (성능 최적화)
                if len(news_links) >= self.max_news * 2:  # 여유분 포함
                    break
                    
                href = link.get('href')
                if not href:
                    continue
                
                text = link.get_text(strip=True)
                
                # 뉴스 기사 패턴 확인
                if (self._is_valid_news_link(str(href)) and 
                    len(text) > 20 and  # 충분한 길이의 제목
                    text != 'Ad' and  # 광고 제외
                    not text.startswith('See more') and  # 더보기 링크 제외
                    not text.startswith('View')):  # 뷰 링크 제외
                    
                    full_url = urljoin(self.base_url, str(href))
                    news_links.append({
                        'url': full_url,
                        'title': text
                    })
        
        # 중복 제거 (URL 기준)
        seen_urls = set()
        unique_links = []
        for link in news_links:
            if link['url'] not in seen_urls:
                seen_urls.add(link['url'])
                unique_links.append(link)
                
                # 필요한 개수만큼 추출되면 중단
                if len(unique_links) >= self.max_news:
                    break
        
        return unique_links
    
    def _fetch_html(self) -> Optional[str]:
        """HTML 페이지 가져오기 (더 가벼운 버전)"""
        try:
            # 단순한 캐시 방지 (성능 최적화)
            cache_buster = int(time.time() % 86400)  # 하루 단위로 순환
            url = f"{self.base_url}?_cb={cache_buster}"
            
            # 최적화된 헤더 (필수만)
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            print(f"[OPTIMIZED] 요청 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"[OPTIMIZED] 응답 상태: {response.status_code}")
            print(f"[OPTIMIZED] 응답 길이: {len(response.text):,} 문자")
            
            return response.text
            
        except Exception as e:
            logger.error(f"HTML 가져오기 실패: {e}")
            return None
    
    def _is_valid_news_link(self, url: str) -> bool:
        """유효한 뉴스 링크인지 확인"""
        # 잘못된 패턴 확인
        for pattern in self.invalid_patterns:
            if re.search(pattern, url):
                return False
        
        # 뉴스 URL 패턴 확인
        news_patterns = [
            r'/news/[a-zA-Z0-9-]+\.html',  # 표준 뉴스 URL
            r'/news/[a-zA-Z0-9-]+-\d+\.html',  # 뉴스 ID 포함
        ]
        
        for pattern in news_patterns:
            if re.search(pattern, url):
                return True
        
        return False
    
    def _create_news_items(self, links: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """뉴스 아이템 생성"""
        news_items = []
        
        for link in links:
            # 키워드 추출 (제목에서)
            keywords = self._extract_keywords(link['title'])
            
            news_item = {
                'title': link['title'],
                'url': link['url'],
                'keywords': keywords,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            news_items.append(news_item)
        
        return news_items
    
    def _extract_keywords(self, title: str) -> List[str]:
        """제목에서 키워드 추출"""
        # 간단한 키워드 추출 (성능 최적화)
        keywords = []
        
        # 대문자 단어 추출 (회사명, 브랜드명 등)
        uppercase_words = re.findall(r'\b[A-Z][A-Z0-9]+\b', title)
        keywords.extend(uppercase_words[:3])  # 최대 3개
        
        # 중요 키워드 패턴
        important_patterns = [
            r'\b(Bitcoin|BTC|Ethereum|ETH|Tesla|TSLA|Apple|AAPL|Google|GOOGL|Amazon|AMZN|Microsoft|MSFT|Meta|META|Netflix|NFLX|Nvidia|NVDA)\b',
            r'\b(crypto|cryptocurrency|blockchain|AI|artificial intelligence|stock|shares|market|trading|investment)\b',
        ]
        
        for pattern in important_patterns:
            matches = re.findall(pattern, title, re.IGNORECASE)
            keywords.extend(matches[:2])  # 최대 2개씩
        
        return list(set(keywords))[:5]  # 중복 제거 후 최대 5개


def extract_news_from_multiple_sources(sources: List[Dict[str, Any]], 
                                     keyword: str = "", 
                                     count: int = 10, 
                                     max_workers: int = 3) -> List[Dict[str, Any]]:
    """여러 출처에서 병렬로 뉴스 추출"""
    
    print(f"병렬 뉴스 추출 시작: {len(sources)}개 출처")
    start_time = time.time()
    
    all_news = []
    
    # 병렬 처리로 뉴스 추출
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 각 출처별로 추출 작업 제출
        future_to_source = {}
        
        for source in sources:
            # full_url이 있으면 사용, 없으면 url 사용
            base_url = source.get('full_url', source['url'])
            
            extractor = OptimizedNewsExtractor(
                base_url=base_url,
                search_keywords=keyword if keyword else None,
                max_news=count
            )
            
            future = executor.submit(extractor.extract_news)
            future_to_source[future] = source
        
        # 결과 수집
        for future in as_completed(future_to_source):
            source = future_to_source[future]
            try:
                news_items = future.result()
                
                # 디버깅: 실제 추출된 뉴스 확인
                print(f"[DEBUG] {source['name']} 추출 결과:")
                for i, item in enumerate(news_items):
                    print(f"  {i+1}. {item['title'][:50]}...")
                    print(f"     URL: {item['url']}")
                
                # 출처 정보 추가
                for item in news_items:
                    item['source_id'] = source['id']
                    item['source_name'] = source['name']
                    item['source_url'] = source['url']
                
                all_news.extend(news_items)
                
                print(f"✅ {source['name']}: {len(news_items)}개")
                
            except Exception as e:
                logger.error(f"❌ {source['name']}: {e}")
                import traceback
                print(f"[DEBUG] Exception traceback:")
                print(traceback.format_exc())
    
    end_time = time.time()
    print(f"고성능 병렬 추출: {len(all_news)}개 뉴스, {end_time - start_time:.2f}초")
    
    return all_news


def test_extractor():
    """추출기 테스트"""
    sources = [
        {
            'id': 'test_crypto',
            'name': 'Yahoo Finance Crypto Test',
            'url': 'https://finance.yahoo.com/topic/crypto/'
        }
    ]
    
    news = extract_news_from_multiple_sources(sources, count=3)
    
    print(f"\n=== 테스트 결과 ===")
    for item in news:
        print(f"제목: {item['title']}")
        print(f"URL: {item['url']}")
        print(f"키워드: {item['keywords']}")
        print("---")


if __name__ == "__main__":
    test_extractor()
