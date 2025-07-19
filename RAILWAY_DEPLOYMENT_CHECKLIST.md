# 🚂 Railway 백엔드 배포 체크리스트 & 재발 방지 가이드

## 📋 배포 전 체크리스트

### 1. 로컬 테스트 ✅
```bash
# 백엔드 서버 시작
source venv/bin/activate
python3 app.py

# 새 기능 테스트 (예: X 타입)
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","api_provider":"anthropic","api_key":"your-key","content_type":"x"}'
```

### 2. Git 커밋 & 푸시 ✅
```bash
# 상태 확인
git status

# 커밋
git add .
git commit -m "feat: 기능 설명"

# 푸시
git push origin main
```

### 3. Railway 연동 확인 ✅
```bash
# Railway 프로젝트 상태
railway status

# GitHub 연동 확인
railway whoami
```

## 🚀 배포 프로세스

### 자동 배포 (기본)
1. `git push origin main` 실행
2. GitHub 웹훅이 Railway에 알림
3. Railway가 자동으로 빌드 및 배포
4. 약 2-5분 후 배포 완료

### 수동 배포 (자동 배포 실패 시)
```bash
# 옵션 1: CLI로 직접 배포
railway up --detach

# 옵션 2: 강제 재배포
railway up --force

# 옵션 3: 서비스 재시작
railway restart
```

## 📊 배포 후 확인사항

### 1. 배포 모니터링 스크립트 실행
```bash
chmod +x railway-deploy-monitor.sh
./railway-deploy-monitor.sh
```

### 2. 수동 검증
```bash
# 헬스체크
curl https://nongbuxxbackend-production.up.railway.app/api/health

# 새 기능 테스트
curl -X POST https://nongbuxxbackend-production.up.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -d '{"url":"test","api_provider":"anthropic","api_key":"sk-ant-test","content_type":"x"}'
```

### 3. 로그 확인
```bash
# 실시간 로그
railway logs -f

# 최근 100줄
railway logs -n 100

# 에러만 필터링
railway logs | grep -E "(ERROR|Error|error)"
```

## 🔧 문제 해결 가이드

### 문제 1: 자동 배포가 트리거되지 않음
**증상**: Git push 후에도 Railway가 재배포하지 않음

**해결책**:
1. Railway 대시보드에서 GitHub 연동 재설정
2. Settings → GitHub → Disconnect & Reconnect
3. 또는 수동 배포: `railway up --detach`

### 문제 2: 빌드는 성공했지만 코드가 반영되지 않음
**증상**: 배포 완료 메시지는 나왔지만 새 기능이 작동하지 않음

**해결책**:
```bash
# 빌드 캐시 무시하고 재배포
railway up --force

# Railway 환경 변수 재설정
railway variables --set "PYTHONDONTWRITEBYTECODE=1"
railway up
```

### 문제 3: "Content type must be..." 에러
**증상**: 새로 추가한 콘텐츠 타입이 인식되지 않음

**해결책**:
1. `app.py`의 콘텐츠 타입 검증 로직 확인
2. 로컬에서 정상 작동 확인
3. `railway up --force`로 강제 재배포

## 🛡️ 재발 방지 대책

### 1. 배포 자동화 개선
```bash
# deploy-backend.sh 스크립트 생성
#!/bin/bash
git add .
git commit -m "$1"
git push origin main

echo "⏳ 배포 대기 중 (2분)..."
sleep 120

# 자동 검증
./railway-deploy-monitor.sh
```

### 2. GitHub Actions 활용 (선택사항)
`.github/workflows/railway-deploy.yml`:
```yaml
name: Railway Deploy Check

on:
  push:
    branches: [main]

jobs:
  deploy-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Wait for Railway Deploy
        run: sleep 180
      - name: Check Deployment
        run: |
          curl -f https://nongbuxxbackend-production.up.railway.app/api/health
```

### 3. 배포 상태 대시보드
Railway 대시보드에서 실시간 모니터링:
- https://railway.app/project/[your-project-id]
- Deployments 탭에서 상태 확인
- Logs 탭에서 실시간 로그 확인

## 📌 Quick Reference

| 명령어 | 설명 |
|--------|------|
| `railway up` | 수동 배포 |
| `railway logs` | 로그 확인 |
| `railway status` | 프로젝트 상태 |
| `railway restart` | 서비스 재시작 |
| `railway variables` | 환경 변수 관리 |

## ⚡ 긴급 대응 매뉴얼

배포 실패 시 30초 내 복구:
```bash
# 1. 강제 재배포
railway up --force

# 2. 실패 시 이전 버전으로 롤백
git revert HEAD
git push origin main

# 3. Railway 대시보드에서 수동 롤백
# Deployments → 이전 성공 배포 → Redeploy
```

---

**💡 핵심**: Git push 후 2-3분 기다리고, `./railway-deploy-monitor.sh`로 확인! 