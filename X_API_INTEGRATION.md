# X(Twitter) API 통합 가이드

## 📋 개요
NONGBUXX 서비스에 X(Twitter) API를 통한 자동 게시 기능이 추가되었습니다.
생성된 X(Twitter) 콘텐츠를 바로 X에 게시할 수 있습니다.

## 🚀 주요 기능

### 1. 콘텐츠 게시 기능
- **단일 트윗 게시**: 280자 이내 콘텐츠 직접 게시
- **스레드 게시**: 긴 콘텐츠를 여러 트윗으로 나누어 스레드 형태로 게시
- **자동 분할**: 280자 초과 콘텐츠 자동 분할 및 번호 매기기

### 2. API 인증 관리
- X API 인증 정보 안전한 저장 (LocalStorage)
- 인증 상태 실시간 확인
- 사용자 정보 표시

### 3. UI/UX 기능
- 미리보기 모달에서 바로 게시
- 실시간 글자 수 카운트
- 게시 진행 상태 표시
- 게시 결과 및 링크 제공

## 🔧 설정 방법

### 1. X Developer Portal 설정

1. [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard) 접속
2. 새 앱 생성 또는 기존 앱 선택
3. **User authentication settings** 설정:
   - App permissions: **Read and write** 선택 (필수)
   - Type of App: **Web App, Automated App or Bot** 선택
   - Callback URI: `http://localhost:3000` (개발용)
   - Website URL: 서비스 URL 입력

4. **Keys and tokens** 탭에서 다음 정보 복사:
   - API Key (Consumer Key)
   - API Secret (Consumer Secret)
   - Access Token
   - Access Token Secret

### 2. NONGBUXX 서비스 설정

1. 콘텐츠 생성 후 "생성된 콘텐츠" 탭으로 이동
2. X(Twitter) 콘텐츠 미리보기
3. "X에 게시" 버튼 클릭
4. API 인증 정보 입력:
   ```
   API Key: [Twitter Developer Portal에서 복사]
   API Secret: [Twitter Developer Portal에서 복사]
   Access Token: [Twitter Developer Portal에서 복사]
   Access Token Secret: [Twitter Developer Portal에서 복사]
   ```
5. "인증 확인" 버튼으로 연결 테스트
6. "저장" 버튼으로 인증 정보 저장

## 🔒 보안 고려사항

### API 키 보안
- **절대 공개 저장소에 API 키 업로드 금지**
- 프로덕션 환경에서는 환경 변수 사용 권장
- API 키는 브라우저 LocalStorage에 Base64 인코딩으로 저장
- 더 높은 보안이 필요한 경우 서버 측 키 관리 구현 필요

### 권한 관리
- X API 앱은 최소 필요 권한만 부여
- Read and write 권한만 사용 (DM 권한 불필요)
- 정기적으로 Access Token 재생성 권장

## 📝 사용 방법

### 1. 단일 트윗 게시
```
1. X(Twitter) 콘텐츠 생성
2. 생성된 콘텐츠 미리보기
3. "X에 게시" 버튼 클릭
4. 콘텐츠 확인 및 편집
5. "X에 게시" 버튼 클릭
```

### 2. 스레드 게시
```
1. 280자 초과 콘텐츠 생성
2. "긴 콘텐츠를 스레드로 게시" 옵션 체크
3. 자동 분할된 트윗 확인
4. "X에 게시" 버튼 클릭
```

## 🛠️ 기술 스택

### Backend
- **Python**: Flask 기반 API 서버
- **Tweepy**: X API v2 클라이언트 라이브러리
- **OAuth 1.0a**: X API 인증 프로토콜

### Frontend
- **JavaScript**: 바닐라 JS 기반 UI
- **LocalStorage**: API 키 클라이언트 저장
- **Fetch API**: 백엔드 통신

## 📊 API 엔드포인트

### POST /api/publish/x
X에 콘텐츠 게시

**Request:**
```json
{
  "content": "게시할 콘텐츠",
  "consumer_key": "API Key",
  "consumer_secret": "API Secret",
  "access_token": "Access Token",
  "access_token_secret": "Access Token Secret",
  "publish_as_thread": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "tweet_id": "1234567890",
    "tweet_url": "https://twitter.com/username/status/1234567890",
    "posted_at": "2025-01-13T10:00:00"
  }
}
```

### POST /api/validate/x-credentials
X API 인증 정보 검증

**Request:**
```json
{
  "consumer_key": "API Key",
  "consumer_secret": "API Secret",
  "access_token": "Access Token",
  "access_token_secret": "Access Token Secret"
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": "1234567890",
    "username": "username",
    "name": "Display Name"
  }
}
```

## 🚨 트러블슈팅

### 1. 인증 실패
- API 키가 올바른지 확인
- 앱 권한이 "Read and write"인지 확인
- Access Token이 만료되지 않았는지 확인

### 2. 게시 실패
- Rate limit 확인 (15분당 300개 트윗 제한)
- 콘텐츠 길이 확인 (280자 제한)
- 중복 콘텐츠 확인 (동일 내용 반복 게시 제한)

### 3. 스레드 게시 문제
- 각 트윗이 280자를 초과하지 않는지 확인
- 네트워크 연결 상태 확인
- API 응답 시간 초과 확인

## 📈 향후 개선 사항

### 계획된 기능
- [ ] 예약 게시 기능
- [ ] 미디어(이미지/동영상) 첨부
- [ ] 게시 히스토리 관리
- [ ] 다중 계정 관리
- [ ] 해시태그 자동 추천
- [ ] 게시 분석 통계

### 보안 개선
- [ ] 서버 측 API 키 관리
- [ ] OAuth 2.0 PKCE 플로우 구현
- [ ] API 키 암호화 강화
- [ ] 세션 기반 인증

## 📚 참고 자료

- [X API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [Tweepy Documentation](https://docs.tweepy.org/)
- [X Developer Portal](https://developer.twitter.com/en/portal/dashboard)
- [X API Rate Limits](https://developer.twitter.com/en/docs/twitter-api/rate-limits)

## 🤝 지원

문제가 발생하거나 도움이 필요한 경우:
1. GitHub Issues에 문제 제기
2. X API 공식 포럼 참조
3. Tweepy GitHub 이슈 확인

---

**⚠️ 주의사항**: X API 사용 시 [X Developer Agreement](https://developer.twitter.com/en/developer-terms/agreement-and-policy)를 준수해야 합니다.
