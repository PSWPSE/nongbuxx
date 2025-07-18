# 🔐 NONGBUXX 인증 API 문서

## 📋 개요

NONGBUXX 로그인 시스템은 JWT(JSON Web Token) 기반 인증을 사용합니다.
모든 인증이 필요한 API는 `Authorization: Bearer <token>` 헤더가 필요합니다.

## 🚀 API 엔드포인트

### 1. 인증 관련 API (`/api/auth`)

#### 회원가입
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "StrongPassword123!",
  "username": "username123"  // 선택사항
}

Response:
{
  "success": true,
  "message": "회원가입이 완료되었습니다.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username123",
    "created_at": "2025-07-18T12:00:00"
  },
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

#### 로그인
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "success": true,
  "message": "로그인되었습니다.",
  "user": { ... },
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

#### 로그아웃
```http
POST /api/auth/logout
Authorization: Bearer <access_token>

Response:
{
  "success": true,
  "message": "로그아웃되었습니다."
}
```

#### 토큰 갱신
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>

Response:
{
  "success": true,
  "access_token": "eyJ..."
}
```

#### 현재 사용자 정보
```http
GET /api/auth/me
Authorization: Bearer <access_token>

Response:
{
  "success": true,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username123",
    "is_active": true,
    "created_at": "2025-07-18T12:00:00"
  }
}
```

#### 이메일 중복 확인
```http
POST /api/auth/check-email
Content-Type: application/json

{
  "email": "user@example.com"
}

Response:
{
  "success": true,
  "available": false,
  "message": "이미 사용 중인 이메일입니다."
}
```

### 2. 사용자 관리 API (`/api/user`)

#### 프로필 조회
```http
GET /api/user/profile
Authorization: Bearer <access_token>

Response:
{
  "success": true,
  "user": { ... }
}
```

#### 프로필 수정
```http
PUT /api/user/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "username": "newusername"
}

Response:
{
  "success": true,
  "message": "프로필이 업데이트되었습니다.",
  "user": { ... }
}
```

### 3. API 키 관리 (`/api/user/api-keys`)

#### API 키 목록 조회
```http
GET /api/user/api-keys
Authorization: Bearer <access_token>

Response:
{
  "success": true,
  "api_keys": [
    {
      "id": 1,
      "provider": "anthropic",
      "masked_key": "sk-ant-api...xwAA",
      "created_at": "2025-07-18T12:00:00"
    }
  ]
}
```

#### API 키 저장/업데이트
```http
POST /api/user/api-keys
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "provider": "anthropic",  // 또는 "openai"
  "api_key": "sk-ant-api03-..."
}

Response:
{
  "success": true,
  "message": "Anthropic API 키가 저장되었습니다."
}
```

#### API 키 삭제
```http
DELETE /api/user/api-keys/anthropic
Authorization: Bearer <access_token>

Response:
{
  "success": true,
  "message": "Anthropic API 키가 삭제되었습니다."
}
```

#### API 키 테스트
```http
POST /api/user/api-keys/test
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "provider": "anthropic"
}

Response:
{
  "success": true,
  "message": "Anthropic API 키가 유효합니다.",
  "provider": "anthropic"
}
```

### 4. 콘텐츠 생성 API (인증 버전)

#### 콘텐츠 생성 (v2)
```http
POST /api/v2/generate
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "url": "https://example.com/article",
  "content_type": "standard",  // 또는 "blog", "x", "threads"
  "api_provider": "anthropic"  // 사용할 API 제공자
}

Response:
{
  "success": true,
  "job_id": "uuid",
  "data": {
    "success": true,
    "content": "...",
    "filename": "generated_content_20250718_120000.md"
  },
  "message": "콘텐츠가 생성되었습니다."
}
```

#### 사용자 생성 콘텐츠 목록
```http
GET /api/user/generated-content?page=1&per_page=20
Authorization: Bearer <access_token>

Response:
{
  "success": true,
  "data": {
    "contents": [
      {
        "id": 1,
        "url": "https://example.com/article",
        "content_type": "standard",
        "file_path": "generated_content_20250718_120000.md",
        "created_at": "2025-07-18T12:00:00"
      }
    ],
    "total": 50,
    "page": 1,
    "per_page": 20,
    "pages": 3
  }
}
```

## 🔒 인증 헤더

모든 보호된 엔드포인트는 다음 헤더가 필요합니다:
```
Authorization: Bearer <access_token>
```

## ⏱️ 토큰 만료 시간

- **Access Token**: 1시간
- **Refresh Token**: 30일

## 🔑 비밀번호 정책

- 최소 8자 이상
- 대문자 포함
- 소문자 포함
- 숫자 포함
- 특수문자 포함 (!@#$%^&*(),.?":{}|<>)

## 📝 에러 코드

| 코드 | 설명 |
|-----|------|
| `MISSING_FIELDS` | 필수 필드 누락 |
| `INVALID_EMAIL` | 잘못된 이메일 형식 |
| `WEAK_PASSWORD` | 약한 비밀번호 |
| `EMAIL_EXISTS` | 이미 등록된 이메일 |
| `INVALID_CREDENTIALS` | 잘못된 로그인 정보 |
| `TOKEN_EXPIRED` | 토큰 만료 |
| `INVALID_TOKEN` | 유효하지 않은 토큰 |
| `AUTHORIZATION_REQUIRED` | 인증 필요 |
| `API_KEY_NOT_SET` | API 키 미설정 |

## 🔄 마이그레이션 가이드

### 기존 사용자가 로그인 시스템으로 전환하는 방법:

1. **회원가입**: `/api/auth/register`로 계정 생성
2. **API 키 등록**: `/api/user/api-keys`로 기존 API 키 저장
3. **콘텐츠 생성**: 
   - 기존: `/api/generate` (API 키 직접 전달)
   - 신규: `/api/v2/generate` (저장된 API 키 사용)

### 프론트엔드 통합 예시:

```javascript
// 로그인
const login = async (email, password) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  if (data.success) {
    // 토큰 저장
    localStorage.setItem('access_token', data.tokens.access_token);
    localStorage.setItem('refresh_token', data.tokens.refresh_token);
  }
  return data;
};

// API 호출 (인증 포함)
const generateContent = async (url, contentType) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('/api/v2/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      url,
      content_type: contentType,
      api_provider: 'anthropic'
    })
  });
  
  return await response.json();
};
```

## 📌 중요 참고사항

1. **하위 호환성**: 기존 `/api/generate` 엔드포인트는 계속 작동합니다
2. **점진적 마이그레이션**: 사용자는 원하는 속도로 로그인 시스템으로 전환 가능
3. **API 키 보안**: 사용자 API 키는 암호화되어 데이터베이스에 저장됩니다
4. **세션 관리**: JWT는 stateless이므로 서버 재시작 시에도 유효합니다 