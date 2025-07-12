#!/usr/bin/env python3
"""
범용 뉴스 추출기 (url_extractor.py)

기능:
- 다양한 뉴스 사이트에서 뉴스 추출
- Yahoo Finance 뉴스 추출 (기존)
- 범용 뉴스 사이트 추출 (신규)
- 키워드 기반 뉴스 검색 및 필터링
- 추출 개수 사용자 지정
- 광고성 콘텐츠 자동 필터링
- JSON 파일로 결과 저장

사용법:
    python url_extractor.py                          # 최신 뉴스 10개 추출
    python url_extractor.py -k "Tesla AI"            # Tesla AI 관련 뉴스 추출
    python url_extractor.py -n 20                    # 최신 뉴스 20개 추출
    python url_extractor.py -k "Bitcoin" -n 15       # Bitcoin 관련 뉴스 15개 추출

새로운 기능:
- 범용 뉴스 사이트 지원
- 자동 RSS 피드 감지
- 메타 태그 기반 뉴스 추출
- 다양한 뉴스 사이트 구조 지원
"""

import requests
from bs4 import BeautifulSoup
import re
from collections import Counter
from urllib.parse import urljoin, urlparse
import json
import time
from datetime import datetime
from fake_useragent import UserAgent
import argparse
import sys
import feedparser
from typing import List, Dict, Optional

