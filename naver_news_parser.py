#!/usr/bin/env python3
"""
네이버 뉴스 전용 파서
기존 시스템에 영향을 주지 않는 독립적인 파서
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Optional, Any
import logging
from fake_useragent import UserAgent
import re
from urllib.parse import urljoin, urlparse

# 로깅 설정
logger = logging.getLogger(__name__)

class NaverNewsExtractor:
    """네이버 뉴스 전용 추출기"""
    
    def __init__(self, base_url: str, search_keywords: Optional[str] = None, max_news: int = 10):
        self.base_url = base_url
        self.search_keywords = search_keywords
        self.max_news = max_news
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # 네이버 뉴스 최적화 헤더
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 타임아웃 설정
        self.timeout = 15
        
        # 🚨 강화된 홍보성 뉴스 필터링 시스템
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
                'AD', 'Sponsored', '후원', '제휴',
            ],
            
            # URL 패턴 기반 홍보성 필터
            'url_patterns': [
                r'/ad/', r'/ads/', r'/advertisement/', r'/sponsored/',
                r'/promotion/', r'/promotional/', r'/event/', r'/events/',
                r'/contest/', r'/giveaway/', r'/sweepstakes/', r'/sale/',
                r'/deal/', r'/offer/', r'/special/', r'/limited/',
                r'/free/', r'/trial/', r'/sample/', r'/gift/',
                r'/subscribe/', r'/signup/', r'/register/', r'/join/',
                r'/membership/', r'/premium/', r'/vip/', r'/exclusive/',
                r'/press-release/', r'/announcement/', r'/launch/', r'/release/',
                r'/partnership/', r'/collaboration/', r'/sponsor/', r'/sponsored/',
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
            ],
            
            # 짧은 제목 필터 (홍보성 제목은 보통 짧음)
            'min_title_length': 15,
            
            # 과도한 특수문자 필터 (홍보성 제목에 자주 나타남)
            'excessive_symbols': [
                '!', '!!', '!!!', '?', '??', '???', '~', '~~', '~~~',
                '★', '☆', '♥', '♡', '♠', '♣', '♦', '●', '○', '◆', '◇',
                '▶', '◀', '▲', '▼', '■', '□', '▣', '▤', '▥', '▦', '▧', '▨', '▩',
            ]
        }
    
    def extract_news(self) -> List[Dict[str, Any]]:
        """뉴스 추출 메인 함수"""
        try:
            print(f"네이버 뉴스 추출 시작: {self.base_url}")
            
            # HTML 요청
            html_content = self._fetch_html()
            if not html_content:
                return []
            
            # 네이버 뉴스 링크 추출
            news_links = self._extract_naver_news_links(html_content)
            
            # 🚨 홍보성 뉴스 필터링 적용
            filtered_links = self._filter_promotional_content(news_links)
            
            # 뉴스 아이템 생성
            news_items = self._create_news_items(filtered_links)
            
            print(f"네이버 뉴스에서 {len(news_links)}개 뉴스 추출, 홍보성 필터링 후 {len(filtered_links)}개 유지")
            return news_items[:self.max_news]
            
        except Exception as e:
            logger.error(f"네이버 뉴스 추출 오류: {e}")
            return []
    
    def _filter_promotional_content(self, links: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """홍보성 콘텐츠 필터링"""
        filtered_links = []
        
        for link in links:
            title = link['title']
            url = link['url']
            
            # 홍보성 콘텐츠 체크
            if self._is_promotional_content(title, url):
                print(f"🚫 홍보성 뉴스 제외: {title[:50]}...")
                continue
            
            filtered_links.append(link)
        
        return filtered_links
    
    def _is_promotional_content(self, title: str, url: str) -> bool:
        """홍보성 콘텐츠인지 판단"""
        title_lower = title.lower()
        url_lower = url.lower()
        
        # 1. 제목 키워드 체크
        for keyword in self.promotional_patterns['title_keywords']:
            if keyword.lower() in title_lower:
                return True
        
        # 2. URL 패턴 체크
        for pattern in self.promotional_patterns['url_patterns']:
            if re.search(pattern, url_lower):
                return True
        
        # 3. 제목 패턴 체크 (대괄호, 소괄호 안의 홍보성 키워드)
        for pattern in self.promotional_patterns['title_patterns']:
            if re.search(pattern, title, re.IGNORECASE):
                return True
        
        # 4. 제목 길이 체크 (너무 짧으면 홍보성일 가능성)
        if len(title.strip()) < self.promotional_patterns['min_title_length']:
            return True
        
        # 5. 과도한 특수문자 체크
        symbol_count = sum(1 for symbol in self.promotional_patterns['excessive_symbols'] if symbol in title)
        if symbol_count >= 3:  # 3개 이상의 특수문자가 있으면 홍보성
            return True
        
        # 6. 반복되는 문자 체크 (예: "대박!!!", "최고!!!")
        if re.search(r'([!?~★☆♥♡])\1{2,}', title):
            return True
        
        # 7. 과도한 대문자 체크 (홍보성 제목은 대문자를 많이 사용)
        uppercase_ratio = sum(1 for char in title if char.isupper()) / len(title) if title else 0
        if uppercase_ratio > 0.7:  # 70% 이상이 대문자면 홍보성
            return True
        
        return False
    
    def _fetch_html(self) -> Optional[str]:
        """HTML 페이지 가져오기"""
        try:
            # 네이버 뉴스 전용 User-Agent
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://news.naver.com/',
            }
            
            response = self.session.get(self.base_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            print(f"[NAVER] 요청 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"[NAVER] 응답 상태: {response.status_code}")
            print(f"[NAVER] 응답 길이: {len(response.text):,} 문자")
            
            return response.text
            
        except Exception as e:
            logger.error(f"네이버 뉴스 HTML 가져오기 실패: {e}")
            return None
    
    def _extract_naver_news_links(self, html: str) -> List[Dict[str, str]]:
        """네이버 뉴스 전용 링크 추출"""
        soup = BeautifulSoup(html, 'html.parser')
        news_links = []
        
        # 네이버 뉴스 링크 패턴별 추출
        link_patterns = [
            # 랭킹 뉴스 페이지
            'a[href*="/main/ranking/"]',
            'a[href*="/read.naver"]',
            'a[href*="/article/"]',
            # 섹션 뉴스 페이지  
            'a[href*="/section/"]',
            # 팩트체크 페이지
            'a[href*="/factcheck/"]',
            # 일반 뉴스 링크
            'a.list_title',
            'a.news_tit',
            'a.cluster_text_headline',
            'a.sh_text_headline',
            # 추가 패턴
            '.list_body a',
            '.group_news a',
            '.news_area a',
        ]
        
        for pattern in link_patterns:
            if len(news_links) >= self.max_news * 2:  # 여유분 포함
                break
                
            try:
                links = soup.select(pattern)
                for link in links:
                    if len(news_links) >= self.max_news * 2:
                        break
                        
                    href = link.get('href')
                    text = link.get_text(strip=True)
                    
                    if (href and text and 
                        len(text) > 10 and  # 충분한 길이의 제목
                        self._is_valid_naver_news_link(str(href))):
                        
                        # 절대 URL로 변환
                        if href.startswith('/'):
                            full_url = f"https://news.naver.com{href}"
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            full_url = urljoin(self.base_url, href)
                        
                        news_links.append({
                            'url': full_url,
                            'title': text
                        })
                        
            except Exception as e:
                logger.error(f"패턴 {pattern} 처리 중 오류: {e}")
                continue
        
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
    
    def _is_valid_naver_news_link(self, url: str) -> bool:
        """유효한 네이버 뉴스 링크인지 확인"""
        # 네이버 뉴스 유효 패턴
        valid_patterns = [
            r'news\.naver\.com',
            r'/read\.naver',
            r'/article/',
            r'/main/ranking/',
            r'/section/',
            r'/factcheck/',
        ]
        
        # 제외할 패턴
        invalid_patterns = [
            r'/sports/',  # 스포츠 뉴스 (선택적)
            r'/entertainment/',  # 연예 뉴스 (선택적)
            r'/comment/',  # 댓글 페이지
            r'/photo/',  # 포토 뉴스
            r'/video/',  # 비디오 뉴스
            r'javascript:',  # 자바스크립트 링크
            r'#',  # 앵커 링크
        ]
        
        # 유효 패턴 확인
        has_valid = any(re.search(pattern, url) for pattern in valid_patterns)
        if not has_valid:
            return False
            
        # 무효 패턴 확인
        has_invalid = any(re.search(pattern, url) for pattern in invalid_patterns)
        return not has_invalid
    
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
                'source_type': 'naver_news',  # 네이버 뉴스 식별자
            }
            
            news_items.append(news_item)
        
        return news_items
    
    def _extract_keywords(self, title: str) -> List[str]:
        """제목에서 키워드 추출"""
        keywords = []
        
        # 한국어 키워드 패턴
        korean_patterns = [
            r'[가-힣]{2,}(?:그룹|회사|기업|코퍼레이션)',  # 회사명
            r'[가-힣]{2,}(?:은행|증권|생명|화재|카드)',  # 금융사
            r'(?:삼성|현대|LG|SK|롯데|신세계|CJ|한화)',  # 대기업
            r'(?:정부|청와대|국회|법원|검찰|경찰)',  # 정부기관
            r'(?:코스피|코스닥|나스닥|다우|S&P)',  # 주식시장
        ]
        
        for pattern in korean_patterns:
            matches = re.findall(pattern, title)
            keywords.extend(matches[:2])
        
        # 영어 키워드 패턴
        english_patterns = [
            r'\b[A-Z][A-Z0-9]{2,}\b',  # 대문자 약어 (AAPL, TSLA 등)
            r'\b(?:AI|IoT|5G|6G|VR|AR|NFT|DeFi|FinTech)\b',  # 기술 키워드
        ]
        
        for pattern in english_patterns:
            matches = re.findall(pattern, title)
            keywords.extend(matches[:2])
        
        return list(set(keywords))[:5]  # 중복 제거 후 최대 5개


def test_naver_extractor():
    """네이버 뉴스 추출기 테스트"""
    test_urls = [
        'https://news.naver.com/main/ranking/popularDay.naver',
        'https://news.naver.com/section/101',  # 경제
        'https://news.naver.com/factcheck/main',
    ]
    
    for url in test_urls:
        print(f"\n=== 테스트: {url} ===")
        extractor = NaverNewsExtractor(url, max_news=3)
        news = extractor.extract_news()
        
        for item in news:
            print(f"제목: {item['title']}")
            print(f"URL: {item['url']}")
            print(f"키워드: {item['keywords']}")
            print("---")


if __name__ == "__main__":
    test_naver_extractor() 