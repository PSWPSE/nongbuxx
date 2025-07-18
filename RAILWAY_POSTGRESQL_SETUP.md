# 🗄️ Railway PostgreSQL 설정 가이드

## 📋 Railway Dashboard에서 PostgreSQL 추가하기

### 1️⃣ Railway 프로젝트에 PostgreSQL 추가

1. **Railway Dashboard 접속**
   - https://railway.app/dashboard 로그인
   - NONGBUXX 프로젝트 선택

2. **New Service 추가**
   ```
   프로젝트 페이지에서:
   → "+ New" 버튼 클릭
   → "Database" 선택
   → "Add PostgreSQL" 클릭
   ```

3. **PostgreSQL 서비스 생성**
   - 자동으로 PostgreSQL 인스턴스가 생성됨
   - 환경 변수가 자동으로 주입됨

### 2️⃣ 환경 변수 확인 및 설정

Railway가 자동으로 제공하는 환경 변수:
- `DATABASE_URL`: PostgreSQL 연결 문자열
- `PGDATABASE`: 데이터베이스 이름
- `PGHOST`: 호스트 주소
- `PGPASSWORD`: 비밀번호
- `PGPORT`: 포트 번호
- `PGUSER`: 사용자명

### 3️⃣ 추가 환경 변수 설정

백엔드 서비스의 Variables 탭에서 추가:

```bash
# JWT 및 보안 설정
SECRET_KEY=your-very-long-random-secret-key-here
JWT_SECRET_KEY=another-very-long-random-jwt-key-here
ENCRYPTION_KEY=32-character-encryption-key-here

# Flask 환경
FLASK_ENV=production

# 이메일 설정 (선택사항 - 비밀번호 재설정용)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 4️⃣ 로컬 개발 환경 설정

`.env` 파일에 추가:

```bash
# 기존 API 키들...
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key

# 데이터베이스 (로컬 개발용)
DATABASE_URL=sqlite:///nongbuxx.db

# JWT 및 보안
SECRET_KEY=dev-secret-key-for-local-development
JWT_SECRET_KEY=dev-jwt-secret-key
ENCRYPTION_KEY=dev-encryption-key-32-chars-long

# Flask
FLASK_ENV=development
```

### 5️⃣ 데이터베이스 초기화 스크립트

`init_db.py` 생성:

```python
from app import app
from models import db

with app.app_context():
    # 모든 테이블 생성
    db.create_all()
    print("✅ 데이터베이스 테이블이 생성되었습니다.")
```

### 6️⃣ Railway에서 DB 초기화

1. **Railway CLI 사용**:
   ```bash
   railway run python init_db.py
   ```

2. **또는 Railway Shell**:
   ```bash
   railway shell
   python init_db.py
   exit
   ```

### 7️⃣ 데이터베이스 연결 테스트

```bash
# 로컬에서 Railway DB 연결 테스트
railway run python -c "from app import app, db; print('DB 연결 성공!' if db.engine.execute('SELECT 1').scalar() == 1 else 'DB 연결 실패')"
```

## 🔍 문제 해결

### PostgreSQL 연결 오류
- `DATABASE_URL`이 `postgres://`로 시작하면 `postgresql://`로 변경 필요
- config.py에 이미 처리 코드 포함됨

### 권한 오류
- Railway PostgreSQL은 자동으로 권한 설정됨
- 추가 설정 불필요

### 백업 및 복원
```bash
# 백업
railway run pg_dump $DATABASE_URL > backup.sql

# 복원
railway run psql $DATABASE_URL < backup.sql
```

## 📝 다음 단계

1. ✅ PostgreSQL 서비스 추가 완료
2. ✅ 환경 변수 설정 완료
3. ⏳ 데이터베이스 초기화
4. ⏳ 인증 API 구현
5. ⏳ 프론트엔드 통합 