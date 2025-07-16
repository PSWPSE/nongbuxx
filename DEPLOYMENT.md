# 🚀 NONGBUXX 배포 가이드

## 📋 배포 명령어 모음

### 🌐 프론트엔드 배포 (Vercel)
```bash
./deploy-quick.sh
```
- 프론트엔드를 Vercel에 배포
- 프로덕션 환경으로 배포
- 약 10-30초 소요

### 🚀 백엔드 배포 (Railway)
```bash
./deploy-railway.sh
```
- 백엔드를 Railway에 배포
- API 서버 배포
- 약 1-3분 소요

### 📊 배포 상태 확인
```bash
# Railway 백엔드 상태 확인
railway status

# Vercel 프론트엔드 상태 확인
vercel ls
```

### 📜 실시간 로그 확인
```bash
# Railway 백엔드 로그 확인
railway logs

# 로컬 백엔드 실행 시 로그 확인
tail -f logs/nongbuxx.log
```

## 🌐 배포된 사이트

- **프론트엔드**: https://nongbuxxfrontend.vercel.app/
- **백엔드 API**: https://nongbuxxbackend-production.up.railway.app
- **API 헬스체크**: https://nongbuxxbackend-production.up.railway.app/api/health

## 🔧 로컬 개발 서버

### 백엔드 실행
```bash
source venv/bin/activate
python3 app.py
# http://localhost:8080에서 실행
```

### 프론트엔드 실행
```bash
cd frontend
python3 -m http.server 3000
# http://localhost:3000에서 실행
```

## 💡 배포 팁

### ⚡ 개발 워크플로우
1. 로컬에서 개발 및 테스트
2. **프론트엔드 변경**: `./deploy-quick.sh` 실행
3. **백엔드 변경**: `./deploy-railway.sh` 실행
4. 배포 완료 확인 후 라이브 사이트 테스트

### 🔧 문제 해결
- 백엔드 에러 시: `railway logs`로 로그 확인
- 프론트엔드 에러 시: 브라우저 개발자 도구에서 API 호출 확인
- 캐시 문제 시: 브라우저 새로고침 또는 시크릿 모드 사용

### 🎯 배포 전 체크리스트
- [ ] 로컬에서 정상 동작 확인
- [ ] 백엔드 API 연결 확인 (`curl http://localhost:8080/api/health`)
- [ ] 프론트엔드에서 백엔드 API 호출 확인
- [ ] 모바일 반응형 확인
- [ ] 뉴스 추출 기능 정상 작동 확인

## 🛠️ 수동 배포 (필요시)

### Vercel 수동 배포
```bash
cd frontend
vercel --prod
```

### Railway 수동 배포
```bash
railway up
```

## 📱 모바일 테스트
배포 후 반드시 모바일 환경에서도 테스트하세요:
- iOS Safari
- Android Chrome
- 반응형 디자인 확인
- 뉴스 추출 기능 확인

## 🚨 포트 충돌 해결
개발 서버 실행 시 포트 충돌이 발생하면:
```bash
# 포트 정리
lsof -ti:8080 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
```

---

**🎉 이제 프론트엔드는 `./deploy-quick.sh`, 백엔드는 `./deploy-railway.sh`로 쉽게 배포하세요!** 