# NONGBUXX - 한국어 뉴스 콘텐츠 생성기

AI 기반 뉴스 콘텐츠 생성 도구로, 웹 기사를 구조화된 한국어 마크다운 형식으로 변환합니다.

## 🌟 주요 기능

- 🔗 **웹 콘텐츠 자동 추출**: URL에서 뉴스 기사 내용을 자동으로 추출
- 🤖 **AI 기반 변환**: OpenAI GPT-4 또는 Anthropic Claude를 사용한 지능적 변환
- 📝 **구조화된 마크다운**: 한국어 독자를 위한 체계적인 마크다운 형식
- 🏷️ **SEO 최적화**: 자동 생성되는 한국어 해시태그
- ⚡ **배치 처리**: 여러 URL 동시 처리 가능
- 🎯 **원스탑 처리**: 추출부터 변환까지 한 번에 완료
- 🌐 **웹 인터페이스**: 직관적인 웹 UI로 누구나 쉽게 사용 가능

## 🚀 빠른 시작 (웹 애플리케이션)

### 방법 1: 원클릭 배포 (권장)
```bash
# 저장소 복제
git clone https://github.com/PSWPSE/nongbuxx.git
cd nongbuxx

# 자동 배포 스크립트 실행
./deploy.sh
```

### 방법 2: Docker Compose 사용
```bash
# 1. 환경 변수 설정
cp env.example .env
# .env 파일을 열어서 API 키 설정

# 2. 애플리케이션 시작
docker-compose up -d

# 3. 웹 브라우저에서 접속
open http://localhost:5000
```

### 방법 3: 직접 실행
```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경 변수 설정
export ANTHROPIC_API_KEY=your_key_here
# 또는
export OPENAI_API_KEY=your_key_here

# 3. 웹 서버 시작
python app.py
```

## 🖥️ 웹 인터페이스 사용법

1. **웹 브라우저에서 접속**: http://localhost:5000
2. **URL 입력**: 변환할 뉴스 기사의 URL을 입력
3. **API 선택**: Anthropic Claude 또는 OpenAI GPT-4 선택
4. **콘텐츠 생성**: '콘텐츠 생성' 버튼 클릭
5. **결과 확인**: 생성된 마크다운을 미리보기 또는 다운로드

### 배치 처리
- '배치 처리' 버튼을 클릭하여 여러 URL을 한 번에 처리
- 각 URL을 새 줄에 입력
- 모든 결과를 개별 또는 일괄 다운로드 가능

## 🛠️ 시스템 요구사항

### 웹 애플리케이션
- Docker 및 Docker Compose
- OpenAI API 키 또는 Anthropic API 키
- 인터넷 연결

### CLI 도구
- Python 3.7+
- OpenAI API 키 또는 Anthropic API 키
- 인터넷 연결

## 📋 CLI 사용 방법

### 설치 및 설정

#### 1. 저장소 복제
```bash
git clone https://github.com/PSWPSE/nongbuxx.git
cd nongbuxx
```

#### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

#### 3. 환경 변수 설정
`.env` 파일을 생성하고 API 키를 설정:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

> **참고**: 최소 하나의 API 키는 필수입니다.

### 기본 사용법
```bash
python nongbuxx_generator.py "https://finance.yahoo.com/news/example-article"
```

### 고급 옵션
```bash
# OpenAI API 사용
python nongbuxx_generator.py "https://news-url.com" --api openai

# 사용자 정의 파일명
python nongbuxx_generator.py "https://news-url.com" --filename "my_article"

# 중간 파일 저장 안 함
python nongbuxx_generator.py "https://news-url.com" --no-temp

# 배치 처리
python nongbuxx_generator.py --batch "https://url1.com" "https://url2.com" "https://url3.com"
```

## 🏗️ 프로젝트 구조

```
nongbuxx/
├── app.py                   # Flask 웹 애플리케이션
├── nongbuxx_generator.py    # 통합 메인 생성기 (CLI)
├── web_extractor.py         # 웹 콘텐츠 추출 모듈
├── converter.py             # AI 마크다운 변환 모듈
├── requirements.txt         # Python 의존성
├── Dockerfile              # Docker 이미지 빌드
├── docker-compose.yml      # Docker Compose 설정
├── deploy.sh               # 자동 배포 스크립트
├── env.example             # 환경 변수 템플릿
├── static/                 # 웹 프론트엔드 파일
│   ├── index.html         # 메인 HTML
│   ├── styles.css         # CSS 스타일
│   └── script.js          # JavaScript 로직
├── generated_content/       # 생성된 콘텐츠 저장소
└── uploads/                # 업로드 파일 저장소
```

## 🌐 API 엔드포인트

