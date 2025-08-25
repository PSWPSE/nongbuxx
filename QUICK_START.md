# ⚡ NONGBUXX 배포 빠른 시작 가이드

## 🎯 **이것만 기억하세요!**

### 📱 **일반 배포 (90% 사용)**
```bash
./deploy-all.sh "feat: 새로운 기능 추가"
```

### 🔍 **상태 확인**
```bash
./deploy-status.sh
```

### 🔄 **문제 시 롤백**
```bash
./deploy-rollback.sh
```

---

## 🚀 **첫 배포 테스트**

배포 시스템을 테스트해보려면:

```bash
# 1. 배포 전 검증 (문제 없는지 확인)
./deploy-validate.sh

# 2. 작은 변경사항으로 테스트 배포
echo "/* 배포 테스트 $(date) */" >> frontend/styles.css
./deploy-all.sh "test: 새로운 배포 시스템 테스트"

# 3. 배포 후 상태 확인
./deploy-status.sh

# 4. 5분간 모니터링
./deploy-monitor.sh 300 30
```

---

## 💡 **문제 해결**

### 🔧 **CLI 도구 설치 (필요한 경우)**
```bash
# Railway CLI
npm install -g @railway/cli
railway login

# Vercel CLI  
npm install -g vercel
vercel login

# jq (JSON 파서)
brew install jq  # macOS
```

### 🚨 **긴급 상황**
문제가 생기면 바로:
```bash
./deploy-rollback.sh emergency
```

---

## 📞 **도움말**
상세한 가이드: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**🎉 이제 원클릭 배포를 즐기세요!**