class UniversalNewsExtractor:
    """범용 뉴스 추출기"""
    
    def __init__(self, base_url: str, search_keywords=None, max_news=10):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.ua = UserAgent()
        self.search_keywords = search_keywords or []
        self.max_news = max_news
        
        # 검색 키워드 전처리
        if isinstance(self.search_keywords, str):
            self.search_keywords = [keyword.strip().lower() for keyword in self.search_keywords.split()]
        else:
            self.search_keywords = [keyword.strip().lower() for keyword in self.search_keywords]
        
        # 뉴스 선택자 패턴 (일반적인 뉴스 사이트 구조)
        self.news_selectors = [
            'article h1 a', 'article h2 a', 'article h3 a',
            '.news-item a', '.article-item a', '.story-item a',
            'h1 a', 'h2 a', 'h3 a',
            '.headline a', '.title a', '.news-title a',
            '[class*="headline"] a', '[class*="title"] a',
            '[class*="article"] a', '[class*="news"] a',
            '.entry-title a', '.post-title a'
        ]
        
        # 제외할 URL 패턴
        self.exclude_patterns = [
            r'#', r'javascript:', r'mailto:', r'tel:',
            r'/tag/', r'/category/', r'/author/', r'/search/',
            r'/login', r'/register', r'/subscribe', r'/about',
            r'/contact', r'/privacy', r'/terms', r'/advertise'
        ]
        
        # 불용어 (키워드 추출 시 제외)
        self.stop_words = {
            'the', 'is', 'at', 'which', 'on', 'and', 'or', 'but', 'in', 'with',
            'a', 'an', 'as', 'are', 'was', 'were', 'been', 'be', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'can', 'to', 'of', 'for', 'by', 'from', 'up', 'about',
            'into', 'through', 'during', 'before', 'after', 'above', 'below', 'out',
            'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
            'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
            'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
            'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now',
            'says', 'said', 'according', 'report', 'reports', 'news', 'article',
            'story', 'finance', 'yahoo', 'latest', 'today', 'new', 'this', 'that',
            'these', 'those', 'breaking', 'updated', 'read', 'more', 'click'
        }
    
    def get_page_content(self, url: str) -> Optional[str]:
        """웹 페이지 내용 가져오기"""
        try:
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            return response.text
            
        except requests.RequestException as e:
            print(f"페이지 요청 중 오류 발생: {e}")
            return None
    
    def try_rss_feed(self, url: str) -> List[Dict]:
        """RSS 피드 시도 (입력 URL 기반 + 도메인 기반)"""
        try:
            # 일반적인 RSS 피드 경로들
            rss_paths = [
                '/rss', '/rss.xml', '/feed', '/feed.xml',
                '/rss/news', '/feeds/news', '/news/rss',
                '/atom.xml', '/index.xml'
            ]
            
            base_domain = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            
            # 1. 입력된 URL 기반으로 RSS 피드 시도 (우선)
            parsed_url = urlparse(url)
            if parsed_url.path and parsed_url.path != '/':
                print(f"입력된 URL 기반 RSS 피드 시도: {url}")
                
                # 입력된 URL에 RSS 경로 추가해서 시도
                for path in rss_paths:
                    try:
                        # 입력 URL의 경로에 RSS 경로 추가
                        rss_url = url.rstrip('/') + path
                        feed = feedparser.parse(rss_url)
                        
                        if feed.entries:
                            print(f"RSS 피드 발견: {rss_url}")
                            news_items = []
                            
                            for entry in feed.entries[:self.max_news]:
                                if hasattr(entry, 'title') and hasattr(entry, 'link'):
                                    news_items.append({
                                        'title': str(entry.title),
                                        'url': entry.link,
                                        'keywords': self.extract_keywords(str(entry.title)),
                                        'published_date': getattr(entry, 'published', '')
                                    })
                            
                            if news_items:
                                return news_items
                                
                    except Exception as e:
                        continue
            
            # 2. 도메인 기반 RSS 피드 시도 (백업)
            print(f"도메인 기반 RSS 피드 시도: {base_domain}")
            for path in rss_paths:
                try:
                    rss_url = base_domain + path
                    feed = feedparser.parse(rss_url)
                    
                    if feed.entries:
                        print(f"RSS 피드 발견: {rss_url}")
                        news_items = []
                        
                        for entry in feed.entries[:self.max_news]:
                            if hasattr(entry, 'title') and hasattr(entry, 'link'):
                                news_items.append({
                                    'title': str(entry.title),
                                    'url': entry.link,
                                    'keywords': self.extract_keywords(str(entry.title)),
                                    'published_date': getattr(entry, 'published', '')
                                })
                        
                        if news_items:
                            return news_items
                            
                except Exception as e:
                    continue
            
            return []
            
        except Exception as e:
            print(f"RSS 피드 추출 중 오류: {e}")
            return []
    
    def extract_news_from_html(self, html_content: str) -> List[Dict]:
        """HTML에서 뉴스 링크 추출"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            found_links = []
            
            # 다양한 선택자로 뉴스 링크 찾기
            for selector in self.news_selectors:
                try:
                    links = soup.select(selector)
                    for link in links:
                        href = link.get('href')
                        if href:
                            found_links.append({
                                'element': link,
                                'title': link.get_text(strip=True),
                                'url': href
                            })
                except Exception as e:
                    continue
            
            # 중복 제거 및 정리
            unique_links = {}
            for link in found_links:
                url = link['url']
                title = link['title']
                
                # 상대 URL을 절대 URL로 변환
                if url.startswith('/'):
                    url = urljoin(self.base_url, url)
                elif not url.startswith('http'):
                    continue
                
                # 제외할 URL 패턴 체크
                if any(re.search(pattern, url, re.IGNORECASE) for pattern in self.exclude_patterns):
                    continue
                
                # 제목이 너무 짧거나 비어있는 경우 제외
                if not title or len(title.strip()) < 10:
                    continue
                
                # 중복 URL 제거
                if url not in unique_links:
                    unique_links[url] = {
                        'title': title,
                        'url': url,
                        'keywords': self.extract_keywords(title)
                    }
            
            return list(unique_links.values())
            
        except Exception as e:
            print(f"HTML 파싱 중 오류: {e}")
            return []
    
    def extract_keywords(self, text: str, num_keywords: int = 3) -> List[str]:
        """텍스트에서 주요 키워드 추출"""
        if not text:
            return []
            
        # 텍스트 정제
        text = text.lower()
        text = re.sub(r'[^a-zA-Z가-힣\s]', ' ', text)
        
        # 단어 분리
        words = text.split()
        
        # 불용어 제거 및 길이 필터링
        filtered_words = [
            word for word in words 
            if word not in self.stop_words and len(word) > 2
        ]
        
        # 빈도수 계산
        word_freq = Counter(filtered_words)
        
        # 상위 키워드 반환
        return [word for word, _ in word_freq.most_common(num_keywords)]
    
    def matches_keywords(self, title: str, url: str = "") -> bool:
        """키워드와 매치되는지 확인"""
        if not self.search_keywords:
            return True
        
        search_text = (title + " " + url).lower()
        return any(keyword in search_text for keyword in self.search_keywords)
    
    def calculate_relevance_score(self, title: str, url: str = "") -> float:
        """키워드 관련성 점수 계산"""
        if not self.search_keywords:
            return 1.0
        
        search_text = (title + " " + url).lower()
        score = 0
        
        for keyword in self.search_keywords:
            title_count = title.lower().count(keyword) * 2
            url_count = url.lower().count(keyword)
            score += title_count + url_count
        
        return score
    
    def extract_news(self) -> List[Dict]:
        """뉴스 추출 (입력 URL 직접 파싱 우선, RSS 백업)"""
        print(f"뉴스 추출 시작: {self.base_url}")
        
        # 1. 입력된 URL에서 직접 HTML 파싱 시도 (우선)
        html_content = self.get_page_content(self.base_url)
        if html_content:
            print(f"입력된 URL에서 직접 HTML 파싱 시도: {self.base_url}")
            news_items = self.extract_news_from_html(html_content)
            
            if news_items:
                # 키워드 필터링
                if self.search_keywords:
                    filtered_items = []
                    for item in news_items:
                        if self.matches_keywords(item['title'], item['url']):
                            item['relevance_score'] = self.calculate_relevance_score(item['title'], item['url'])
                            filtered_items.append(item)
                    
                    # 관련성 점수 순으로 정렬
                    filtered_items.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
                    result = filtered_items[:self.max_news]
                else:
                    result = news_items[:self.max_news]
                
                if result:
                    print(f"HTML 파싱에서 {len(result)}개 뉴스 추출 완료")
                    return result
            
            print("HTML 파싱에서 뉴스를 찾을 수 없음, RSS 백업 시도")
        else:
            print("HTML 내용을 가져올 수 없음, RSS 백업 시도")
        
        # 2. RSS 피드 백업 시도
        rss_news = self.try_rss_feed(self.base_url)
        if rss_news:
            filtered_news = []
            for news in rss_news:
                if self.matches_keywords(news['title'], news['url']):
                    filtered_news.append(news)
            
            if filtered_news:
                print(f"RSS 백업에서 {len(filtered_news)}개 뉴스 추출")
                return filtered_news[:self.max_news]
        
        print("HTML 파싱과 RSS 백업 모두 실패")
        return []

class YahooFinanceNewsExtractor:
    def __init__(self, search_keywords=None, max_news=10):
        self.base_url = "https://finance.yahoo.com"
        self.latest_news_url = "https://finance.yahoo.com/topic/latest-news/"
        self.ua = UserAgent()
        self.search_keywords = search_keywords or []
        self.max_news = max_news
        
        # 검색 키워드 전처리
        if isinstance(self.search_keywords, str):
            self.search_keywords = [keyword.strip().lower() for keyword in self.search_keywords.split()]
        else:
            self.search_keywords = [keyword.strip().lower() for keyword in self.search_keywords]
        
        # 한국어-영어 키워드 매핑 추가
        self.keyword_mapping = {
            # 주식 관련
            '주식': ['stock', 'stocks', 'equity', 'share', 'shares'],
            '증권': ['securities', 'stock', 'shares'],
            '투자': ['investment', 'investing', 'invest'],
            '시장': ['market', 'markets'],
            '거래': ['trading', 'trade'],
            '상장': ['ipo', 'listing', 'public'],
            '배당': ['dividend', 'dividends'],
            '펀드': ['fund', 'funds', 'etf'],
            
            # 암호화폐 관련
            '암호화폐': ['cryptocurrency', 'crypto', 'bitcoin', 'ethereum'],
            '코인': ['coin', 'crypto', 'cryptocurrency'],
            '비트코인': ['bitcoin', 'btc'],
            '이더리움': ['ethereum', 'eth'],
            '블록체인': ['blockchain', 'crypto'],
            '스테이블코인': ['stablecoin', 'usdt', 'usdc', 'stable'],
            '디파이': ['defi', 'decentralized finance'],
            'nft': ['nft', 'non-fungible token'],
            
            # 경제 관련
            '경제': ['economy', 'economic'],
            '금리': ['interest rate', 'rate', 'fed'],
            '인플레이션': ['inflation', 'cpi'],
            '달러': ['dollar', 'usd'],
            '환율': ['exchange rate', 'currency'],
            '무역': ['trade', 'trading'],
            '수출': ['export', 'exports'],
            '수입': ['import', 'imports'],
            
            # 기업 관련
            '기업': ['company', 'companies', 'corporate'],
            '실적': ['earnings', 'results', 'performance'],
            '매출': ['revenue', 'sales'],
            '이익': ['profit', 'earnings', 'income'],
            '손실': ['loss', 'losses'],
            '인수합병': ['merger', 'acquisition', 'm&a'],
            
            # 기술 관련
            '인공지능': ['ai', 'artificial intelligence'],
            '기술': ['technology', 'tech'],
            '반도체': ['semiconductor', 'chip'],
            '전기차': ['electric vehicle', 'ev', 'tesla'],
            '에너지': ['energy', 'oil', 'gas'],
            '배터리': ['battery', 'batteries'],
            
            # 일반 금융 용어
            '은행': ['bank', 'banking'],
            '보험': ['insurance'],
            '부동산': ['real estate', 'property'],
            '채권': ['bond', 'bonds'],
            '신용': ['credit'],
            '대출': ['loan', 'lending'],
        }
        
        # 확장된 검색 키워드 생성
        self.expanded_keywords = self._expand_keywords(self.search_keywords)
        
        # 광고성 콘텐츠 필터링 키워드
        self.ad_keywords = [
            'sponsored', 'advertisement', 'promoted', 'ad', 'promo',
            'affiliate', 'partner', 'deals', 'offer', 'discount',
            'sale', 'buy now', 'click here', 'learn more'
        ]
        
        # 불용어 (키워드 추출 시 제외)
        self.stop_words = {
            'the', 'is', 'at', 'which', 'on', 'and', 'or', 'but', 'in', 'with',
            'a', 'an', 'as', 'are', 'was', 'were', 'been', 'be', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'can', 'to', 'of', 'for', 'by', 'from', 'up', 'about',
            'into', 'through', 'during', 'before', 'after', 'above', 'below', 'out',
            'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
            'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
            'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
            'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now',
            'says', 'said', 'according', 'report', 'reports', 'news', 'article',
            'story', 'finance', 'yahoo', 'latest', 'today', 'new', 'this', 'that',
            'these', 'those', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours',
            'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he',
            'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its',
            'itself', 'they', 'them', 'their', 'theirs', 'themselves'
        }
        
    def _expand_keywords(self, keywords):
        """키워드를 확장 (한국어 -> 영어 매핑 포함)"""
        expanded = []
        
        for keyword in keywords:
            # 원본 키워드 추가
            expanded.append(keyword)
            
            # 매핑된 영어 키워드 추가
            if keyword in self.keyword_mapping:
                expanded.extend(self.keyword_mapping[keyword])
                print(f"한국어 키워드 '{keyword}' -> 영어 키워드: {self.keyword_mapping[keyword]}")
        
        # 중복 제거
        return list(set(expanded))
        
    def get_page_content(self, url):
        """웹 페이지 내용 가져오기"""
        try:
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            return response.text
            
        except requests.RequestException as e:
            print(f"페이지 요청 중 오류 발생: {e}")
            return None
    
    def is_ad_content(self, title, url):
        """광고성 콘텐츠 여부 확인"""
        title_lower = title.lower()
        url_lower = url.lower()
        
        # 광고 키워드 체크
        for keyword in self.ad_keywords:
            if keyword in title_lower or keyword in url_lower:
                return True
        
        # 특정 도메인 제외
        parsed_url = urlparse(url)
        excluded_domains = ['promotions.yahoo.com', 'shopping.yahoo.com', 'finance.yahoo.com/m/']
        
        if any(domain in parsed_url.netloc for domain in excluded_domains):
            return True
            
        return False
    
    def matches_keywords(self, title, url=""):
        """키워드와 매치되는지 확인 (확장된 키워드 사용)"""
        if not self.expanded_keywords:
            return True  # 키워드가 없으면 모든 뉴스 포함
        
        search_text = (title + " " + url).lower()
        
        # 확장된 키워드 중 하나라도 포함되면 매치 (OR 조건으로 변경)
        return any(keyword in search_text for keyword in self.expanded_keywords)
    
    def calculate_relevance_score(self, title, url=""):
        """키워드 관련성 점수 계산 (확장된 키워드 사용)"""
        if not self.expanded_keywords:
            return 1.0  # 키워드가 없으면 모든 뉴스 동일한 점수
        
        search_text = (title + " " + url).lower()
        score = 0
        
        for keyword in self.expanded_keywords:
            # 제목에서 키워드 출현 횟수 (가중치 2배)
            title_count = title.lower().count(keyword) * 2
            # URL에서 키워드 출현 횟수
            url_count = url.lower().count(keyword)
            score += title_count + url_count
        
        return score
    
    def extract_keywords(self, text, num_keywords=3):
        """텍스트에서 주요 키워드 추출"""
        if not text:
            return []
            
        # 텍스트 정제
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # 단어 분리
        words = text.split()
        
        # 불용어 제거 및 길이 필터링
        filtered_words = [
            word for word in words 
            if word not in self.stop_words and len(word) > 2
        ]
        
        # 빈도 계산
        word_freq = Counter(filtered_words)
        
        # 상위 키워드 반환
        top_keywords = [word for word, _ in word_freq.most_common(num_keywords)]
        
        return top_keywords
    
    def search_yahoo_finance(self, query):
        """Yahoo Finance에서 키워드 검색"""
        search_urls = []
        
        if query:
            # Yahoo Finance 검색 URL 생성
            search_query = "+".join(query.split())
            search_url = f"https://finance.yahoo.com/lookup?s={search_query}"
            search_urls.append(search_url)
            
            # 뉴스 검색 URL
            news_search_url = f"https://finance.yahoo.com/news?query={search_query}"
            search_urls.append(news_search_url)
        
        return search_urls
    
    def extract_news_from_page(self, html_content):
        """HTML에서 뉴스 정보 추출"""
        soup = BeautifulSoup(html_content, 'lxml')
        news_items = []
        
        # 다양한 뉴스 선택자 시도
        selectors = [
            'li[data-test-locator="mega"] h3 a',
            'li[data-test-locator="mega"] a[data-test-locator="main-link"]',
            'li[class*="js-stream-content"] h3 a',
            'li[class*="js-stream-content"] a[class*="js-content-viewer"]',
            'article h3 a',
            'div[class*="stream-item"] h3 a',
            'div[class*="stream-item"] a[class*="js-content-viewer"]',
            'h3 a[href*="/news/"]',
            'a[href*="/news/"][href*=".html"]'
        ]
        
        elements = []
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                print(f"선택자 '{selector}'로 {len(elements)}개 요소 발견")
                break
        
        if not elements:
            # 일반적인 링크 찾기
            all_links = soup.find_all('a', href=True)
            print(f"일반 링크 {len(all_links)}개 발견")
            
            # 뉴스 링크 필터링 (실제 뉴스 기사 URL 패턴)
            news_links = []
            for link in all_links:
                try:
                    href = link.get('href')
                    if href:
                        href_str = str(href)
                        title = link.get_text(strip=True)
                        # 실제 뉴스 기사 URL 패턴 확인
                        if (('/news/' in href_str and '.html' in href_str) or 
                            ('/news/' in href_str and any(char.isdigit() for char in href_str[-20:]))) and \
                           title and len(title) > 10:  # 제목이 10자 이상인 실제 기사
                            news_links.append(link)
                except:
                    continue
            
            elements = news_links[:50]  # 상위 50개만 체크 (키워드 필터링을 위해 더 많이)
            print(f"뉴스 링크 {len(elements)}개 필터링")
        
        # 키워드 매칭된 뉴스와 관련성 점수 저장
        scored_news = []
        
        for element in elements:
            try:
                # 제목 추출
                title = element.get_text(strip=True)
                if not title:
                    continue
                
                # URL 추출
                href = element.get('href')
                if not href:
                    continue
                
                # href를 문자열로 변환
                href_str = str(href)
                if not href_str:
                    continue
                
                # 절대 URL 생성
                if href_str.startswith('/'):
                    url = urljoin(self.base_url, href_str)
                elif href_str.startswith('http'):
                    url = href_str
                else:
                    continue
                
                # 광고성 콘텐츠 필터링
                if self.is_ad_content(title, url):
                    continue
                
                # 키워드 매칭 확인
                if not self.matches_keywords(title, url):
                    continue
                
                # 중복 제거
                if any(item['url'] == url for item in scored_news):
                    continue
                
                # 관련성 점수 계산
                relevance_score = self.calculate_relevance_score(title, url)
                
                # 키워드 추출
                keywords = self.extract_keywords(title)
                
                news_item = {
                    'title': title,
                    'url': url,
                    'keywords': keywords,
                    'relevance_score': relevance_score
                }
                
                scored_news.append(news_item)
                    
            except Exception as e:
                print(f"뉴스 항목 처리 중 오류: {e}")
                continue
        
        # 관련성 점수 기준으로 정렬 (높은 점수부터)
        scored_news.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # 관련성 점수 제거하고 최대 개수만큼 반환
        news_items = []
        for item in scored_news[:self.max_news]:
            del item['relevance_score']
            news_items.append(item)
        
        return news_items
    
    def extract_latest_news(self):
        """최신 뉴스 추출"""
        search_mode = "키워드 검색" if self.search_keywords else "최신 뉴스"
        keyword_text = " + ".join(self.search_keywords) if self.search_keywords else "없음"
        
        print(f"Yahoo Finance 뉴스 추출을 시작합니다...")
        print(f"모드: {search_mode}")
        print(f"키워드: {keyword_text}")
        print(f"추출 개수: {self.max_news}개")
        print(f"URL: {self.latest_news_url}")
        
        # 페이지 내용 가져오기
        html_content = self.get_page_content(self.latest_news_url)
        if not html_content:
            print("페이지 내용을 가져올 수 없습니다.")
            return []
        
        print(f"페이지 내용 길이: {len(html_content)} 문자")
        
        # 뉴스 추출
        news_items = self.extract_news_from_page(html_content)
        
        if not news_items and not self.search_keywords:
            print("뉴스를 찾을 수 없습니다. 다른 방법을 시도합니다...")
            # 메인 Finance 페이지에서 시도
            main_page_url = "https://finance.yahoo.com"
            html_content = self.get_page_content(main_page_url)
            if html_content:
                news_items = self.extract_news_from_page(html_content)
        
        if self.search_keywords and not news_items:
            print(f"'{' + '.join(self.search_keywords)}' 키워드와 관련된 뉴스를 찾을 수 없습니다.")
            print("키워드를 다르게 시도하거나 키워드 없이 최신 뉴스를 확인해보세요.")
        
        print(f"총 {len(news_items)}개의 뉴스를 추출했습니다.")
        return news_items
    
    def save_to_json(self, news_items, filename="yahoo_finance_news.json"):
        """결과를 JSON 파일로 저장"""
        data = {
            'extracted_at': datetime.now().isoformat(),
            'source': 'Yahoo Finance',
            'search_keywords': self.search_keywords,
            'max_news': self.max_news,
            'total_count': len(news_items),
            'news_items': news_items
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"결과가 '{filename}' 파일에 저장되었습니다.")
    
    def display_results(self, news_items):
        """결과 화면 출력"""
        if not news_items:
            if self.search_keywords:
                print(f"'{' + '.join(self.search_keywords)}' 키워드와 관련된 뉴스가 없습니다.")
            else:
                print("추출된 뉴스가 없습니다.")
            return
        
        print("\n" + "="*80)
        if self.search_keywords:
            print(f"'{' + '.join(self.search_keywords)}' 키워드 관련 뉴스 추출 결과")
        else:
            print("Yahoo Finance 최신 뉴스 추출 결과")
        print("="*80)
        
        for i, item in enumerate(news_items, 1):
            print(f"\n{i}. {item['title']}")
            print(f"   URL: {item['url']}")
            print(f"   주요 키워드: {', '.join(item['keywords']) if item['keywords'] else '없음'}")
            print("-" * 80)
    
    def run(self, output_filename="yahoo_finance_news.json"):
        """메인 실행 함수"""
        try:
            news_items = self.extract_latest_news()
            
            if news_items:
                self.display_results(news_items)
                self.save_to_json(news_items, output_filename)
            else:
                if self.search_keywords:
                    print(f"'{' + '.join(self.search_keywords)}' 키워드와 관련된 뉴스를 찾을 수 없습니다.")
                    print("다른 키워드로 시도하거나 키워드 없이 최신 뉴스를 확인해보세요.")
                else:
                    print("뉴스를 추출할 수 없습니다.")
                
        except Exception as e:
            print(f"실행 중 오류가 발생했습니다: {e}")

def parse_arguments():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(
        description='범용 뉴스 추출기 (Yahoo Finance + 기타 사이트)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python url_extractor.py                          # Yahoo Finance 최신 뉴스 10개 추출
  python url_extractor.py -k "Tesla AI"            # Yahoo Finance에서 Tesla AI 관련 뉴스 추출
  python url_extractor.py -n 20                    # Yahoo Finance 최신 뉴스 20개 추출
  python url_extractor.py -k "Bitcoin" -n 15       # Yahoo Finance에서 Bitcoin 관련 뉴스 15개 추출
  python url_extractor.py -u "https://finance.yahoo.com/topic/latest-news/" -n 5
                                                    # 특정 URL에서 뉴스 5개 추출
  python url_extractor.py -u "https://cnn.com" -k "technology" -n 10
                                                    # CNN에서 technology 관련 뉴스 10개 추출
        """
    )
    
    parser.add_argument(
        '-u', '--url',
        type=str,
        help='추출할 뉴스 사이트 URL (예: "https://finance.yahoo.com/topic/latest-news/")'
    )
    
    parser.add_argument(
        '-k', '--keyword',
        type=str,
        help='검색할 키워드 (예: "Tesla AI", "Bitcoin price")'
    )
    
    parser.add_argument(
        '-n', '--number',
        type=int,
        default=10,
        help='추출할 뉴스 개수 (기본값: 10)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='extracted_news.json',
        help='출력 파일명 (기본값: extracted_news.json)'
    )
    
    return parser.parse_args()

