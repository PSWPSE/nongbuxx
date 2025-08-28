# 🚨 X API 호출 최적화 분석 보고서

## 📊 현재 API 호출 패턴 분석

### 1. **문제가 되는 API 호출 지점**

#### 🔴 **비효율적인 호출 발견**

1. **인증 확인 (`/api/validate/x-credentials`)**
   - 매번 `verify_credentials()` 호출
   - X API v2: `client.get_me()` 호출
   - **문제**: 사용자가 "인증 확인" 버튼을 누를 때마다 API 호출

2. **인플루언서 포스트 수집**
   - `tweepy.Cursor`로 최대 200개 트윗 요청
   - `get_user()` API 호출로 사용자 ID 조회
   - **문제**: 각 인플루언서마다 2개 이상의 API 호출

3. **트윗 게시**
   - `update_status()` API 호출
   - **문제**: 각 게시마다 1회 호출 (불가피함)

### 2. **X API Rate Limits (제한사항)**

#### 📋 **Twitter API v1.1 제한**
| 엔드포인트 | 15분당 제한 | 용도 |
|----------|------------|------|
| `statuses/user_timeline` | 900회 | 타임라인 조회 |
| `users/show` | 900회 | 사용자 정보 |
| `statuses/update` | 300회 | 트윗 게시 |
| `account/verify_credentials` | 75회 | 인증 확인 |

#### 📋 **Twitter API v2 제한**
| 엔드포인트 | 15분당 제한 | 월간 제한 |
|----------|------------|----------|
| `users/me` | 75회 | - |
| `tweets` (읽기) | 300회 | 10,000회 |
| `tweets` (쓰기) | 200회 | - |

### 3. **현재 코드의 문제점**

```python
# 문제 1: 매번 사용자 정보 조회
user = self.x_client.get_user(screen_name=username)  # API 호출 1
for tweet in tweepy.Cursor(self.x_client.user_timeline...):  # API 호출 2+
```

```python
# 문제 2: 인증 확인 남발
def verify_credentials(self):
    response = self.client.get_me()  # 매번 API 호출
```

## 🛠️ **최적화 방안**

### 1. **캐싱 전략 구현**

#### ✅ **사용자 정보 캐싱**
```python
class XCrawler:
    def __init__(self):
        self.user_cache = {}  # 사용자 정보 캐시
        self.cache_ttl = 3600  # 1시간 캐시
        
    def get_user_id(self, username):
        # 캐시 확인
        cache_key = username
        if cache_key in self.user_cache:
            cached = self.user_cache[cache_key]
            if time.time() - cached['timestamp'] < self.cache_ttl:
                return cached['user_id']
        
        # 캐시 미스 시에만 API 호출
        user = self.x_client.get_user(screen_name=username)
        self.user_cache[cache_key] = {
            'user_id': user.id_str,
            'timestamp': time.time()
        }
        return user.id_str
```

#### ✅ **인증 상태 캐싱**
```python
class XPublisher:
    def __init__(self):
        self.last_verify_time = 0
        self.verify_cache_ttl = 900  # 15분
        self.cached_user = None
        
    def verify_credentials(self):
        # 캐시된 인증 정보 사용
        if self.cached_user and \
           time.time() - self.last_verify_time < self.verify_cache_ttl:
            return {
                'success': True,
                'user': self.cached_user,
                'cached': True
            }
        
        # 캐시 만료 시에만 API 호출
        response = self.client.get_me()
        self.cached_user = {...}
        self.last_verify_time = time.time()
```

### 2. **배치 처리 최적화**

#### ✅ **트윗 수집 최적화**
```python
def fetch_influencer_posts(self, username, count=10, since_hours=24):
    # count를 최소화 (10개면 충분)
    # API 호출을 줄이기 위해 필요한 만큼만 가져오기
    
    tweets = []
    for tweet in tweepy.Cursor(...).items(count):
        # 조기 종료 조건
        if len(tweets) >= count:
            break
```

