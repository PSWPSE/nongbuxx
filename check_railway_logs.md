# Railway 로그 확인 가이드

## 1. Railway Dashboard에서 로그 확인

### 접속 경로:
1. https://railway.app/dashboard
2. NONGBUXX 프로젝트 → Backend 서비스
3. **Logs 탭** 클릭

### 확인할 내용:
```
[2025-01-19 00:39:00] Starting Flask app...
[2025-01-19 00:39:01] * Running on http://0.0.0.0:8080
[2025-01-19 00:39:01] JWT_SECRET_KEY loaded: nongbuxx-jwt-secret... ← 이 부분 확인!
```

## 2. Railway CLI로 로그 확인 (터미널)

```bash
# Railway CLI 설치 (처음만)
npm install -g @railway/cli

# 로그인
railway login

# 프로젝트 연결
railway link

# 실시간 로그 보기
railway logs
```

## 3. 로그에서 찾아야 할 것:

### ✅ 정상적인 경우:
- "JWT_SECRET_KEY loaded from environment"
- "Database: SQLite initialized"
- "Flask app started successfully"

### ❌ 문제가 있는 경우:
- "JWT_SECRET_KEY not found, using default"
- "Environment variable error"
- "Token validation failed" 