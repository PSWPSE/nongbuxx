# NONGBUXX 상용화 배포 가이드

Railway(백엔드) + Vercel(프론트엔드) 분리 배포를 위한 완전한 가이드입니다.

## 🏗️ 아키텍처 구조

```
┌─────────────────┐    API 호출    ┌─────────────────┐
│   Vercel        │ ──────────────► │   Railway       │
│  (프론트엔드)     │                │   (백엔드 API)   │
│                 │                │                 │
│ - HTML/CSS/JS   │                │ - Flask App     │
│ - 정적 호스팅    │                │ - AI Processing │
│ - CDN 글로벌     │                │ - File Storage  │
└─────────────────┘                └─────────────────┘
```

## 🚀 1단계: Railway 백엔드 배포

### 1.1 Railway 계정 설정
1. [Railway](https://railway.app) 가입
2. GitHub 연동 설정
3. 새 프로젝트 생성

### 1.2 환경 변수 설정
Railway 대시보드에서 다음 환경 변수들을 설정하세요:

**필수 환경 변수:**
```bash
# API Keys (최소 하나는 필수)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Flask 설정
FLASK_ENV=production
PYTHONUNBUFFERED=1
DEBUG=False

# Railway 자동 설정 (수동 설정 불필요)
# PORT=자동할당
# RAILWAY_ENVIRONMENT=production
```

**선택 환경 변수:**
```bash
# 로그 레벨
LOG_LEVEL=INFO

# 최대 콘텐츠 크기 (바이트)
MAX_CONTENT_LENGTH=16777216

# 요청 제한 (분당 요청 수)
RATE_LIMIT=60
```

### 1.3 배포 설정
1. **자동 배포**: GitHub 저장소 연결
2. **수동 배포**: Railway CLI 사용

#### GitHub 자동 배포 (권장)
```bash
# 1. GitHub에 코드 푸시
git add .
git commit -m "Add production deployment config"
git push origin main

# 2. Railway에서 GitHub 저장소 연결
# 3. 자동 빌드 및 배포 완료
```

#### Railway CLI 수동 배포
```bash
# Railway CLI 설치
npm install -g @railway/cli

# Railway 로그인
railway login

# 프로젝트 연결
railway link

# 배포
railway up
```

### 1.4 도메인 설정
1. Railway 대시보드에서 "Settings" → "Domains"
2. 커스텀 도메인 추가: `nongbuxx-api.railway.app`
3. SSL 인증서 자동 생성 확인

## 🌐 2단계: Vercel 프론트엔드 배포

### 2.1 Vercel 계정 설정
1. [Vercel](https://vercel.com) 가입
2. GitHub 연동 설정

### 2.2 프론트엔드 준비
프론트엔드 폴더 구조 확인:
```
frontend/
├── index.html          # 메인 페이지
├── styles.css          # 스타일시트
├── script.js           # JavaScript 로직
├── config.js           # 환경 설정
├── vercel.json         # Vercel 설정
└── package.json        # 프로젝트 메타데이터
```

### 2.3 환경 변수 설정 (선택사항)
Vercel 대시보드에서 환경 변수 설정:
```bash
# API 백엔드 URL (자동 감지되므로 선택사항)
API_BASE_URL=https://nongbuxx-api.railway.app
```

### 2.4 배포 설정

#### 방법 1: Vercel CLI 배포 (권장)
```bash
# Vercel CLI 설치
npm install -g vercel

# frontend 디렉토리로 이동
cd frontend

# Vercel 로그인
vercel login

# 배포
vercel

# 프로덕션 배포
vercel --prod
```

#### 방법 2: GitHub 자동 배포
```bash
# 1. frontend 폴더를 별도 저장소에 푸시하거나
# 2. 서브디렉토리 배포 설정 사용

# Vercel에서 GitHub 저장소 연결
# Root Directory: frontend
# Build Command: npm run build (또는 자동 감지)
# Output Directory: . (static files)
```

#### 방법 3: 수동 배포
```bash
# frontend 디렉토리를 zip으로 압축
# Vercel 대시보드에서 직접 업로드
```

### 2.5 도메인 설정
1. Vercel 대시보드에서 "Settings" → "Domains"
2. 커스텀 도메인 추가: `nongbuxx.vercel.app`
3. DNS 설정 및 SSL 인증서 자동 생성

## 🔧 3단계: 연동 테스트

### 3.1 백엔드 API 테스트
```bash
# 헬스 체크
curl https://nongbuxx-api.railway.app/api/health

# 예상 응답
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000000",
  "version": "1.0.0"
}
```

### 3.2 프론트엔드 테스트
1. `https://nongbuxx.vercel.app` 접속
2. URL 입력 테스트
3. 콘텐츠 생성 테스트
4. 다운로드 기능 테스트

### 3.3 CORS 연결 테스트
브라우저 개발자 도구에서 CORS 오류가 없는지 확인:
```javascript
// 콘솔에서 테스트
fetch('https://nongbuxx-api.railway.app/api/health')
  .then(response => response.json())
  .then(data => console.log(data));
```

## 📊 4단계: 모니터링 설정

### 4.1 Railway 모니터링
- **로그 확인**: Railway 대시보드 → "Logs"
- **메트릭 확인**: CPU, 메모리, 네트워크 사용량
- **헬스 체크**: `/api/health` 엔드포인트 모니터링

### 4.2 Vercel 모니터링
- **접속 통계**: Vercel 대시보드 → "Analytics"
- **빌드 로그**: 배포 상태 및 오류 확인
- **성능 측정**: Core Web Vitals 모니터링

### 4.3 외부 모니터링 (선택사항)
```bash
# UptimeRobot 설정
Monitor URL: https://nongbuxx-api.railway.app/api/health
Check Interval: 5분
Alert Method: 이메일/SMS

# StatusPage 설정
Frontend: https://nongbuxx.vercel.app
Backend: https://nongbuxx-api.railway.app
```

## 🔒 5단계: 보안 설정

### 5.1 API 키 보안
```bash
# Railway 환경 변수 암호화 확인
# Vercel 환경 변수 암호화 확인
# GitHub Actions Secrets 사용 (CI/CD 시)
```

### 5.2 HTTPS 강제 설정
```bash
# Railway: 자동 HTTPS 리디렉션
# Vercel: 자동 HTTPS 리디렉션
# 추가 보안 헤더 설정 (vercel.json에 포함됨)
```

### 5.3 Rate Limiting (선택사항)
```python
# app.py에 추가할 수 있는 레이트 리미팅
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/generate')
@limiter.limit("10 per minute")
def generate_content():
    # ...
```

## 🚀 6단계: 성능 최적화

### 6.1 Railway 백엔드 최적화
```bash
# Gunicorn 워커 수 조정
# railway.json에서 startCommand 수정
"startCommand": "gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app"

# 메모리 사용량 최적화
# 불필요한 로깅 줄이기
```

### 6.2 Vercel 프론트엔드 최적화
```bash
# 이미지 최적화
# CSS/JS 압축
# CDN 활용 (Vercel 자동 제공)
```

## 🔄 7단계: CI/CD 설정 (선택사항)

### 7.1 GitHub Actions 설정
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      # Railway 자동 배포 (GitHub 연동)
      
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      # Vercel 자동 배포 (GitHub 연동)
```

## 📋 체크리스트

### 배포 전 체크리스트
- [ ] API 키 환경 변수 설정
- [ ] CORS 도메인 설정 확인
- [ ] Railway/Vercel 계정 생성
- [ ] GitHub 저장소 준비
- [ ] 로컬 테스트 완료

### 배포 후 체크리스트
- [ ] 백엔드 헬스 체크 통과
- [ ] 프론트엔드 접속 확인
- [ ] API 연동 테스트 완료
- [ ] 파일 다운로드 기능 테스트
- [ ] 배치 처리 기능 테스트
- [ ] 모바일 반응형 확인

## 🆘 문제 해결

### 일반적인 오류

#### 1. CORS 오류
```bash
# 증상: 브라우저에서 "CORS policy" 오류
# 해결: app.py의 CORS origins에 프론트엔드 도메인 추가
```

#### 2. API 키 오류
```bash
# 증상: "ANTHROPIC_API_KEY environment variable is required"
# 해결: Railway 환경 변수에 API 키 추가
```

#### 3. 배포 실패
```bash
# Railway 로그 확인
railway logs

# Vercel 로그 확인
vercel logs
```

#### 4. 느린 응답 시간
```bash
# Railway: 워커 수 증가
# Vercel: CDN 캐싱 활용
# API: 타임아웃 설정 조정
```

## 💰 비용 예상

### Railway (백엔드)
- **Starter Plan**: $5/월
- **포함사항**: 512MB RAM, 1GB 스토리지
- **추가 비용**: 트래픽 사용량에 따라

### Vercel (프론트엔드)
- **Hobby Plan**: 무료
- **포함사항**: 100GB 대역폭, 무제한 요청
- **Pro Plan**: $20/월 (상용 서비스 권장)

### 총 예상 비용
- **개발/테스트**: $5/월 (Railway Starter + Vercel Hobby)
- **상용 서비스**: $25/월 (Railway Starter + Vercel Pro)

## 📞 지원

배포 과정에서 문제가 발생하면:
1. [GitHub Issues](https://github.com/PSWPSE/nongbuxx/issues) 생성
2. Railway/Vercel 공식 문서 참조
3. 커뮤니티 포럼 활용

---

**Happy Deploying! 🚀** 