### 3. **Rate Limit 관리**

#### ✅ **Rate Limit 추적**
```python
class RateLimitManager:
    def __init__(self):
        self.limits = {
            'verify_credentials': {'count': 0, 'reset_time': 0, 'limit': 75},
            'user_timeline': {'count': 0, 'reset_time': 0, 'limit': 900},
            'update_status': {'count': 0, 'reset_time': 0, 'limit': 300}
        }
    
    def can_call(self, endpoint):
        limit = self.limits.get(endpoint)
        if not limit:
            return True
            
        # 리셋 시간 확인
        if time.time() > limit['reset_time']:
            limit['count'] = 0
            limit['reset_time'] = time.time() + 900  # 15분
            
        return limit['count'] < limit['limit']
    
    def record_call(self, endpoint):
        if endpoint in self.limits:
            self.limits[endpoint]['count'] += 1
```

### 4. **스마트 폴링**

#### ✅ **조건부 API 호출**
```python
def should_fetch_posts(self, influencer):
    # 마지막 수집 시간 확인
    last_fetch = influencer.get('last_fetched')
    if last_fetch:
        time_diff = datetime.now() - datetime.fromisoformat(last_fetch)
        # 최소 1시간 간격
        if time_diff.total_seconds() < 3600:
            return False
    return True
```

## 📈 **예상 개선 효과**

### Before (현재)
- 인증 확인: 버튼 클릭마다 1회
- 인플루언서 5명 수집: 10회 (각 2회)
- 총 API 호출: 시간당 50-100회

### After (최적화 후)
- 인증 확인: 15분당 1회 (캐싱)
- 인플루언서 5명 수집: 5-7회 (캐싱)
- 총 API 호출: 시간당 10-20회
- **80% 감소**

## 🚀 **즉시 적용 가능한 Quick Fix**

### 1. **프론트엔드 디바운싱**
```javascript
// 인증 확인 버튼 연속 클릭 방지
let isValidating = false;
async function validateXApi() {
    if (isValidating) return;
    isValidating = true;
    
    try {
        // API 호출
    } finally {
        setTimeout(() => {
            isValidating = false;
        }, 5000);  // 5초 쿨다운
    }
}
```

### 2. **최소 수집 간격 설정**
```python
MIN_COLLECTION_INTERVAL = 3600  # 1시간

def can_collect(self):
    if self.last_collection_time:
        elapsed = time.time() - self.last_collection_time
        if elapsed < MIN_COLLECTION_INTERVAL:
            return False, f"다음 수집까지 {int((MIN_COLLECTION_INTERVAL - elapsed)/60)}분 남음"
    return True, None
```

## 🎯 **권장 사항**

1. **즉시 조치**
   - ✅ 인증 확인 캐싱 구현
   - ✅ 사용자 정보 캐싱 구현
   - ✅ 최소 수집 간격 설정

2. **단기 개선**
   - ✅ Rate Limit Manager 구현
   - ✅ 프론트엔드 디바운싱
   - ✅ 배치 크기 최적화 (200→10)

3. **장기 개선**
   - ✅ Redis 캐시 도입
   - ✅ Webhook 기반 실시간 수집
   - ✅ 스케줄러 최적화

## 📊 **모니터링 지표**

```python
# API 사용량 추적
{
    "x_api": {
        "calls_made": 45,
        "calls_remaining": 855,
        "reset_time": "2025-08-28T14:30:00",
        "endpoints": {
            "verify_credentials": 5,
            "user_timeline": 30,
            "update_status": 10
        }
    }
}
```

## ⚠️ **주의사항**

1. **Free Tier 제한**
   - 월 10,000 트윗 읽기
   - 일 333개, 시간당 14개

2. **Rate Limit 도달 시**
   - 15분 대기 필요
   - 429 에러 처리 필수

3. **Best Practices**
   - 필요한 데이터만 요청
   - 캐싱 적극 활용
   - 배치 처리 최적화
