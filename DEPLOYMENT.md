# 🚀 NONGBUXX 배포 가이드

## 📋 배포 명령어 모음

### 🔥 빠른 배포 (가장 많이 사용)
```bash
./deploy-quick.sh
```
- 현재 변경사항을 즉시 Vercel에 배포
- 프로덕션 환경으로 배포
- 약 10-30초 소요

### 📊 배포 상태 확인
```bash
./deploy-status.sh
```
- 현재 배포 상태 확인
- 최근 배포 로그 확인
- 라이브 사이트 URL 표시

### 📜 실시간 로그 확인
```bash
./deploy-logs.sh
```
- 실시간 배포 로그 확인
- 에러 발생 시 디버깅 용도

## 🌐 배포된 사이트

- **프로덕션**: https://nongbuxxfrontend.vercel.app/
- **백엔드 API**: https://nongbuxxbackend-production.up.railway.app

## 💡 배포 팁

### ⚡ 개발 워크플로우
1. 로컬에서 개발 및 테스트
2. 변경사항 완료 후 `./deploy-quick.sh` 실행
3. 배포 완료 확인 후 라이브 사이트 테스트

### 🔧 문제 해결
- 배포 실패 시: `./deploy-status.sh`로 상태 확인
- 로그 확인 필요 시: `./deploy-logs.sh`로 실시간 확인
- 캐시 문제 시: 브라우저 새로고침 또는 시크릿 모드 사용

### 🎯 배포 전 체크리스트
- [ ] 로컬에서 정상 동작 확인
- [ ] 백엔드 API 연결 확인
- [ ] 모바일 반응형 확인
- [ ] 다크모드 정상 작동 확인

## 🛠️ 수동 배포 (필요시)
```bash
cd frontend
vercel --prod
```

## 📱 모바일 테스트
배포 후 반드시 모바일 환경에서도 테스트하세요:
- iOS Safari
- Android Chrome
- 반응형 디자인 확인

---

**🎉 이제 언제든지 `./deploy-quick.sh`로 쉽게 배포하세요!** 