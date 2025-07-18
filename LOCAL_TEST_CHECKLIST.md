# 📋 로컬 테스트 체크리스트

## 1️⃣ 서버 실행 테스트

### Step 1: 포트 정리 및 서버 시작
```bash
# 포트 8080 정리
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

# 인증 통합 서버 실행
python app_with_auth.py
```

**✅ 확인사항:**
- [ ] 서버가 정상적으로 시작되는가?
- [ ] "🔐 인증 시스템 초기화 완료" 메시지가 표시되는가?
- [ ] 데이터베이스 연결 성공 메시지가 나오는가?

### Step 2: 인증 API 테스트
```bash
# 새 터미널에서 실행
python test_auth.py
```

**✅ 확인사항:**
- [ ] 회원가입 테스트 통과
- [ ] 로그인 테스트 통과
- [ ] API 키 저장 테스트 통과
- [ ] 토큰 갱신 테스트 통과

## 2️⃣ 수동 API 테스트

### 회원가입 테스트
```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "username": "testuser"
  }'
```

### 로그인 테스트
```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

**💡 응답에서 access_token 복사하여 다음 테스트에 사용**

### API 키 저장 테스트
```bash
# YOUR_ACCESS_TOKEN을 실제 토큰으로 교체
curl -X POST http://localhost:8080/api/user/api-keys \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "provider": "anthropic",
    "api_key": "sk-ant-api03-YOUR-ACTUAL-KEY"
  }'
```

### 콘텐츠 생성 테스트 (v2 API)
```bash
curl -X POST http://localhost:8080/api/v2/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "url": "https://example.com",
    "content_type": "standard",
    "api_provider": "anthropic"
  }'
```

## 3️⃣ 기존 API 호환성 테스트

### 기존 방식 (인증 없이)
```bash
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "content_type": "standard",
    "api_provider": "anthropic",
    "api_key": "sk-ant-api03-YOUR-KEY"
  }'
```

**✅ 확인사항:**
- [ ] 기존 API가 여전히 작동하는가?
- [ ] 인증 없이도 사용 가능한가?

## 4️⃣ 프론트엔드 연동 테스트

### Frontend 서버 시작
```bash
# 새 터미널
cd frontend
python -m http.server 3000
```

### 브라우저 테스트
1. http://localhost:3000 접속
2. 개발자 도구 콘솔 열기
3. 기존 기능이 정상 작동하는지 확인

## 5️⃣ 데이터베이스 확인

### SQLite DB 확인
```bash
# Python 인터프리터에서
python
>>> from app_with_auth import app, db
>>> from models import User
>>> with app.app_context():
...     users = User.query.all()
...     print(f"총 사용자 수: {len(users)}")
```

## ⚠️ 일반적인 문제 해결

### 1. Import 에러
```bash
pip install -r requirements.txt
```

### 2. 포트 충돌
```bash
lsof -ti:8080 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
```

### 3. 데이터베이스 에러
```bash
# DB 초기화
rm -f nongbuxx_auth.db
python
>>> from app_with_auth import app, db
>>> with app.app_context():
...     db.create_all()
```

## ✅ 최종 확인 사항

- [ ] 모든 인증 API 정상 작동
- [ ] JWT 토큰 발급 및 검증 성공
- [ ] API 키 암호화 저장 확인
- [ ] 기존 API 하위 호환성 유지
- [ ] 에러 없이 서버 실행

---

**모든 테스트 통과 시 → Railway 배포 준비 완료!** 