"""
X(Twitter) API 게시 모듈
X API v2를 사용한 트윗 게시 기능
"""
import tweepy
import os
from typing import Dict, Optional, List
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class XPublisher:
    """X(Twitter) 게시 관리 클래스"""
    
    def __init__(self, bearer_token: Optional[str] = None, 
                 consumer_key: Optional[str] = None,
                 consumer_secret: Optional[str] = None,
                 access_token: Optional[str] = None,
                 access_token_secret: Optional[str] = None):
        """
        X API 클라이언트 초기화
        
        Args:
            bearer_token: Bearer Token (읽기 전용)
            consumer_key: API Key
            consumer_secret: API Secret
            access_token: Access Token
            access_token_secret: Access Token Secret
        """
        self.authenticated = False
        self.client = None
        
        try:
            # OAuth 1.0a 인증 (게시 권한 필요)
            if all([consumer_key, consumer_secret, access_token, access_token_secret]):
                self.client = tweepy.Client(
                    consumer_key=consumer_key,
                    consumer_secret=consumer_secret,
                    access_token=access_token,
                    access_token_secret=access_token_secret
                )
                self.authenticated = True
                logger.info("X API 클라이언트 초기화 성공")
            else:
                logger.warning("X API 인증 정보 불완전")
                
        except Exception as e:
            logger.error(f"X API 클라이언트 초기화 실패: {str(e)}")
            self.authenticated = False
    
    def verify_credentials(self) -> Dict:
        """
        API 인증 상태 확인
        
        Returns:
            인증 상태 및 사용자 정보
        """
        if not self.authenticated or not self.client:
            return {
                'success': False,
                'error': 'API 클라이언트가 초기화되지 않았습니다'
            }
        
        try:
            # 현재 사용자 정보 가져오기
            response = self.client.get_me()
            if response.data:
                return {
                    'success': True,
                    'user': {
                        'id': response.data.id,
                        'username': response.data.username,
                        'name': response.data.name
                    }
                }
            else:
                return {
                    'success': False,
                    'error': '사용자 정보를 가져올 수 없습니다'
                }
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"인증 확인 실패: {error_msg}")
            
            # 429 Too Many Requests 처리
            if '429' in error_msg or 'Too Many Requests' in error_msg:
                return {
                    'success': False,
                    'error': 'X API 요청 제한에 도달했습니다. 15분 후에 다시 시도해주세요.',
                    'code': 'RATE_LIMIT_EXCEEDED'
                }
            # 401 Unauthorized
            elif '401' in error_msg or 'Unauthorized' in error_msg:
                return {
                    'success': False,
                    'error': 'X API 인증에 실패했습니다. API 키를 확인해주세요.',
                    'code': 'UNAUTHORIZED'
                }
            else:
                return {
                    'success': False,
                    'error': error_msg
                }
    
    def post_tweet(self, text: str, media_ids: Optional[List[str]] = None) -> Dict:
        """
        트윗 게시
        
        Args:
            text: 트윗 내용 (280자 제한)
            media_ids: 미디어 ID 리스트 (선택)
            
        Returns:
            게시 결과
        """
        if not self.authenticated or not self.client:
            return {
                'success': False,
                'error': 'API 클라이언트가 초기화되지 않았습니다'
            }
        
        try:
            # 트윗 길이 검증
            if len(text) > 280:
                return {
                    'success': False,
                    'error': f'트윗이 너무 깁니다 ({len(text)}/280자)'
                }
            
            # 트윗 게시
            response = self.client.create_tweet(
                text=text,
                media_ids=media_ids
            )
            
            if response.data:
                tweet_id = response.data['id']
                # 트윗 URL 생성
                user_info = self.verify_credentials()
                if user_info['success']:
                    tweet_url = f"https://twitter.com/{user_info['user']['username']}/status/{tweet_id}"
                else:
                    tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
                
                return {
                    'success': True,
                    'tweet_id': tweet_id,
                    'tweet_url': tweet_url,
                    'posted_at': datetime.now().isoformat(),
                    'text': text
                }
            else:
                return {
                    'success': False,
                    'error': '트윗 게시에 실패했습니다'
                }
                
        except tweepy.TooManyRequests as e:
            logger.error(f"Rate limit 초과: {str(e)}")
            return {
                'success': False,
                'error': 'API 요청 제한을 초과했습니다. 잠시 후 다시 시도해주세요.'
            }
        except tweepy.Forbidden as e:
            logger.error(f"권한 없음: {str(e)}")
            return {
                'success': False,
                'error': '트윗 게시 권한이 없습니다. API 설정을 확인해주세요.'
            }
        except Exception as e:
            logger.error(f"트윗 게시 실패: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def post_thread(self, tweets: List[str]) -> Dict:
        """
        스레드 형태로 여러 트윗 연속 게시
        
        Args:
            tweets: 트윗 리스트
            
        Returns:
            게시 결과
        """
        if not self.authenticated or not self.client:
            return {
                'success': False,
                'error': 'API 클라이언트가 초기화되지 않았습니다'
            }
        
        thread_results = []
        reply_to_id = None
        
        try:
            for i, tweet_text in enumerate(tweets):
                # 각 트윗 게시
                if reply_to_id:
                    # 이전 트윗에 대한 답글로 게시
                    response = self.client.create_tweet(
                        text=tweet_text,
                        in_reply_to_tweet_id=reply_to_id
                    )
                else:
                    # 첫 트윗
                    response = self.client.create_tweet(text=tweet_text)
                
                if response.data:
                    tweet_id = response.data['id']
                    reply_to_id = tweet_id  # 다음 트윗은 이 트윗에 대한 답글로
                    
                    thread_results.append({
                        'tweet_id': tweet_id,
                        'text': tweet_text,
                        'position': i + 1
                    })
                else:
                    return {
                        'success': False,
                        'error': f'{i+1}번째 트윗 게시 실패',
                        'posted_tweets': thread_results
                    }
            
            # 스레드 URL 생성
            user_info = self.verify_credentials()
            if user_info['success'] and thread_results:
                thread_url = f"https://twitter.com/{user_info['user']['username']}/status/{thread_results[0]['tweet_id']}"
            else:
                thread_url = None
            
            return {
                'success': True,
                'thread_url': thread_url,
                'tweets': thread_results,
                'total_tweets': len(thread_results),
                'posted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"스레드 게시 실패: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'posted_tweets': thread_results
            }
    
    def split_long_content(self, content: str, max_length: int = 270) -> List[str]:
        """
        긴 콘텐츠를 여러 트윗으로 분할
        
        Args:
            content: 원본 콘텐츠
            max_length: 트윗당 최대 길이 (기본 270자, 스레드 번호 공간 확보)
            
        Returns:
            분할된 트윗 리스트
        """
        tweets = []
        
        # 문장 단위로 분할
        sentences = re.split(r'(?<=[.!?])\s+', content)
        current_tweet = ""
        
        for sentence in sentences:
            # 현재 트윗에 문장 추가 가능한지 확인
            if len(current_tweet) + len(sentence) + 1 <= max_length:
                if current_tweet:
                    current_tweet += " " + sentence
                else:
                    current_tweet = sentence
            else:
                # 현재 트윗 저장하고 새 트윗 시작
                if current_tweet:
                    tweets.append(current_tweet)
                current_tweet = sentence
        
        # 마지막 트윗 추가
        if current_tweet:
            tweets.append(current_tweet)
        
        # 스레드 번호 추가
        if len(tweets) > 1:
            numbered_tweets = []
            for i, tweet in enumerate(tweets, 1):
                numbered_tweet = f"({i}/{len(tweets)}) {tweet}"
                # 280자 제한 확인
                if len(numbered_tweet) > 280:
                    # 트윗이 너무 길면 축약
                    max_content_length = 280 - len(f"({i}/{len(tweets)}) ...")
                    numbered_tweet = f"({i}/{len(tweets)}) {tweet[:max_content_length]}..."
                numbered_tweets.append(numbered_tweet)
            return numbered_tweets
        
        return tweets
    
    def format_content_for_x(self, content: str) -> str:
        """
        콘텐츠를 X 게시에 적합한 형식으로 변환
        
        Args:
            content: 원본 콘텐츠
            
        Returns:
            포맷된 콘텐츠
        """
        # 마크다운 헤더 제거 (# ## ### 등)
        content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)
        
        # 마크다운 볼드/이탤릭 제거 (내용은 유지)
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
        content = re.sub(r'\*([^*]+)\*', r'\1', content)
        content = re.sub(r'__([^_]+)__', r'\1', content)
        content = re.sub(r'_([^_]+)_', r'\1', content)
        
        # 마크다운 코드 블록 제거
        content = re.sub(r'```[^`]*```', '', content)
        content = re.sub(r'`([^`]+)`', r'\1', content)
        
        # 마크다운 링크 제거 (텍스트만 유지)
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
        
        # X Short Form 포맷팅 적용
        # 구조: 제목 → 출처 → 빈줄 → 본문 → 빈줄 → 해시태그
        lines = content.split('\n')
        title = ""
        source = ""
        body_lines = []
        hashtags = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 제목 (다양한 이모지로 시작)
            if not title and any(line.startswith(emoji) for emoji in ['🚨', '📈', '📉', '📊', '💰', '💵', '💴', '💶', '🏢', '🏭', '🛍️', '🏦', '🚀', '💡', '🔬', '🤖', '💻', '⚠️', '🔥', '💥', '🇺🇸', '🇨🇳', '🇯🇵', '🇰🇷', '🇪🇺', '🎯', '⚡', '🌍', '📱', '🏆', '🎮', '🛡️', '📌', '🔍', '🌟']):
                if '(출처:' in line:
                    title = line.split('(출처:')[0].strip()
                    source = '(출처:' + line.split('(출처:')[1]
                else:
                    title = line
            # 출처
            elif not source and '(출처:' in line:
                source = line
            # 해시태그
            elif line.startswith('#') and line.count('#') >= 2:
                hashtags = line
            # 불렛 포인트나 섹션 구분자
            elif line.startswith('•') or line.startswith('▶'):
                body_lines.append(line)
            # 기타 내용
            elif not title:
                title = line
            elif not line.startswith('#'):
                body_lines.append(line)
        
        # 재구성
        parts = []
        if title:
            parts.append(title)
        if source:
            parts.append(source)
            parts.append("")  # 출처 다음 빈 줄
        if body_lines:
            parts.extend(body_lines)
        if hashtags:
            if parts and parts[-1].strip() != "":
                parts.append("")  # 해시태그 앞 빈 줄
            parts.append(hashtags)
        
        content = '\n'.join(parts)
        
        # 불필요한 공백 제거
        content = content.strip()
        
        return content


# 테스트 및 유틸리티 함수
def test_connection(consumer_key: str, consumer_secret: str, 
                   access_token: str, access_token_secret: str) -> Dict:
    """
    X API 연결 테스트
    
    Returns:
        연결 테스트 결과
    """
    try:
        publisher = XPublisher(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        result = publisher.verify_credentials()
        if result['success']:
            return {
                'success': True,
                'message': f"연결 성공! 사용자: @{result['user']['username']}",
                'user': result['user']
            }
        else:
            return result
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
