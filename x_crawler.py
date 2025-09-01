"""
X 크롤러 백엔드 서비스
인플루언서 포스트 수집 및 AI 요약 생성
"""

import json
import logging
import os
import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pytz
import tweepy
from openai import OpenAI
import anthropic

# 로거 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('x_crawler')

# 한국 시간대
KST = pytz.timezone('Asia/Seoul')


class XCrawler:
    """X 크롤러 메인 클래스"""
    
    def __init__(self):
        """초기화"""
        self.x_client = None
        self.ai_client = None
        self.ai_provider = None
        self.influencers = []
        self.collected_posts = []
        self.collection_history = []  # 수집 기록
        self.publish_history = []  # 게시 기록
        self.api_usage = {  # API 사용량
            'x_api': {'calls': 0, 'last_reset': datetime.now(KST)},
            'ai_api': {'tokens': 0, 'calls': 0}
        }
        
        # 캐싱 추가
        self.user_cache = {}  # 사용자 정보 캐시
        self.cache_ttl = 21600  # 6시간 캐시 (수집 주기와 동일)
        self.last_collection_time = 0  # 마지막 수집 시간
        self.min_collection_interval = 21600  # 최소 6시간 간격 (6 * 60 * 60)
        
        logger.info("✅ X 크롤러 초기화")
    
    def setup_x_api(self, credentials: Dict[str, str]) -> bool:
        """X API 설정 - Free Tier 최적화"""
        try:
            # OAuth 1.0a 설정 (Free Tier에서 주로 사용)
            auth = tweepy.OAuthHandler(
                credentials.get('consumer_key'),
                credentials.get('consumer_secret')
            )
            auth.set_access_token(
                credentials.get('access_token'),
                credentials.get('access_token_secret')
            )
            
            # v1.1 API (Free Tier에서 사용 가능)
            self.x_api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
            
            # v2 Client 설정 (Free Tier에서 제한적)
            # OAuth 1.0a User Context 사용
            self.x_client = tweepy.Client(
                consumer_key=credentials.get('consumer_key'),
                consumer_secret=credentials.get('consumer_secret'),
                access_token=credentials.get('access_token'),
                access_token_secret=credentials.get('access_token_secret'),
                wait_on_rate_limit=True
            )
            
            # 인증 테스트 (Free Tier에서 가능)
            user = self.x_api_v1.verify_credentials()
            logger.info(f"✅ X API 인증 성공: @{user.screen_name}")
            logger.info("⚠️ Free Tier 제한: 트윗 수집 불가, 게시만 가능")
            return True
            
        except Exception as e:
            logger.error(f"❌ X API 설정 실패: {str(e)}")
            return False
    
    def setup_ai_api(self, config):
        """AI API 설정 - dict 형태로 받기"""
        try:
            # dict로 받은 경우
            if isinstance(config, dict):
                provider = config.get('provider')
                api_key = config.get('api_key')
            # 실수로 두 개의 인자로 받은 경우 (backward compatibility)
            else:
                provider = config
                api_key = None
                
            if not provider or not api_key:
                logger.warning("⚠️ AI API 설정 정보 부족")
                return False
                
            if provider == 'openai':
                self.ai_client = OpenAI(api_key=api_key)
                self.ai_provider = 'openai'
            elif provider == 'anthropic':
                self.ai_client = anthropic.Anthropic(api_key=api_key)
                self.ai_provider = 'anthropic'
            elif provider == 'perplexity':
                # Perplexity API는 requests로 직접 호출
                self.ai_client = None
                self.ai_provider = 'perplexity'
                self.perplexity_api_key = api_key
            else:
                raise ValueError(f"지원하지 않는 AI 제공자: {provider}")
            
            logger.info(f"✅ {provider} AI API 설정 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ AI API 설정 실패: {str(e)}")
            return False
    
    async def fetch_influencer_posts(
        self,
        username: str,
        count: int = 30,  # 트윗 30개로 설정
        since_hours: int = 24
    ) -> List[Dict]:
        """인플루언서 최신 포스트 수집 (최적화됨)"""
        # 수집 간격 체크
        current_time = time.time()
        if self.last_collection_time > 0:
            elapsed = current_time - self.last_collection_time
            if elapsed < self.min_collection_interval:
                remaining = int((self.min_collection_interval - elapsed) / 60)
                logger.warning(f"⏳ 수집 간격 제한: {remaining}분 후 재시도 가능")
                return []
        
        try:
            if not self.x_client:
                logger.error("❌ X API 클라이언트가 설정되지 않았습니다")
                return []
            
            # @ 제거
            username = username.replace('@', '')
            
            logger.info(f"📥 {username} 포스트 수집 시작")
            
            # 시간 필터
            since_time = datetime.now(KST) - timedelta(hours=since_hours)
            
            # 캐시된 사용자 정보 확인
            cache_key = f"user_{username}"
            user_id = None
            
            if cache_key in self.user_cache:
                cached = self.user_cache[cache_key]
                if current_time - cached['timestamp'] < self.cache_ttl:
                    user_id = cached['user_id']
                    logger.info(f"📦 캐시된 사용자 정보 사용: @{username}")
            
            # Free Tier는 대부분의 API에 제한이 있음
            # 더미 데이터로 테스트 (실제 API 호출 대신)
            tweets = []
            
            # Free Tier 제한 안내
            logger.warning(f"⚠️ X API Free Tier는 타임라인 및 검색 API 접근이 제한됩니다.")
            logger.warning(f"⚠️ Basic Tier ($100/월) 이상이 필요합니다.")
            
            # 테스트용 샘플 데이터 생성
            if username.lower() in ['nongbudaddy', 'elonmusk', 'test']:
                # 테스트용 샘플 트윗 생성
                sample_tweets = [
                    {
                        'id': f'sample_{datetime.now().timestamp():.0f}_1',
                        'author': username,
                        'text': f"[테스트] {username}의 최신 트윗입니다. Free Tier에서는 실제 트윗을 가져올 수 없습니다. #테스트 #XCrawler",
                        'created_at': datetime.now(KST).isoformat(),
                        'likes': 10,
                        'retweets': 5,
                        'url': f'https://twitter.com/{username}/status/sample1',
                        'engagement': 15
                    },
                    {
                        'id': f'sample_{datetime.now().timestamp():.0f}_2',
                        'author': username,
                        'text': f"[테스트] Basic Tier로 업그레이드하면 실제 트윗 수집이 가능합니다. #XAPI #업그레이드",
                        'created_at': (datetime.now(KST) - timedelta(hours=1)).isoformat(),
                        'likes': 20,
                        'retweets': 10,
                        'url': f'https://twitter.com/{username}/status/sample2',
                        'engagement': 30
                    }
                ]
                tweets = sample_tweets
                logger.info(f"📋 테스트 데이터 생성: @{username} - {len(tweets)}개")
                logger.info(f"✅ {username}: {len(tweets)}개 포스트 수집 완료")
            else:
                logger.warning(f"⚠️ '{username}'은 테스트 계정이 아닙니다. Free Tier에서는 실제 수집이 불가능합니다.")
                tweets = []
                
        except tweepy.errors.TooManyRequests as e:
            logger.warning(f"⚠️ Rate limit 도달 - {username}: {str(e)}")
            self.collection_history.append({
                'timestamp': datetime.now(KST).isoformat(),
                'influencer': username,
                'posts_count': 0,
                'success': False,
                'error': 'Rate limit exceeded'
            })
            return []
        except Exception as e:
            logger.error(f"❌ 트윗 수집 오류 - {username}: {str(e)}")
            return []
            
            # 수집 시간 업데이트
            self.last_collection_time = current_time
            
            # API 사용량 업데이트 (타임라인 조회)
            self.api_usage['x_api']['calls'] += 1
            self.api_usage['x_api']['timeline_calls'] = self.api_usage['x_api'].get('timeline_calls', [])
            self.api_usage['x_api']['timeline_calls'].append({
                'timestamp': datetime.now(KST).isoformat(),
                'username': username,
                'count': len(tweets)
            })
            
            # 수집 기록 저장
            if tweets:
                self.collection_history.append({
                    'timestamp': datetime.now(KST).isoformat(),
                    'influencer': username,
                    'posts_count': len(tweets),
                    'success': True
                })
            
            return tweets
            
        except Exception as e:
            logger.error(f"❌ 예상치 못한 오류: {str(e)}")
            return []
    
    async def collect_all_influencers(
        self, 
        influencers: List[str]
    ) -> List[Dict]:
        """모든 인플루언서 포스트 수집"""
        all_posts = []
        
        for influencer in influencers:
            posts = await self.fetch_influencer_posts(influencer)
            all_posts.extend(posts)
            
            # Rate limit 고려한 지연
            await asyncio.sleep(2)
        
        # 시간순 정렬
        all_posts.sort(key=lambda x: x['created_at'], reverse=True)
        
        logger.info(f"📊 총 {len(all_posts)}개 포스트 수집 완료")
        return all_posts
    
    async def generate_summary(
        self, 
        posts: List[Dict],
        max_length: int = 280
    ) -> Dict:
        """AI를 이용한 포스트 요약 생성"""
        try:
            if not posts:
                return {
                    'summary': "",
                    'hashtags': [],
                    'error': "요약할 포스트가 없습니다"
                }
            
            if not self.ai_provider or (not self.ai_client and self.ai_provider != 'perplexity'):
                logger.warning("⚠️ AI API가 설정되지 않았습니다")
                return {
                    'summary': f"📊 {len(posts)}개 포스트 수집 완료 (AI 요약 미설정)",
                    'hashtags': [],
                    'posts_count': len(posts)
                }
            
            # 인기도 순으로 정렬 후 상위 10개 선택
            posts_to_summarize = sorted(
                posts, 
                key=lambda x: x.get('engagement', x.get('likes', 0) + x.get('retweets', 0)), 
                reverse=True
            )[:10]
            
            # 포스트 텍스트 결합 (리포스팅 정보 포함)
            combined_text_parts = []
            for post in posts_to_summarize:
                post_info = f"@{post['author']} (❤️{post.get('likes', 0)} 🔁{post.get('retweets', 0)}):\n{post['text'][:200]}"
                
                # 리포스팅인 경우 원문 정보 추가
                if post.get('is_repost', False):
                    original_author = post.get('original_author', '')
                    original_content = post.get('original_content', '')
                    if original_author and original_content:
                        post_info += f"\n[참조 원문] @{original_author}: {original_content[:150]}"
                
                combined_text_parts.append(post_info)
            
            combined_text = "\n\n".join(combined_text_parts)
            
            # 새로운 포맷팅 스타일
            from datetime import datetime
            import pytz
            
            KST = pytz.timezone('Asia/Seoul')
            
            # 인플루언서별로 그룹화
            posts_by_author = {}
            for post in posts_to_summarize:
                author = post.get('author', 'unknown')
                if author not in posts_by_author:
                    posts_by_author[author] = []
                posts_by_author[author].append(post)
            
            # 포맷팅된 텍스트 생성 (리포스팅 지원)
            formatted_posts = []
            
            for author, author_posts in posts_by_author.items():
                formatted_posts.append(f"@{author}의 포스트:")
                for post in author_posts[:5]:  # 작성자당 최대 5개
                    # 리포스팅인 경우 특별 처리
                    if post.get('is_repost', False):
                        formatted_posts.append(f"💬 인플루언서 코멘트: \"{post['text'][:150]}...\"")
                        created_at = post.get('created_at', '')
                        if created_at:
                            try:
                                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                dt_kst = dt.astimezone(KST)
                                formatted_posts.append(f"   -{dt_kst.strftime('%Y.%m.%d (%a) %H:%M')}")
                            except:
                                formatted_posts.append(f"   -시간 정보 없음")
                        
                        # 원문 정보 추가
                        original_author = post.get('original_author', '')
                        original_content = post.get('original_content', '')
                        original_datetime = post.get('original_datetime', '')
                        
                        if original_author and original_content:
                            formatted_posts.append(f"📰 참조한 포스팅: @{original_author}의 포스팅")
                            formatted_posts.append(f"   \"{original_content[:150]}...\"")
                            if original_datetime:
                                try:
                                    dt = datetime.fromisoformat(original_datetime.replace('Z', '+00:00'))
                                    dt_kst = dt.astimezone(KST)
                                    formatted_posts.append(f"   -{dt_kst.strftime('%Y.%m.%d (%a) %H:%M')}")
                                except:
                                    formatted_posts.append(f"   -원문 시간 정보 없음")
                    else:
                        # 일반 포스팅
                        formatted_posts.append(f"▶ \"{post['text'][:150]}...\"")
                        created_at = post.get('created_at', '')
                        if created_at:
                            try:
                                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                dt_kst = dt.astimezone(KST)
                                formatted_posts.append(f"   -{dt_kst.strftime('%Y.%m.%d (%a) %H:%M')}")
                            except:
                                formatted_posts.append(f"   -시간 정보 없음")
                    
                    formatted_posts.append("------------------------------------")
                formatted_posts.append("")
            
            combined_text = "\n".join(formatted_posts)
            
            prompt = f"""다음 X(트위터) 포스트들을 아래 형식으로 요약해주세요:

[수집된 포스트]
{combined_text}

[요구 포맷]
📱 오늘의 @인플루언서명 의 게시글 모음  

💬 "인플루언서 포스팅 내용 인용문"
-2025.09.02 (화) 10:30

📰 참조한 포스팅 : @참조원문작성자명 의 포스팅
"참조한 포스팅의 원문 내용 인용문"
-2025.09.02 (화) 08:30

------------------------------------

💬 "다음 인플루언서 포스팅 내용"
-2025.09.02 (화) 15:20

📰 참조한 포스팅 : @참조원문작성자명 의 포스팅
"참조한 포스팅의 원문 내용 인용문"
-2025.09.02 (화) 14:00

------------------------------------

[작성 원칙]
1. 제목 앞에 적절한 알림 이모지 1개 추가 (📱, 📊, 💰, 🔥, 📈 등 내용에 맞게)
2. 리포스팅인 경우: 💬 인플루언서 코멘트 → 📰 참조 원문 순서로 작성
3. 일반 포스팅인 경우: 💬 "포스팅 내용" 형태로만 작성
4. 각 포스팅 사이에 구분선(------------------------------------) 추가
5. 인용문은 구어체로 자연스럽게 한국어 번역
6. 시간은 한국 시간(KST) 기준으로 정확히 표시
7. 링크는 포함하지 않음
8. 해시태그는 포함하지 않음"""
            
            if self.ai_provider == 'openai':
                response = self.ai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "당신은 소셜 미디어 트렌드 분석 전문가입니다. 주어진 포맷에 맞춰 정확히 작성하고, 구어체로 자연스럽게 번역합니다."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                ai_response = response.choices[0].message.content
                
            elif self.ai_provider == 'anthropic':
                response = self.ai_client.messages.create(
                    model="claude-3-5-haiku-20241022",
                    max_tokens=500,
                    temperature=0.7,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                ai_response = response.content[0].text
                
            elif self.ai_provider == 'perplexity':
                import requests
                headers = {
                    'Authorization': f'Bearer {self.perplexity_api_key}',
                    'Content-Type': 'application/json'
                }
                data = {
                    'model': 'llama-3.1-sonar-large-128k-chat',
                    'messages': [
                        {"role": "system", "content": "당신은 소셜 미디어 트렌드 분석 전문가입니다. 주어진 포맷에 맞춰 정확히 작성하고, 구어체로 자연스럽게 번역합니다."},
                        {"role": "user", "content": prompt}
                    ],
                    'max_tokens': 500,
                    'temperature': 0.7
                }
                response = requests.post(
                    'https://api.perplexity.ai/chat/completions',
                    headers=headers,
                    json=data,
                    timeout=60
                )
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result['choices'][0]['message']['content']
                else:
                    logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                    raise Exception(f"Perplexity API error: {response.status_code}")
            
            else:
                return {
                    'summary': f"📱 오늘의 테크 리더 인사이트\n\n{len(posts)}개 포스트 수집됨",
                    'hashtags': ['#X트렌드', '#AI요약', '#인플루언서'],
                    'posts_count': len(posts)
                }
            
            # 새로운 포맷 응답 파싱
            lines = ai_response.strip().split('\n')
            summary = ai_response  # 전체 응답을 요약으로 사용
            
            # 긍정/부정 키워드 추출
            positive_keywords = []
            negative_keywords = []
            hashtags = []
            
            for line in lines:
                if '긍정 키워드:' in line:
                    keyword_text = line.split('긍정 키워드:')[1].strip()
                    positive_keywords = [tag.strip() for tag in keyword_text.split() if tag.startswith('#')]
                elif '부정 키워드:' in line:
                    keyword_text = line.split('부정 키워드:')[1].strip()
                    negative_keywords = [tag.strip() for tag in keyword_text.split() if tag.startswith('#')]
            
            # 모든 키워드를 해시태그로 결합
            hashtags = positive_keywords + negative_keywords
            
            # 기본값 처리
            if not hashtags:
                hashtags = ['#X트렌드', '#AI요약', '#인플루언서', '#소셜미디어', '#트렌드분석']
            
            logger.info(f"✅ AI 요약 생성 완료 ({len(summary)}자, 해시태그 {len(hashtags)}개)")
            
            return {
                'summary': summary,
                'hashtags': hashtags,
                'posts_count': len(posts),
                'analyzed_count': len(posts_to_summarize)
            }
            
        except Exception as e:
            logger.error(f"❌ 요약 생성 실패: {str(e)}")
            return {
                'summary': f"📱 오늘의 인사이트: {len(posts)}개 포스트",
                'hashtags': [],
                'error': str(e)
            }
    
    async def create_summary_content(
        self, 
        posts: List[Dict]
    ) -> Dict:
        """요약 콘텐츠 생성"""
        # 인플루언서별 그룹화
        by_author = {}
        for post in posts:
            author = post['author']
            if author not in by_author:
                by_author[author] = []
            by_author[author].append(post)
        
        # 요약 생성
        summary_text = await self.generate_summary(posts)
        
        # 해시태그 생성
        hashtags = self.generate_hashtags(posts)
        
        # 최종 콘텐츠
        content = {
            'id': f'summary_{datetime.now(KST).strftime("%Y%m%d_%H%M%S")}',
            'text': summary_text,
            'hashtags': hashtags,
            'posts_count': len(posts),
            'influencers': list(by_author.keys()),
            'created_at': datetime.now(KST).isoformat(),
            'metadata': {
                'top_post': max(posts, key=lambda x: x['likes'] + x['retweets']) if posts else None
            }
        }
        
        return content
    
    def generate_hashtags(self, posts: List[Dict]) -> List[str]:
        """해시태그 생성"""
        # 간단한 해시태그 생성 로직
        hashtags = ['#테크뉴스', '#AI', '#혁신']
        
        # 인플루언서 기반 해시태그
        authors = list(set(post['author'] for post in posts))
        for author in authors[:3]:  # 최대 3명
            if 'elon' in author.lower():
                hashtags.append('#일론머스크')
            elif 'sundar' in author.lower():
                hashtags.append('#구글')
        
        return hashtags[:5]  # 최대 5개
    
    async def post_to_x(self, content: Dict) -> Dict:
        """X에 게시"""
        try:
            if not self.x_client:
                logger.error("❌ X API 클라이언트가 설정되지 않았습니다")
                return {
                    'success': False,
                    'error': 'X API가 설정되지 않았습니다'
                }
            
            # 텍스트와 해시태그 결합
            full_text = content.get('text', content.get('summary', ''))
            if content.get('hashtags'):
                hashtags_text = ' '.join(content['hashtags'])
                # 280자 제한 고려
                if len(full_text) + len(hashtags_text) + 2 <= 280:
                    full_text = f"{full_text}\n\n{hashtags_text}"
                else:
                    # 본문을 줄이고 해시태그 유지
                    max_text_len = 280 - len(hashtags_text) - 5  # "\n\n" + "..."
                    full_text = f"{full_text[:max_text_len]}...\n\n{hashtags_text}"
            
            # 트윗 게시 (v1.1 API 사용)
            try:
                tweet = self.x_api_v1.update_status(full_text)
                
                logger.info(f"✅ X 게시 성공: {tweet.id_str}")
                
                # 게시 기록 저장
                self.publish_history.append({
                    'timestamp': datetime.now(KST).isoformat(),
                    'tweet_id': tweet.id_str,
                    'url': f'https://twitter.com/user/status/{tweet.id_str}',
                    'content': full_text,
                    'success': True
                })
                
                # API 사용량 업데이트
                self.api_usage['x_api']['calls'] += 1
                
                return {
                    'success': True,
                    'tweet_id': tweet.id_str,
                    'url': f'https://twitter.com/user/status/{tweet.id_str}',
                    'content': full_text,
                    'created_at': tweet.created_at.isoformat()
                }
                
            except tweepy.errors.Forbidden as e:
                logger.error(f"❌ 권한 오류: {str(e)}")
                return {
                    'success': False,
                    'error': '게시 권한이 없습니다. Write 권한이 있는 API 키를 확인해주세요.'
                }
            except tweepy.errors.TooManyRequests as e:
                logger.warning(f"⚠️ Rate limit 초과: {str(e)}")
                return {
                    'success': False,
                    'error': 'API 호출 한도를 초과했습니다. 잠시 후 다시 시도해주세요.',
                    'retry_after': 900  # 15분
                }
            except tweepy.errors.TweepyException as e:
                logger.error(f"❌ Tweepy 오류: {str(e)}")
                return {
                    'success': False,
                    'error': f'게시 실패: {str(e)}'
                }
            
        except Exception as e:
            logger.error(f"❌ X 게시 실패: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_stats(self) -> Dict:
        """통계 정보 (API 호출 상세 포함)"""
        # 최근 24시간 통계
        now = datetime.now(KST)
        last_24h = now - timedelta(hours=24)
        today = now.date()
        
        recent_collections = [
            h for h in self.collection_history 
            if datetime.fromisoformat(h['timestamp']) > last_24h
        ]
        
        recent_publishes = [
            h for h in self.publish_history
            if datetime.fromisoformat(h['timestamp']) > last_24h
        ]
        
        # API 호출 통계 계산
        user_calls_today = 0
        timeline_calls_today = 0
        user_calls_24h = 0
        timeline_calls_24h = 0
        
        # 사용자 정보 조회 통계
        for call in self.api_usage['x_api'].get('user_calls', []):
            call_time = datetime.fromisoformat(call['timestamp'])
            if call_time.date() == today:
                user_calls_today += 1
            if call_time > last_24h:
                user_calls_24h += 1
        
        # 타임라인 조회 통계
        for call in self.api_usage['x_api'].get('timeline_calls', []):
            call_time = datetime.fromisoformat(call['timestamp'])
            if call_time.date() == today:
                timeline_calls_today += 1
            if call_time > last_24h:
                timeline_calls_24h += 1
        
        return {
            'overview': {
                'total_collected': len(self.collected_posts),
                'total_published': len(self.publish_history),
                'influencers_count': len(self.influencers),
                'last_collection': self.collection_history[-1]['timestamp'] if self.collection_history else None,
                'last_publish': self.publish_history[-1]['timestamp'] if self.publish_history else None
            },
            'last_24h': {
                'collections': len(recent_collections),
                'publishes': len(recent_publishes),
                'success_rate': self._calculate_success_rate(recent_collections)
            },
            'api_calls': {
                'today': {
                    'user_lookups': user_calls_today,
                    'timeline_fetches': timeline_calls_today,
                    'total': user_calls_today + timeline_calls_today
                },
                'last_24h': {
                    'user_lookups': user_calls_24h,
                    'timeline_fetches': timeline_calls_24h,
                    'total': user_calls_24h + timeline_calls_24h
                },
                'all_time': {
                    'user_lookups': len(self.api_usage['x_api'].get('user_calls', [])),
                    'timeline_fetches': len(self.api_usage['x_api'].get('timeline_calls', [])),
                    'total': self.api_usage['x_api']['calls']
                }
            },
            'api_status': {
                'x_api': {
                    'connected': self.x_client is not None,
                    'calls_made': self.api_usage['x_api']['calls'],
                    'last_reset': self.api_usage['x_api']['last_reset'].isoformat()
                },
                'ai_api': {
                    'connected': self.ai_client is not None,
                    'calls_made': self.api_usage['ai_api']['calls'],
                    'tokens_used': self.api_usage['ai_api']['tokens']
                }
            },
            'recent_activity': {
                'collections': self.collection_history[-5:],  # 최근 5개
                'publishes': self.publish_history[-5:]  # 최근 5개
            }
        }
    
    def _calculate_success_rate(self, records):
        """성공률 계산"""
        if not records:
            return 100.0
        successful = sum(1 for r in records if r.get('success', False))
        return round((successful / len(records)) * 100, 1)


# 싱글톤 인스턴스
crawler_instance = None

def get_crawler() -> XCrawler:
    """크롤러 인스턴스 가져오기"""
    global crawler_instance
    if crawler_instance is None:
        crawler_instance = XCrawler()
    return crawler_instance


# 테스트 코드
if __name__ == "__main__":
    async def test():
        crawler = get_crawler()
        
        # API 설정 (실제 키 필요)
        # crawler.setup_x_api({...})
        # crawler.setup_ai_api('openai', 'sk-...')
        
        # 테스트용 더미 데이터
        test_posts = [
            {
                'id': '1',
                'author': 'elonmusk',
                'text': 'AI is the future',
                'created_at': datetime.now(KST).isoformat(),
                'likes': 1000,
                'retweets': 500,
                'url': 'https://twitter.com/test'
            }
        ]
        
        # 요약 생성 테스트
        content = await crawler.create_summary_content(test_posts)
        print(f"생성된 콘텐츠: {json.dumps(content, indent=2, ensure_ascii=False)}")
    
    asyncio.run(test())
