# 🚀 NONGBUXX 완전 자동화 배포 가이드

## 📋 배포 시스템 개요

NONGBUXX의 새로운 배포 시스템은 **원클릭 배포**를 통해 모든 반복적인 문제들을 해결합니다.

### 🎯 **해결된 문제들**
- ✅ Railway.json 파일 손상 → 자동 복구
- ✅ CORS 설정 문제 → 자동 설정
- ✅ Vercel 도메인 alias 문제 → 자동 연결
- ✅ 분리된 배포 과정 → 통합 배포
- ✅ 배포 실패 시 수동 대응 → 자동 복구 및 롤백
- ✅ 복잡한 상태 확인 → 실시간 모니터링

---

## 🚀 핵심 배포 명령어 (이것만 기억하세요!)

### 1️⃣ **일반 배포 (가장 많이 사용)**
```bash
./deploy-all.sh "feat: 새로운 기능 추가"
```
> 프론트엔드 + 백엔드 + 검증을 한 번에 처리합니다.

### 2️⃣ **배포 상태 확인**
```bash
./deploy-status.sh
```
> 현재 서비스 상태를 한눈에 확인합니다.

### 3️⃣ **문제 발생 시 롤백**
```bash
./deploy-rollback.sh
```
> 이전 안정 버전으로 즉시 되돌립니다.

---

## 📚 전체 스크립트 가이드

### 🔍 **배포 전 검증**
```bash
./deploy-validate.sh
```
**기능:**
- Git 상태 확인
- 필수 파일 검증 및 자동 복구 (railway.json, vercel.json 등)
- CLI 도구 연결 상태 확인 (Railway, Vercel)
- Python/JavaScript 문법 검증
- 포트 사용 상태 확인

**언제 사용:** 배포 전 안전성 확인 또는 문제 진단 시

---

### 🚀 **통합 배포**
```bash
./deploy-all.sh "커밋 메시지"
```
**기능:**
- 사전 검증 및 설정 파일 자동 복구
- Git 커밋 및 푸시
- 백엔드 배포 (Railway) + 자동 재시도
- 프론트엔드 배포 (Vercel) + 도메인 연결
- 통합 검증 및 완료 리포트

**예시:**
```bash
./deploy-all.sh "feat: X API 인증 개선"
./deploy-all.sh "fix: 뉴스 추출 버그 수정"
./deploy-all.sh "update: UI 개선사항 적용"
```

---

### 📊 **배포 상태 확인**
```bash
./deploy-status.sh
```
**기능:**
- 백엔드 상태 확인 (헬스체크)
- 프론트엔드 상태 확인
- API 기능 테스트 (최신 코드 반영 여부)
- Git 커밋 정보
- Railway/Vercel 상세 정보

**언제 사용:** 배포 후 상태 확인, 문제 진단 시

---

### 📈 **실시간 모니터링**
```bash
./deploy-monitor.sh [시간(초)] [간격(초)]
```
**기능:**
- 지정된 시간 동안 서비스 상태 실시간 모니터링
- 백엔드, 프론트엔드, API 기능 연속 체크
- 실패 감지 시 자동 알림
- 성공률 통계 및 권장사항 제공

**예시:**
```bash
./deploy-monitor.sh               # 5분간 30초 간격 (기본값)
./deploy-monitor.sh 600 20        # 10분간 20초 간격
./deploy-monitor.sh 1800 60       # 30분간 1분 간격
```

---

### 🔄 **롤백 시스템**
```bash
./deploy-rollback.sh [옵션]
```
**기능:**
- Git 롤백 + 백엔드 재배포 + 프론트엔드 재배포
- 다양한 롤백 옵션 지원
- 롤백 후 자동 검증

**옵션:**
```bash
./deploy-rollback.sh             # 자동 롤백 (1개 커밋 되돌리기)
./deploy-rollback.sh 2           # 2개 커밋 되돌리기
./deploy-rollback.sh abc123      # 특정 커밋으로 롤백
./deploy-rollback.sh emergency   # 긴급 롤백 (최근 안정 버전)
```

---

## 🛠️ 개별 배포 명령어 (기존 유지)