### 주요 엔드포인트
- `GET /` - 메인 웹 페이지
- `GET /api/health` - 서비스 상태 확인
- `POST /api/generate` - 단일 콘텐츠 생성
- `POST /api/batch` - 배치 콘텐츠 생성
- `GET /api/status/<job_id>` - 작업 상태 조회
- `GET /api/download/<job_id>` - 파일 다운로드

### API 사용 예시
```bash
# 콘텐츠 생성
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/news", "api_provider": "anthropic"}'

# 서비스 상태 확인
curl http://localhost:5000/api/health
```

## 📝 출력 형식

생성되는 한국어 마크다운은 다음과 같은 구조를 가집니다:

```markdown
# 📈 [제목] (이모지 포함)

## ▶ 핵심 요약
- 주요 내용 요약

## ▶ 주요 내용
- 상세 내용
- 회사명 $SYMBOL 형식

## ▶ 시장 영향
- 시장에 미치는 영향 분석

## ▶ 투자 시사점
- 투자 관련 인사이트

#한국어해시태그 #투자 #경제 #뉴스 #금융
```

## ⚡ 주요 특징

### 🔧 성능 최적화
- 직접 데이터 처리로 95% 파일 I/O 감소
- 메모리 사용량 50% 절약
- 처리 시간 33% 단축

### 🎯 스마트 변환
- 한국어 독자 최적화
- 구조화된 섹션 구성
- SEO 친화적 해시태그 자동 생성

### 🔄 유연한 API 지원
- OpenAI GPT-4
- Anthropic Claude
- 실시간 API 전환 가능

### 🌐 사용자 친화적 웹 인터페이스
- 반응형 디자인
- 실시간 진행 상황 표시
- 미리보기 및 다운로드 기능
- 배치 처리 지원

## 🚀 배포 옵션

### 1. 로컬 개발 환경
```bash
python app.py
```

### 2. Docker 컨테이너
```bash
docker build -t nongbuxx .
docker run -p 5000:5000 --env-file .env nongbuxx
```

### 3. Docker Compose
```bash
docker-compose up -d
```

### 4. **🌟 상용화 배포 (권장)**

#### 원클릭 상용화 배포
```bash
# 1단계: Railway 백엔드 배포
./deploy-railway.sh

# 2단계: Vercel 프론트엔드 배포  
./deploy-vercel.sh
```

#### 분리 배포 아키텍처
```
┌─────────────────┐    API 호출    ┌─────────────────┐
│   Vercel        │ ──────────────► │   Railway       │
│  (프론트엔드)     │                │   (백엔드 API)   │
│                 │                │                 │
│ - 정적 호스팅    │                │ - Flask API     │
│ - 글로벌 CDN     │                │ - AI Processing │
│ - 무료/저렴      │                │ - 스케일링      │
└─────────────────┘                └─────────────────┘
```

**장점:**
- ⚡ **빠른 성능**: Vercel CDN으로 전세계 빠른 접속
- 💰 **비용 효율**: 프론트엔드 무료, 백엔드 $5/월
- 🔄 **자동 배포**: GitHub 푸시 시 자동 업데이트
- 📈 **확장성**: 트래픽 증가 시 자동 스케일링
- 🛡️ **보안**: HTTPS, 환경 변수 암호화

**상세 가이드**: [PRODUCTION_DEPLOY.md](PRODUCTION_DEPLOY.md) 참조

### 5. 기타 클라우드 배포
- Heroku, AWS, GCP, Azure 등 지원
- 환경 변수 설정 필요
- 포트 5000 사용

## 🔧 문제 해결

### 일반적인 오류

1. **API 키 오류**
   ```
   Error: ANTHROPIC_API_KEY environment variable is required
   ```
   → `.env` 파일에 올바른 API 키를 설정하세요.

2. **URL 접근 오류**
   ```
   Error: Content extraction failed
   ```
   → URL이 올바른지 확인하고 네트워크 연결을 점검하세요.

3. **Docker 관련 오류**
   ```bash
   # 컨테이너 로그 확인
   docker-compose logs -f
   
   # 컨테이너 재시작
   docker-compose restart
   ```

4. **포트 충돌**
   ```bash
   # 다른 포트 사용
   PORT=8080 docker-compose up -d
   ```

## 📊 모니터링

### 헬스 체크
```bash
curl http://localhost:5000/api/health
```

### 로그 확인
```bash
# Docker Compose
docker-compose logs -f

# 직접 실행
tail -f app.log
```

## 🔐 보안 고려사항

- API 키는 환경 변수로 관리
- HTTPS 사용 권장 (프로덕션 환경)
- 파일 업로드 크기 제한
- 요청 빈도 제한 (선택사항)

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여하기

1. 이 저장소를 포크하세요
2. 새 브랜치를 생성하세요 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋하세요 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시하세요 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성하세요

## 지원

문제가 발생하면 [Issues](https://github.com/PSWPSE/nongbuxx/issues)에서 리포트해주세요.

---

**Made with ❤️ by PSWPSE** 