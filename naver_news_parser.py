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
        
    def extract_news(self) -> List[Dict[str, Any]]:
        """네이버 뉴스 추출 메인 함수"""
        try:
            print(f"뉴스 추출 시작: {self.base_url}")
            
            # HTML 가져오기
            html_content = self._fetch_html()
            if not html_content:
                return []
            
            # 네이버 뉴스 링크 추출
            news_links = self._extract_naver_news_links(html_content)
            
            # 뉴스 아이템 생성
            news_items = self._create_news_items(news_links)
            
            print(f"HTML 파싱에서 {len(news_items)}개 뉴스 추출 완료")
            return news_items[:self.max_news]
            
        except Exception as e:
            logger.error(f"네이버 뉴스 추출 오류: {e}")
            return []
    
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
                        self._is_valid_naver_news_link(str(href)) and
                        not self._is_spam_content(text)):
                        
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
                logger.debug(f"패턴 {pattern} 처리 중 오류: {e}")
                continue
        
        # 중복 제거 (URL 기준)
        seen_urls = set()
        unique_links = []
        for link in news_links:
            if link['url'] not in seen_urls:
                seen_urls.add(link['url'])
                unique_links.append(link)
                
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
    
    def _is_spam_content(self, text: str) -> bool:
        """스팸 콘텐츠인지 확인"""
        spam_keywords = [
            '광고', '프로모션', '바로가기', '더보기', '전체보기',
            '구독', '팔로우', '로그인', '회원가입', '댓글',
            'AD', 'Sponsored', '후원', '제휴',
        ]
        
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in spam_keywords)
    
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