# 🎨 프론트엔드 로그인 UI 구현 계획

## 📋 구현 목록

### 1️⃣ 로그인/회원가입 모달

**필요한 컴포넌트:**
- 로그인 폼 (이메일, 비밀번호)
- 회원가입 폼 (이메일, 비밀번호, 사용자명)
- 탭 전환 (로그인 ↔ 회원가입)
- 에러 메시지 표시

**구현 위치:**
- `frontend/index.html` - 모달 HTML 추가
- `frontend/script.js` - 인증 로직 추가
- `frontend/styles.css` - 모달 스타일링

### 2️⃣ 헤더 사용자 정보

**변경사항:**
- 로그인 전: "로그인" 버튼
- 로그인 후: 사용자명 드롭다운
  - 프로필 설정
  - API 키 관리
  - 로그아웃

### 3️⃣ API 키 관리 페이지

**기능:**
- 저장된 API 키 목록
- 새 API 키 추가/수정
- API 키 테스트
- 삭제 기능

### 4️⃣ 토큰 관리 시스템

**구현 내용:**
- localStorage에 토큰 저장
- API 호출 시 자동 헤더 추가
- 토큰 만료 감지 및 갱신
- 로그아웃 시 토큰 삭제

## 🔨 구현 순서

### Step 1: 기본 인증 시스템 (auth.js)
```javascript
// frontend/auth.js
class AuthManager {
    constructor() {
        this.accessToken = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
    }
    
    async login(email, password) {
        const response = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        if (data.success) {
            this.saveTokens(data.tokens);
            this.user = data.user;
            localStorage.setItem('user', JSON.stringify(data.user));
        }
        return data;
    }
    
    async register(email, password, username) {
        // 회원가입 로직
    }
    
    saveTokens(tokens) {
        this.accessToken = tokens.access_token;
        this.refreshToken = tokens.refresh_token;
        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
    }
    
    async makeAuthRequest(url, options = {}) {
        if (!this.accessToken) {
            throw new Error('Not authenticated');
        }
        
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${this.accessToken}`
        };
        
        const response = await fetch(url, options);
        
        // 토큰 만료 시 갱신 시도
        if (response.status === 401) {
            await this.refreshAccessToken();
            options.headers.Authorization = `Bearer ${this.accessToken}`;
            return fetch(url, options);
        }
        
        return response;
    }
    
    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        this.accessToken = null;
        this.refreshToken = null;
        this.user = null;
        window.location.reload();
    }
}

const authManager = new AuthManager();
```

### Step 2: 로그인 모달 HTML
```html
<!-- frontend/index.html에 추가 -->
<div id="authModal" class="modal">
    <div class="modal-content">
        <span class="close">&times;</span>
        
        <!-- 탭 버튼 -->
        <div class="auth-tabs">
            <button class="tab-btn active" data-tab="login">로그인</button>
            <button class="tab-btn" data-tab="register">회원가입</button>
        </div>
        
        <!-- 로그인 폼 -->
        <div id="loginTab" class="tab-content active">
            <h2>로그인</h2>
            <form id="loginForm">
                <input type="email" id="loginEmail" placeholder="이메일" required>
                <input type="password" id="loginPassword" placeholder="비밀번호" required>
                <button type="submit">로그인</button>
                <div id="loginError" class="error-message"></div>
            </form>
        </div>
        
        <!-- 회원가입 폼 -->
        <div id="registerTab" class="tab-content">
            <h2>회원가입</h2>
            <form id="registerForm">
                <input type="email" id="registerEmail" placeholder="이메일" required>
                <input type="text" id="registerUsername" placeholder="사용자명 (선택)">
                <input type="password" id="registerPassword" placeholder="비밀번호" required>
                <div class="password-requirements">
                    • 최소 8자 이상<br>
                    • 대문자, 소문자, 숫자, 특수문자 포함
                </div>
                <button type="submit">가입하기</button>
                <div id="registerError" class="error-message"></div>
            </form>
        </div>
    </div>
</div>
```

### Step 3: API 키 관리 UI
```html
<!-- API 키 설정 모달 -->
<div id="apiKeyModal" class="modal">
    <div class="modal-content">
        <h2>API 키 관리</h2>
        
        <div class="api-key-section">
            <h3>Anthropic API Key</h3>
            <input type="password" id="anthropicKey" placeholder="sk-ant-api03-...">
            <button onclick="saveApiKey('anthropic')">저장</button>
            <button onclick="testApiKey('anthropic')">테스트</button>
        </div>
        
        <div class="api-key-section">
            <h3>OpenAI API Key</h3>
            <input type="password" id="openaiKey" placeholder="sk-...">
            <button onclick="saveApiKey('openai')">저장</button>
            <button onclick="testApiKey('openai')">테스트</button>
        </div>
        
        <div id="apiKeyMessage" class="message"></div>
    </div>
</div>
```

### Step 4: 기존 기능 통합
```javascript
// 콘텐츠 생성 시 인증 확인
async function generateContent() {
    if (!authManager.isAuthenticated()) {
        showAuthModal();
        return;
    }
    
    // 사용자의 저장된 API 키 사용
    const response = await authManager.makeAuthRequest(
        `${API_URL}/api/v2/generate`,
        {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: document.getElementById('urlInput').value,
                content_type: selectedContentType,
                api_provider: selectedProvider
            })
        }
    );
    
    // 응답 처리...
}
```

## 🎯 점진적 마이그레이션 전략

### Phase 1: 선택적 로그인
- 로그인 버튼 추가
- 기존 API 키 입력 방식 유지
- 로그인 사용자만 새 기능 사용

### Phase 2: 로그인 권장
- 로그인 사용자에게 혜택 제공
- 콘텐츠 이력 저장
- API 키 안전한 보관

### Phase 3: 로그인 필수
- 모든 기능에 로그인 요구
- 기존 API 키 입력 제거
- 완전한 사용자 시스템

## 📱 반응형 디자인 고려사항

- 모바일에서 모달 전체 화면
- 터치 친화적 버튼 크기
- 키보드 표시 시 스크롤

## 🔒 보안 고려사항

- HTTPS 필수
- 비밀번호 클라이언트 해싱 X
- XSS 방지 (입력값 검증)
- CSRF 토큰 (선택사항)

## 📊 구현 우선순위

1. **필수 (MVP)**
   - 로그인/회원가입 기능
   - 토큰 저장 및 사용
   - 로그아웃

2. **중요**
   - API 키 관리 UI
   - 토큰 자동 갱신
   - 에러 처리

3. **선택사항**
   - 비밀번호 찾기
   - 소셜 로그인
   - 2FA 인증

---

**예상 소요 시간:**
- 기본 인증: 1시간
- UI 구현: 1시간
- 통합 테스트: 1시간
- 총: 3시간 