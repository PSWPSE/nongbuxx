# 🔐 NONGBUXX 로그인 시스템 환경 변수 설정 가이드

## 📍 설정이 필요한 위치

1. **Railway Dashboard**: 프로덕션 환경 변수
2. **로컬 .env 파일**: 개발 환경 변수

## 🔑 필수 환경 변수 및 값 생성 방법

### 1. SECRET_KEY (Flask 앱 시크릿 키)

**용도**: 세션 관리, CSRF 보호 등에 사용

**생성 방법**:
```python
# Python에서 실행
import secrets
print(secrets.token_urlsafe(32))
```

**예시 출력**: `Rl3kD7nP_9xKHLZKZpX6Ug3_sFtJYbcL8eI6Y5fVJfg`

### 2. JWT_SECRET_KEY (JWT 토큰 서명 키)

**용도**: JWT 토큰 생성 및 검증

**생성 방법**:
```python
# Python에서 실행
import secrets
print(secrets.token_urlsafe(32))
```

**예시 출력**: `xM9kP2nL_7dKJHGKLpQ4Rg8_zBtMNvcK6aO8S3hRKhw`

### 3. ENCRYPTION_KEY (API 키 암호화)

**용도**: 사용자의 API 키를 암호화하여 저장

**생성 방법** (정확히 32자여야 함):
```python
# Python에서 실행
import string
import random
chars = string.ascii_letters + string.digits
print(''.join(random.choice(chars) for _ in range(32)))
```

**예시 출력**: `Ab3Cd5Ef7Gh9Ij2Kl4Mn6Op8Qr0St2Uv`

## 📝 Railway에서 환경 변수 설정하기

### Railway Dashboard 설정 순서:

1. **백엔드 서비스 선택**
   ```
   Railway Dashboard → NONGBUXX 프로젝트 → 백엔드 서비스 클릭
   ```

2. **Variables 탭으로 이동**

3. **다음 변수들 추가** (Raw Editor 또는 개별 추가):

```bash
# 보안 관련 (위에서 생성한 값들 사용)
SECRET_KEY=<생성한 32자 이상 문자열>
JWT_SECRET_KEY=<생성한 32자 이상 문자열>
ENCRYPTION_KEY=<생성한 정확히 32자 문자열>

# Flask 환경
FLASK_ENV=production

# 기존에 있던 API 키들 (있다면)
ANTHROPIC_API_KEY=<기존 값>
OPENAI_API_KEY=<기존 값>
```

### 예시 (실제 사용하지 마세요):
```bash
SECRET_KEY=Rl3kD7nP_9xKHLZKZpX6Ug3_sFtJYbcL8eI6Y5fVJfg
JWT_SECRET_KEY=xM9kP2nL_7dKJHGKLpQ4Rg8_zBtMNvcK6aO8S3hRKhw
ENCRYPTION_KEY=Ab3Cd5Ef7Gh9Ij2Kl4Mn6Op8Qr0St2Uv
FLASK_ENV=production
```

## 💻 로컬 개발 환경 설정

### .env 파일 업데이트:

```bash
# 기존 API 키들
ANTHROPIC_API_KEY=<실제 API 키>
OPENAI_API_KEY=<실제 API 키>

# 데이터베이스 (로컬은 SQLite 사용)
DATABASE_URL=sqlite:///nongbuxx.db

# JWT 및 보안 (개발용은 간단한 값 사용 가능)
SECRET_KEY=dev-secret-key-for-local-development-only
JWT_SECRET_KEY=dev-jwt-secret-key-for-local-only
ENCRYPTION_KEY=dev32charactersencryptionkeyhere

# Flask
FLASK_ENV=development
```

## 🔍 설정 확인 방법

### 1. Railway에서 DATABASE_URL 확인:
```
PostgreSQL 서비스 → Variables 탭 → DATABASE_URL 복사
```

### 2. 로컬에서 환경 변수 확인:
```bash
# Python에서 실행
from dotenv import load_dotenv
import os

load_dotenv()
print("SECRET_KEY 설정됨:", bool(os.getenv('SECRET_KEY')))
print("JWT_SECRET_KEY 설정됨:", bool(os.getenv('JWT_SECRET_KEY')))
print("ENCRYPTION_KEY 설정됨:", bool(os.getenv('ENCRYPTION_KEY')))
print("DATABASE_URL:", os.getenv('DATABASE_URL'))
```

## ⚠️ 보안 주의사항

1. **절대 공유하지 마세요**: 
   - SECRET_KEY, JWT_SECRET_KEY, ENCRYPTION_KEY는 비밀번호와 같습니다
   - GitHub에 커밋하지 마세요 (.env는 .gitignore에 포함됨)

2. **프로덕션과 개발 분리**:
   - 프로덕션(Railway)과 개발(로컬)은 다른 키 사용
   - 프로덕션 키는 더 강력하게 생성

3. **주기적 변경**:
   - 보안 사고 시 즉시 변경
   - 정기적으로 (6개월~1년) 변경 권장

## 📊 설정 완료 체크리스트

- [ ] Railway에 PostgreSQL 서비스 추가
- [ ] DATABASE_URL 자동 생성 확인
- [ ] SECRET_KEY 생성 및 설정 (32자 이상)
- [ ] JWT_SECRET_KEY 생성 및 설정 (32자 이상)
- [ ] ENCRYPTION_KEY 생성 및 설정 (정확히 32자)
- [ ] Railway Variables에 모든 환경 변수 추가
- [ ] 로컬 .env 파일 업데이트
- [ ] 설정 값 확인 테스트 실행

## 🚀 다음 단계

모든 환경 변수 설정 완료 후:
1. Railway에서 자동 재배포 확인
2. 로컬에서 `python app.py` 실행 테스트
3. 인증 API 구현 진행 