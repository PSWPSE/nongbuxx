# Railway 환경변수 설정 문제 해결 가이드

## 🔧 자주 발생하는 문제들

### 1. "Variables 탭이 안 보여요"
- **원인**: 잘못된 서비스 선택
- **해결**: 
  - PostgreSQL이 아닌 백엔드 서비스 선택
  - 서비스 이름에 "backend", "web", "app" 등이 포함된 것 선택

### 2. "환경변수 추가했는데도 JWT 에러가 나요"
- **원인**: 재배포가 안 됨
- **해결**:
  1. Variables 탭에서 변수 확인
  2. Deployments 탭에서 최신 배포 상태 확인
  3. 필요시 수동 재배포: Settings → Redeploy

### 3. "DATABASE_URL을 어디서 구하나요?"
- **답변**: PostgreSQL 서비스를 추가하지 않았다면 필요 없음
- 현재는 SQLite 사용 중이므로 DATABASE_URL 없어도 작동

### 4. "기존 API 키 변수를 덮어써도 되나요?"
- **답변**: 아니요! 기존 변수는 유지하고 새로 추가
- ANTHROPIC_API_KEY, OPENAI_API_KEY는 그대로 두세요

## 📋 체크리스트

환경변수 설정 후 확인:

- [ ] JWT_SECRET_KEY 추가됨
- [ ] SECRET_KEY 추가됨  
- [ ] ENCRYPTION_KEY 추가됨
- [ ] FLASK_ENV=production 추가됨
- [ ] 자동 재배포 시작됨 (2-3분 대기)

## 🚀 설정 완료 후 테스트

1. 터미널에서:
   ```bash
   python railway_env_check.py
   ```

2. 브라우저에서:
   - https://nongbuxxfrontend.vercel.app 접속
   - 우측 상단 "로그인" 클릭
   - 회원가입 → 로그인 → API 키 설정

## 💡 그래도 안 된다면?

1. **Railway 로그 확인**
   - Backend 서비스 → Logs 탭
   - 에러 메시지 확인

2. **환경변수 이중 확인**
   - 모든 변수가 정확히 입력되었는지
   - 특히 JWT_SECRET_KEY 값이 정확한지

3. **수동 재배포**
   - Settings 탭 → Redeploy 버튼 클릭 