def main():
    """메인 함수"""
    args = parse_arguments()
    
    print("="*80)
    if args.url:
        print("           범용 뉴스 추출기")
        print("="*80)
        print(f"추출 URL: {args.url}")
        
        if args.keyword:
            print(f"검색 키워드: {args.keyword}")
            search_keywords = args.keyword
        else:
            print("모드: 전체 뉴스 추출")
            search_keywords = None
        
        print(f"추출 개수: {args.number}개")
        print(f"출력 파일: {args.output}")
        print("="*80)
        
        # UniversalNewsExtractor 사용
        extractor = UniversalNewsExtractor(
            base_url=args.url,
            search_keywords=search_keywords,
            max_news=args.number
        )
        
        try:
            news_items = extractor.extract_news()
            
            if news_items:
                # 결과 출력
                print("\n" + "="*80)
                if search_keywords:
                    print(f"'{search_keywords}' 키워드 관련 뉴스 추출 결과")
                else:
                    print("뉴스 추출 결과")
                print("="*80)
                
                for i, item in enumerate(news_items, 1):
                    print(f"\n{i}. {item['title']}")
                    print(f"   URL: {item['url']}")
                    print(f"   주요 키워드: {', '.join(item['keywords']) if item['keywords'] else '없음'}")
                    print("-" * 80)
                
                # JSON 파일로 저장
                data = {
                    'extracted_at': datetime.now().isoformat(),
                    'source': args.url,
                    'search_keywords': search_keywords,
                    'max_news': args.number,
                    'total_count': len(news_items),
                    'news_items': news_items
                }
                
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"\n결과가 '{args.output}' 파일에 저장되었습니다.")
                
            else:
                if search_keywords:
                    print(f"'{search_keywords}' 키워드와 관련된 뉴스를 찾을 수 없습니다.")
                else:
                    print("뉴스를 추출할 수 없습니다.")
        
        except Exception as e:
            print(f"실행 중 오류가 발생했습니다: {e}")
    
    else:
        # 기존 Yahoo Finance 추출기 사용
        print("           Yahoo Finance 뉴스 추출기")
        print("="*80)
        
        if args.keyword:
            print(f"검색 키워드: {args.keyword}")
            search_keywords = args.keyword
        else:
            print("모드: 최신 뉴스 추출")
            search_keywords = None
        
        print(f"추출 개수: {args.number}개")
        print(f"출력 파일: {args.output}")
        print("필터링: 광고성 콘텐츠 자동 제외")
        print("="*80)
        
        extractor = YahooFinanceNewsExtractor(
            search_keywords=search_keywords,
            max_news=args.number
        )
        extractor.run(args.output)

if __name__ == "__main__":
    main() 