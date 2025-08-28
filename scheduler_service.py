"""
X 크롤링&요약게시 스케줄러 서비스
한국 시간 기준으로 자동 수집 및 게시 관리
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
import traceback

# 로거 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('x_crawler_scheduler')

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')


class XCrawlerScheduler:
    """X 크롤러 스케줄러 관리 클래스"""
    
    def __init__(self):
        """스케줄러 초기화"""
        # APScheduler 설정
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3,
            'misfire_grace_time': 30
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=KST
        )
        
        # 작업 큐
        self.publish_queue = []
        self.collection_history = []
        self.active_influencers = []
        
        # 설정
        self.config = {
            'collection': {
                'enabled': True,
                'times': ['09:00', '15:00', '21:00'],
                'influencers': []
            },
            'publishing': {
                'enabled': True,
                'mode': 'auto',
                'delay': 60,
                'times': ['10:00', '16:00', '22:00']
            }
        }
        
        logger.info("✅ X 크롤러 스케줄러 초기화 완료")
    
    def start(self):
        """스케줄러 시작"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("🚀 스케줄러 시작됨")
    
    def stop(self):
        """스케줄러 중지"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("🛑 스케줄러 중지됨")
    
    def setup_schedules(self, config: Dict[str, Any]):
        """스케줄 설정"""
        self.config = config
        
        # 기존 작업 모두 제거
        self.scheduler.remove_all_jobs()
        
        # 수집 스케줄 설정
        if config.get('collection', {}).get('enabled'):
            for time_str in config['collection'].get('times', []):
                hour, minute = map(int, time_str.split(':'))
                trigger = CronTrigger(
                    hour=hour,
                    minute=minute,
                    timezone=KST
                )
                self.scheduler.add_job(
                    func=self.collect_posts,
                    trigger=trigger,
                    id=f'collect_{time_str}',
                    name=f'수집 작업 - {time_str}'
                )
                logger.info(f"📥 수집 스케줄 추가: 매일 {time_str} (한국 시간)")
        
        # 게시 스케줄 설정
        if config.get('publishing', {}).get('enabled'):
            if config['publishing'].get('mode') == 'scheduled':
                for time_str in config['publishing'].get('times', []):
                    hour, minute = map(int, time_str.split(':'))
                    trigger = CronTrigger(
                        hour=hour,
                        minute=minute,
                        timezone=KST
                    )
                    self.scheduler.add_job(
                        func=self.publish_content,
                        trigger=trigger,
                        id=f'publish_{time_str}',
                        name=f'게시 작업 - {time_str}'
                    )
                    logger.info(f"📤 게시 스케줄 추가: 매일 {time_str} (한국 시간)")
    
    async def collect_posts(self):
        """포스트 자동 수집"""
        try:
            current_time = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"🔄 포스트 수집 시작 - {current_time}")
            
            # 인플루언서 목록 가져오기
            influencers = self.config.get('collection', {}).get('influencers', [])
            
            if not influencers:
                logger.warning("⚠️ 수집할 인플루언서가 없습니다")
                return
            
            collected_posts = []
            
            for influencer in influencers:
                try:
                    # 실제 X API 호출 로직 (추후 구현)
                    posts = await self.fetch_influencer_posts(influencer)
                    collected_posts.extend(posts)
                    logger.info(f"✅ {influencer}: {len(posts)}개 포스트 수집")
                except Exception as e:
                    logger.error(f"❌ {influencer} 수집 실패: {str(e)}")
            
            # AI 요약 생성
            if collected_posts:
                summary = await self.generate_summary(collected_posts)
                
                # 게시 큐에 추가
                if summary:
                    await self.add_to_publish_queue(summary)
                    logger.info(f"📝 요약 생성 완료 및 게시 큐 추가")
            
            # 히스토리 기록
            self.collection_history.append({
                'timestamp': current_time,
                'influencers': len(influencers),
                'posts_collected': len(collected_posts),
                'status': 'success'
            })
            
            return {
                'success': True,
                'collected': len(collected_posts),
                'timestamp': current_time
            }
            
        except Exception as e:
            logger.error(f"❌ 수집 작업 실패: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }
    
    async def publish_content(self):
        """콘텐츠 자동 게시"""
        try:
            current_time = datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"📤 게시 작업 시작 - {current_time}")
            
            if not self.publish_queue:
                logger.info("ℹ️ 게시할 콘텐츠가 없습니다")
                return
            
            # 큐에서 첫 번째 아이템 가져오기
            content = self.publish_queue.pop(0)
            
            # X API로 게시 (추후 구현)
            result = await self.post_to_x(content)
            
            if result.get('success'):
                logger.info(f"✅ 콘텐츠 게시 성공")
                return {
                    'success': True,
                    'content_id': content.get('id'),
                    'timestamp': current_time
                }
            else:
                # 실패 시 큐에 다시 추가
                self.publish_queue.insert(0, content)
                logger.error(f"❌ 게시 실패, 큐에 다시 추가")
                return {
                    'success': False,
                    'error': result.get('error')
                }
                
        except Exception as e:
            logger.error(f"❌ 게시 작업 실패: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def fetch_influencer_posts(self, influencer: str) -> List[Dict]:
        """인플루언서 포스트 가져오기 (추후 구현)"""
        # TODO: 실제 X API 연동
        await asyncio.sleep(1)  # 시뮬레이션
        return [
            {
                'id': f'post_{influencer}_{datetime.now().timestamp()}',
                'author': influencer,
                'content': f'샘플 포스트 from {influencer}',
                'created_at': datetime.now(KST).isoformat()
            }
        ]
    
    async def generate_summary(self, posts: List[Dict]) -> Dict:
        """AI 요약 생성 (추후 구현)"""
        # TODO: OpenAI/Anthropic API 연동
        await asyncio.sleep(2)  # 시뮬레이션
        return {
            'id': f'summary_{datetime.now().timestamp()}',
            'content': f'📱 오늘의 테크 리더 인사이트\n\n{len(posts)}개 포스트 요약',
            'posts_count': len(posts),
            'created_at': datetime.now(KST).isoformat()
        }
    
    async def add_to_publish_queue(self, content: Dict):
        """게시 큐에 추가"""
        content['queued_at'] = datetime.now(KST).isoformat()
        
        # 자동 게시 모드인 경우 지연 시간 후 게시 예약
        if self.config['publishing']['mode'] == 'auto':
            delay_minutes = self.config['publishing'].get('delay', 60)
            publish_time = datetime.now(KST) + timedelta(minutes=delay_minutes)
            content['scheduled_for'] = publish_time.isoformat()
            
            # 일회성 작업 추가
            self.scheduler.add_job(
                func=self.publish_content,
                trigger='date',
                run_date=publish_time,
                id=f'auto_publish_{content["id"]}',
                name=f'자동 게시 - {publish_time.strftime("%H:%M")}'
            )
            logger.info(f"⏰ {delay_minutes}분 후 자동 게시 예약됨")
        
        self.publish_queue.append(content)
    
    async def post_to_x(self, content: Dict) -> Dict:
        """X에 게시 (추후 구현)"""
        # TODO: 실제 X API 연동
        await asyncio.sleep(1)  # 시뮬레이션
        return {
            'success': True,
            'post_id': f'x_post_{datetime.now().timestamp()}'
        }
    
    def get_next_schedules(self, count: int = 10) -> List[Dict]:
        """다음 예정된 작업 목록"""
        jobs = []
        for job in self.scheduler.get_jobs():
            next_run = job.next_run_time
            if next_run:
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run': next_run.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': 'collection' if 'collect' in job.id else 'publishing'
                })
        
        # 시간순 정렬
        jobs.sort(key=lambda x: x['next_run'])
        return jobs[:count]
    
    def get_status(self) -> Dict:
        """스케줄러 상태 조회"""
        return {
            'running': self.scheduler.running,
            'jobs_count': len(self.scheduler.get_jobs()),
            'queue_size': len(self.publish_queue),
            'history_count': len(self.collection_history),
            'next_schedules': self.get_next_schedules(5),
            'current_time': datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')
        }
    
    async def test_collection(self) -> Dict:
        """수집 테스트"""
        logger.info("🧪 수집 테스트 시작")
        result = await self.collect_posts()
        logger.info(f"🧪 수집 테스트 완료: {result}")
        return result
    
    async def test_publishing(self) -> Dict:
        """게시 테스트"""
        logger.info("🧪 게시 테스트 시작")
        
        # 테스트용 콘텐츠 추가
        test_content = {
            'id': f'test_{datetime.now().timestamp()}',
            'content': '🧪 테스트 게시물입니다',
            'created_at': datetime.now(KST).isoformat()
        }
        await self.add_to_publish_queue(test_content)
        
        result = await self.publish_content()
        logger.info(f"🧪 게시 테스트 완료: {result}")
        return result


# 싱글톤 인스턴스
scheduler_instance = None

def get_scheduler() -> XCrawlerScheduler:
    """스케줄러 인스턴스 가져오기"""
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = XCrawlerScheduler()
    return scheduler_instance


# 테스트 코드
if __name__ == "__main__":
    async def test():
        scheduler = get_scheduler()
        scheduler.start()
        
        # 테스트 스케줄 설정
        test_config = {
            'collection': {
                'enabled': True,
                'times': ['09:00', '15:00', '21:00'],
                'influencers': ['@elonmusk', '@sundarpichai']
            },
            'publishing': {
                'enabled': True,
                'mode': 'auto',
                'delay': 60,
                'times': []
            }
        }
        
        scheduler.setup_schedules(test_config)
        
        # 상태 확인
        status = scheduler.get_status()
        print(f"스케줄러 상태: {json.dumps(status, indent=2, ensure_ascii=False)}")
        
        # 수집 테스트
        await scheduler.test_collection()
        
        # 5초 대기
        await asyncio.sleep(5)
        
        # 게시 테스트
        await scheduler.test_publishing()
        
        scheduler.stop()
    
    asyncio.run(test())
