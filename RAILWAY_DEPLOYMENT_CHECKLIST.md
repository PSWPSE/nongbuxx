# 🚂 Railway 배포 체크리스트

## 📋 배포 전 필수 확인사항

### 1️⃣ Railway 환경 변수 설정

Railway 대시보드 → nongbuxxbackend → Variables 탭에서 다음 변수들 추가:

```bash
# 이미 생성된 키들 (RAILWAY_ENV_VARS.txt 참조)
SECRET_KEY=TiAnYueCfjXCIPcz8P7LPi8XDpC1LCpR1E5glf13wN4
JWT_SECRET_KEY=MD1mIiR5pCnhpjhTNXklCY34gbgiPiv0mKsP6DHz_CU
ENCRYPTION_KEY=gtUN9kBcHB1fBHJLxdgvqNF0xIcQOnZE
FLASK_ENV=production

# DATABASE_URL은 PostgreSQL 추가 시 자동 설정됨
```

**⚠️ 중요: 각 변수 추가 후 "Add" 버튼 클릭!**

### 2️⃣ Procfile 수정 여부 결정

**옵션 A: 기존 유지 (하위 호환성 우선)**
```procfile
web: gunicorn app:app
```
- 장점: 안정적, 기존 사용자 영향 없음
- 단점: 로그인 기능 사용 불가

**옵션 B: 인증 버전 사용 (권장)**
```procfile
web: gunicorn app_with_auth:app
```
- 장점: 로그인 기능 활성화
- 단점: 철저한 테스트 필요

### 3️⃣ 코드 배포

```bash
# 1. 모든 변경사항 커밋
git add -A
git commit -m "feat: 로그인 시스템 통합"

# 2. main 브랜치로 머지
git checkout main
git merge feature/login-system

# 3. Railway로 푸시
git push origin main
```

### 4️⃣ 배포 모니터링

```bash
# 배포 상태 실시간 확인
./railway-deploy-monitor.sh

# 또는 Railway CLI로 직접 확인
railway logs -f
```

## 🧪 배포 후 테스트

### 1. 헬스체크
```bash
curl https://nongbuxxbackend-production.up.railway.app/api/health
```

### 2. 기존 API 테스트
```bash
curl -X POST https://nongbuxxbackend-production.up.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "content_type": "standard",
    "api_provider": "anthropic",
    "api_key": "YOUR-API-KEY"
  }'
```

### 3. 인증 API 테스트
```bash
# 회원가입
curl -X POST https://nongbuxxbackend-production.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "production@test.com",
    "password": "ProdPassword123!"
  }'
```

### 4. 데이터베이스 연결 확인
```bash
# Railway CLI로 데이터베이스 접속
railway run psql $DATABASE_URL

# 테이블 확인
\dt

# 사용자 수 확인
SELECT COUNT(*) FROM users;
```

## ⚠️ 롤백 계획

문제 발생 시:

### 옵션 1: 빠른 롤백
```bash
# Procfile을 원래대로 되돌리기
echo "web: gunicorn app:app" > Procfile
git add Procfile
git commit -m "rollback: 기존 app.py 사용"
git push origin main
```

### 옵션 2: 이전 커밋으로 롤백
```bash
# 백업 태그로 롤백
git checkout v1.0.0-before-auth
git checkout -b hotfix/rollback
git push origin hotfix/rollback:main --force
```

## 📊 성공 지표

- [ ] 모든 기존 API 정상 작동
- [ ] 인증 API 응답 정상
- [ ] 데이터베이스 연결 성공
- [ ] 에러 로그 없음
- [ ] 응답 시간 < 2초

## 🎯 점진적 마이그레이션 전략

### Phase 1: 소프트 런치 (현재)
- app_with_auth.py 배포
- 기존 사용자는 영향 없음
- 새 사용자만 로그인 사용

### Phase 2: 프론트엔드 통합
- 로그인 UI 추가
- 선택적 로그인 제공
- A/B 테스트

### Phase 3: 완전 전환
- 모든 사용자 로그인 필수
- 기존 API 단계적 폐기
- 완전한 인증 시스템

## 📝 배포 체크리스트

**배포 전:**
- [ ] 로컬 테스트 완료
- [ ] 환경 변수 설정
- [ ] Procfile 결정
- [ ] 롤백 계획 준비

**배포 중:**
- [ ] git push 성공
- [ ] Railway 빌드 성공
- [ ] 배포 로그 모니터링

**배포 후:**
- [ ] 헬스체크 통과
- [ ] API 테스트 통과
- [ ] DB 연결 확인
- [ ] 에러 모니터링

---

**⚡ 빠른 참조:**
- Railway 대시보드: https://railway.app/project/[YOUR-PROJECT-ID]
- 프로덕션 URL: https://nongbuxxbackend-production.up.railway.app
- 환경 변수: RAILWAY_ENV_VARS.txt 