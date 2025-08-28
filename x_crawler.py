"""
X 크롤러 백엔드 서비스
인플루언서 포스트 수집 및 AI 요약 생성
"""

import json
import logging
import os
import asyncio
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
        self.influencers = []
        self.collected_posts = []
        
        logger.info("✅ X 크롤러 초기화")
    
    def setup_x_api(self, credentials: Dict[str, str]) -> bool:
        """X API 설정"""
        try:
            auth = tweepy.OAuthHandler(
                credentials.get('consumer_key'),
                credentials.get('consumer_secret')
            )
            auth.set_access_token(
                credentials.get('access_token'),
                credentials.get('access_token_secret')
            )
            
            self.x_client = tweepy.API(auth, wait_on_rate_limit=True)
            
            # 인증 테스트
            self.x_client.verify_credentials()
            logger.info("✅ X API 인증 성공")
            return True
            
        except Exception as e:
            logger.error(f"❌ X API 설정 실패: {str(e)}")
            return False
    
    def setup_ai_api(self, provider: str, api_key: str):
        """AI API 설정"""
        try:
            if provider == 'openai':
                self.ai_client = OpenAI(api_key=api_key)
                self.ai_provider = 'openai'
            elif provider == 'anthropic':
                self.ai_client = anthropic.Anthropic(api_key=api_key)
                self.ai_provider = 'anthropic'
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
        count: int = 10,
        since_hours: int = 24
    ) -> List[Dict]:
        """인플루언서 최신 포스트 수집"""
        try:
            # @ 제거
            username = username.replace('@', '')
            
            logger.info(f"📥 {username} 포스트 수집 시작")
            
            # 시간 필터
            since_time = datetime.now(KST) - timedelta(hours=since_hours)
            
            # 트윗 가져오기
            tweets = []
            for tweet in tweepy.Cursor(
                self.x_client.user_timeline,
                screen_name=username,
                exclude_replies=True,
                include_rts=False,
                tweet_mode='extended',
                count=200
            ).items(count):
                # 시간 필터 적용
                tweet_time = tweet.created_at.replace(tzinfo=pytz.UTC)
                if tweet_time < since_time.replace(tzinfo=pytz.UTC):
                    break
                
                tweets.append({
                    'id': tweet.id_str,
                    'author': username,
                    'text': tweet.full_text,
                    'created_at': tweet_time.astimezone(KST).isoformat(),
                    'likes': tweet.favorite_count,
                    'retweets': tweet.retweet_count,
                    'url': f'https://twitter.com/{username}/status/{tweet.id_str}'
                })
            
            logger.info(f"✅ {username}: {len(tweets)}개 포스트 수집 완료")
            return tweets
            
        except tweepy.errors.TweepyException as e:
            logger.error(f"❌ {username} 수집 실패: {str(e)}")
            return []
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
    ) -> str:
        """AI를 이용한 포스트 요약 생성"""
        try:
            if not posts:
                return ""
            
            # 포스트 텍스트 결합
            combined_text = "\n\n".join([
                f"@{post['author']}: {post['text'][:200]}"
                for post in posts[:10]  # 최대 10개만
            ])
            
            prompt = f"""다음은 오늘의 주요 X(트위터) 포스트들입니다. 
한국어로 280자 이내의 매력적인 요약을 작성해주세요.
주요 트렌드와 인사이트를 포함하고, 이모지를 적절히 사용하세요.

포스트들:
{combined_text}

요약:"""
            
            if self.ai_provider == 'openai':
                response = self.ai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "당신은 소셜 미디어 콘텐츠 전문가입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                summary = response.choices[0].message.content
                
            elif self.ai_provider == 'anthropic':
                response = self.ai_client.messages.create(
                    model="claude-3-5-haiku-20241022",
                    max_tokens=500,
                    temperature=0.7,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                summary = response.content[0].text
            
            else:
                summary = f"📱 오늘의 테크 리더 인사이트\n\n{len(posts)}개 포스트 수집됨"
            
            # 길이 제한
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
            
            logger.info(f"✅ AI 요약 생성 완료 ({len(summary)}자)")
            return summary
            
        except Exception as e:
            logger.error(f"❌ 요약 생성 실패: {str(e)}")
            return f"📱 오늘의 인사이트: {len(posts)}개 포스트"
    
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
            # 텍스트와 해시태그 결합
            full_text = content['text']
            if content.get('hashtags'):
                hashtags_text = ' '.join(content['hashtags'])
                # 280자 제한 고려
                if len(full_text) + len(hashtags_text) + 2 <= 280:
                    full_text = f"{full_text}\n\n{hashtags_text}"
            
            # 트윗 게시
            tweet = self.x_client.update_status(full_text)
            
            logger.info(f"✅ X 게시 성공: {tweet.id_str}")
            
            return {
                'success': True,
                'tweet_id': tweet.id_str,
                'url': f'https://twitter.com/user/status/{tweet.id_str}'
            }
            
        except Exception as e:
            logger.error(f"❌ X 게시 실패: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_stats(self) -> Dict:
        """통계 정보"""
        return {
            'total_collected': len(self.collected_posts),
            'influencers_count': len(self.influencers),
            'last_collection': datetime.now(KST).isoformat(),
            'api_status': {
                'x_api': self.x_client is not None,
                'ai_api': self.ai_client is not None
            }
        }


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