프론트엔드나 백엔드만 따로 배포해야 하는 경우에만 사용:

### 프론트엔드만 배포
```bash
./deploy-quick.sh
```

### 백엔드만 배포
```bash
./deploy-backend-safe.sh "커밋 메시지"
```

---

## 📖 실전 사용 시나리오

### 🎯 **시나리오 1: 새 기능 개발 후 배포**
```bash
# 1. 개발 완료 후
git add .
git status                    # 변경사항 확인

# 2. 배포 전 검증 (선택사항)
./deploy-validate.sh

# 3. 통합 배포
./deploy-all.sh "feat: 사용자 인증 기능 추가"

# 4. 배포 후 모니터링 (선택사항)
./deploy-monitor.sh 300 30    # 5분간 모니터링
```

### 🚨 **시나리오 2: 문제 발생 시 긴급 대응**
```bash
# 1. 현재 상태 확인
./deploy-status.sh

# 2. 문제가 심각한 경우 즉시 롤백
./deploy-rollback.sh emergency

# 3. 롤백 후 상태 확인
./deploy-status.sh

# 4. 문제 원인 분석
git log --oneline -n 5
railway logs -n 50
```

### 🔧 **시나리오 3: 배포 실패 시 재시도**
```bash
# 1. 배포 실패 시 재검증
./deploy-validate.sh

# 2. 문제 수정 후 재배포
./deploy-all.sh "fix: 배포 설정 수정"

# 3. 지속적인 문제 시 개별 배포
./deploy-backend-safe.sh "fix: 백엔드 설정 수정"
./deploy-quick.sh
```

---

## 🌐 서비스 URL

배포 완료 후 다음 URL에서 서비스를 확인할 수 있습니다:

- **🌍 메인 사이트**: https://nongbuxxfrontend.vercel.app/
- **🔧 백엔드 API**: https://nongbuxxbackend-production.up.railway.app
- **💚 헬스체크**: https://nongbuxxbackend-production.up.railway.app/api/health

---

## 🔧 문제 해결 가이드

### ❓ **자주 발생하는 문제들**

#### 1. Railway CLI 연결 실패
```bash
railway login
railway status
```

#### 2. Vercel CLI 연결 실패
```bash
vercel login
vercel whoami
```

#### 3. 포트 충돌 오류
```bash
# 포트 정리 후 재시도
lsof -ti:8080 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
```

#### 4. Git 푸시 실패
```bash
git pull origin main          # 원격 변경사항 가져오기
git push origin main          # 다시 푸시
```

#### 5. 배포는 성공했지만 최신 코드 미반영
```bash
railway up --force            # 백엔드 강제 재배포
./deploy-quick.sh             # 프론트엔드 재배포
```

---

## 💡 **베스트 프랙티스**

### ✅ **권장사항**
1. **배포 전 검증**: `./deploy-validate.sh` 실행 습관화
2. **의미 있는 커밋 메시지**: `feat:`, `fix:`, `update:` 접두사 사용
3. **배포 후 확인**: `./deploy-status.sh`로 상태 점검
4. **점진적 배포**: 큰 변경사항은 작은 단위로 나누어 배포
5. **모니터링**: 중요한 배포 후에는 `./deploy-monitor.sh` 실행

### ❌ **주의사항**
1. 로컬 테스트 없이 바로 배포하지 마세요
2. 여러 기능을 한 번에 배포하지 마세요
3. 배포 실패 시 무작정 재시도하지 말고 `deploy-status.sh`로 진단하세요
4. 프로덕션에서 실험적 기능을 테스트하지 마세요

---

## 🎉 **배포 완료!**

이제 반복적인 배포 문제들이 모두 해결되었습니다!

### 🚀 **다음에 배포할 때는:**
```bash
./deploy-all.sh "변경사항 설명"
```
**단 한 줄로 모든 배포가 완료됩니다!**

### 📞 **추가 도움이 필요하면:**
- 각 스크립트에 `--help` 옵션 사용
- `./deploy-status.sh`로 현재 상태 확인
- `railway logs -f`로 실시간 로그 확인

---

**🎯 핵심: 이제 `./deploy-all.sh "메시지"`만 기억하면 됩니다!**
