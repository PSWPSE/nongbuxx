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
            
            # URL 패턴 기반 홍보성 필터
            'url_patterns': [
                r'/ad/', r'/ads/', r'/advertisement/', r'/sponsored/',
                r'/promotion/', r'/promotional/', r'/event/', r'/events/',
                r'/contest/', r'/giveaway/', r'/sweepstakes/', r'/sale/',
                r'/deal/', r'/offer/', r'/special/', r'/limited/',
                r'/free/', r'/trial/', r'/sample/', r'/gift/',
                r'/subscribe/', r'/signup/', r'/register/', r'/join/',
                r'/membership/', r'/premium/', r'/vip', r'/exclusive/',
                r'/press-release/', r'/announcement/', r'/launch/', r'/release/',
                r'/partnership/', r'/collaboration/', r'/sponsor/', r'/sponsored/',
                
                # 🚨 ETF 및 투자 상품 관련 URL 패턴 추가
                r'/etf/', r'/etfs/', r'/fund/', r'/funds/', r'/investment-product/',
                r'/product/', r'/products/', r'/investment/', r'/investing/',
                r'/portfolio/', r'/strategy/', r'/analysis/', r'/research/',
                
                # 🚨 주식 추천 및 투자 제안 관련 URL 패턴 추가
                r'/recommendation/', r'/recommendations/', r'/pick/', r'/picks/',
                r'/advice/', r'/suggestion/', r'/timing/', r'/opportunity/',
                r'/buy/', r'/sell/', r'/trade/', r'/trading/',
                r'/stock-pick/', r'/stock-recommendation/', r'/investment-advice/',
                r'/market-timing/', r'/investment-timing/',
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
                r'.*etf.*투자.*가치.*', r'.*etf.*투자.*포인트.*', r'.*etf.*투자.*고려사항.*',
                r'.*etf.*투자.*검토.*', r'.*etf.*투자.*평가.*', r'.*etf.*투자.*전망.*',
                
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
        
        # 1. 제목 키워드 체크 (더 정교한 판단)
        promotional_keywords = 0
        for keyword in self.promotional_patterns['title_keywords']:
            if keyword.lower() in title_lower:
                promotional_keywords += 1
        
        # 키워드가 2개 이상일 때만 홍보성으로 판단 (단일 키워드는 허용)
        if promotional_keywords >= 2:
            return True
        
        # 2. URL 패턴 체크
        for pattern in self.promotional_patterns['url_patterns']:
            if re.search(pattern, url_lower):
                return True
        
        # 3. 제목 패턴 체크 (대괄호, 소괄호 안의 홍보성 키워드)
        for pattern in self.promotional_patterns['title_patterns']:
            if re.search(pattern, title, re.IGNORECASE):
                return True
        
        # 4. 🚨 ETF 홍보성 콘텐츠 특별 체크 (더 정확한 판단)
        if self._is_etf_promotional_content(title):
            return True
        
        # 5. 제목 길이 체크 (너무 짧으면 홍보성일 가능성)
        if len(title.strip()) < self.promotional_patterns['min_title_length']:
            return True
        
        # 6. 과도한 특수문자 체크
        symbol_count = sum(1 for symbol in self.promotional_patterns['excessive_symbols'] if symbol in title)
        if symbol_count >= 3:  # 3개 이상의 특수문자가 있으면 홍보성
            return True
        
        # 7. 반복되는 문자 체크 (예: "대박!!!", "최고!!!")
        if re.search(r'([!?~★☆♥♡])\1{2,}', title):
            return True
        
        # 8. 과도한 대문자 체크 (홍보성 제목은 대문자를 많이 사용)
        uppercase_ratio = sum(1 for char in title if char.isupper()) / len(title) if title else 0
        if uppercase_ratio > 0.7:  # 70% 이상이 대문자면 홍보성
            return True
        
        # 9. 🚨 정상적인 뉴스 패턴 체크 (포함되어야 함)
        if self._is_normal_news_content(title):
            return False
        
        return False
    
    def _is_normal_news_content(self, title: str) -> bool:
        """정상적인 뉴스 콘텐츠인지 판단"""
        title_lower = title.lower()
        
        # 정상적인 뉴스 패턴들
        normal_news_patterns = [
            # 기업 관련
            r'.*기업.*실적.*',
            r'.*기업.*성과.*',
            r'.*기업.*전략.*',
            r'.*기업.*발표.*',
            r'.*기업.*출시.*',
            r'.*기업.*진출.*',
            r'.*기업.*투자.*',
            r'.*기업.*인수.*',
            r'.*기업.*합병.*',
            
            # 시장 관련
            r'.*시장.*동향.*',
            r'.*시장.*분석.*',
            r'.*시장.*전망.*',
            r'.*시장.*변화.*',
            r'.*시장.*성장.*',
            r'.*시장.*규모.*',
            
            # 경제 관련
            r'.*경제.*정책.*',
            r'.*경제.*지표.*',
            r'.*경제.*성장.*',
            r'.*경제.*전망.*',
            
            # 기술 관련
            r'.*기술.*개발.*',
            r'.*기술.*혁신.*',
            r'.*기술.*트렌드.*',
            r'.*기술.*동향.*',
            
            # 주식/투자 관련 (정상적인 뉴스)
            r'.*주가.*상승.*',
            r'.*주가.*하락.*',
            r'.*주가.*변동.*',
            r'.*투자.*동향.*',
            r'.*투자.*환경.*',
            r'.*투자.*시장.*',
        ]
        
        # 정상적인 뉴스 패턴 확인
        for pattern in normal_news_patterns:
            if re.search(pattern, title_lower):
                return True
        
        return False
    
    def _is_etf_promotional_content(self, title: str) -> bool:
        """ETF 홍보성 콘텐츠인지 더 정확하게 판단"""
        title_lower = title.lower()
        
        # 🚨 명확한 ETF 홍보성 패턴들 (의문형, 추천형, 소개형)
        etf_promotional_patterns = [
            # 의문형 패턴 (투자 결정을 요구하는 형태)
            r'.*etf.*투자.*레이더.*올려야.*할까\?',
            r'.*etf.*투자.*가치.*있을까\?',
            r'.*etf.*투자.*기회.*할까\?',
            r'.*etf.*투자.*추천.*할까\?',
            
            # 소개/추천형 패턴
            r'.*etf.*소개.*',
            r'.*etf.*추천.*',
            r'.*etf.*투자.*전략.*',
            
            # 투자 레이더 관련 (명확한 홍보성)
            r'.*투자.*레이더.*',
            r'.*투자.*기회.*',
            r'.*투자.*가치.*',
            r'.*투자.*포인트.*',
            r'.*투자.*고려사항.*',
            r'.*투자.*검토.*',
            r'.*투자.*평가.*',
            r'.*투자.*전망.*',
        ]
        
        # 🚨 주식 추천 및 투자 제안 패턴들 추가
        stock_promotional_patterns = [
            # 의문형 패턴 (투자 결정을 요구하는 형태)
            r'.*주식.*어떄\?.*',
            r'.*주식.*투자.*할까\?.*',
            r'.*투자.*적기.*',
            r'.*투자.*타이밍.*',
            r'.*매수.*시점.*',
            r'.*매도.*시점.*',
            r'.*매수.*타이밍.*',
            r'.*매도.*타이밍.*',
            
            # 추천/제안형 패턴
            r'.*주식.*추천.*',
            r'.*주식.*매수.*',
            r'.*주식.*매도.*',
            r'.*투자.*제안.*',
            r'.*투자.*추천.*',
            r'.*주가.*전망.*',
            r'.*주가.*예측.*',
            r'.*주가.*분석.*',
            r'.*주가.*추천.*',
            r'.*종목.*추천.*',
            r'.*종목.*분석.*',
            r'.*종목.*전망.*',
            r'.*종목.*투자.*',
        ]
        
        # 🚨 정상적인 ETF 뉴스 패턴들 (포함되어야 함)
        etf_normal_patterns = [
            r'.*etf.*시장.*동향.*',
            r'.*etf.*성과.*분석.*',
            r'.*etf.*수익률.*',
            r'.*etf.*자산.*규모.*',
            r'.*etf.*상장.*',
            r'.*etf.*폐지.*',
            r'.*etf.*운용사.*',
            r'.*etf.*투자자.*',
        ]
        
        # 🚨 정상적인 주식 뉴스 패턴들 (포함되어야 함)
        stock_normal_patterns = [
            r'.*주가.*상승.*',
            r'.*주가.*하락.*',
            r'.*주가.*변동.*',
            r'.*주가.*동향.*',
            r'.*주가.*성과.*',
            r'.*주가.*실적.*',
            r'.*주가.*발표.*',
            r'.*주가.*시장.*',
            r'.*종목.*시장.*',
            r'.*종목.*동향.*',
            r'.*종목.*성과.*',
            r'.*종목.*실적.*',
        ]
        
        # 정상적인 ETF 뉴스인지 먼저 확인
        for pattern in etf_normal_patterns:
            if re.search(pattern, title_lower):
                return False  # 정상적인 ETF 뉴스는 홍보성 아님
        
        # 정상적인 주식 뉴스인지 먼저 확인
        for pattern in stock_normal_patterns:
            if re.search(pattern, title_lower):
                return False  # 정상적인 주식 뉴스는 홍보성 아님
        
        # ETF 홍보성 패턴 확인
        for pattern in etf_promotional_patterns:
            if re.search(pattern, title_lower):
                return True
        
        # 주식 홍보성 패턴 확인
        for pattern in stock_promotional_patterns:
            if re.search(pattern, title_lower):
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