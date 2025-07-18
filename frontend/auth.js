// NONGBUXX Authentication Manager
class AuthManager {
    constructor() {
        this.accessToken = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
        this.user = JSON.parse(localStorage.getItem('user') || 'null');
        this.apiUrl = window.CONFIG.API_URL || 'http://localhost:8080';
    }

    // 로그인 상태 확인
    isAuthenticated() {
        return !!this.accessToken && !!this.user;
    }

    // 로그인
    async login(email, password) {
        try {
            const response = await fetch(`${this.apiUrl}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (data.success) {
                this.saveTokens(data.tokens);
                this.user = data.user;
                localStorage.setItem('user', JSON.stringify(data.user));
                this.onAuthStateChanged(true);
            }

            return data;
        } catch (error) {
            console.error('Login error:', error);
            return {
                success: false,
                error: '로그인 중 오류가 발생했습니다.'
            };
        }
    }

    // 회원가입
    async register(email, password, username) {
        try {
            const response = await fetch(`${this.apiUrl}/api/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password, username })
            });

            const data = await response.json();

            if (data.success) {
                this.saveTokens(data.tokens);
                this.user = data.user;
                localStorage.setItem('user', JSON.stringify(data.user));
                this.onAuthStateChanged(true);
            }

            return data;
        } catch (error) {
            console.error('Register error:', error);
            return {
                success: false,
                error: '회원가입 중 오류가 발생했습니다.'
            };
        }
    }

    // 로그아웃
    async logout() {
        try {
            if (this.accessToken) {
                await fetch(`${this.apiUrl}/api/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.accessToken}`
                    }
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.clearAuth();
            this.onAuthStateChanged(false);
            window.location.reload();
        }
    }

    // 토큰 저장
    saveTokens(tokens) {
        this.accessToken = tokens.access_token;
        this.refreshToken = tokens.refresh_token;
        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
    }

    // 인증 정보 삭제
    clearAuth() {
        this.accessToken = null;
        this.refreshToken = null;
        this.user = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    }

    // 인증이 필요한 API 요청
    async makeAuthRequest(url, options = {}) {
        if (!this.accessToken) {
            throw new Error('인증이 필요합니다.');
        }

        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${this.accessToken}`
        };

        let response = await fetch(url, options);

        // 토큰 만료 시 갱신 시도
        if (response.status === 401 && this.refreshToken) {
            const refreshed = await this.refreshAccessToken();
            if (refreshed) {
                options.headers.Authorization = `Bearer ${this.accessToken}`;
                response = await fetch(url, options);
            } else {
                this.clearAuth();
                this.onAuthStateChanged(false);
                throw new Error('인증이 만료되었습니다. 다시 로그인해주세요.');
            }
        }

        return response;
    }

    // 액세스 토큰 갱신
    async refreshAccessToken() {
        try {
            const response = await fetch(`${this.apiUrl}/api/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.refreshToken}`
                }
            });

            const data = await response.json();
            if (data.success) {
                this.accessToken = data.access_token;
                localStorage.setItem('access_token', data.access_token);
                return true;
            }
        } catch (error) {
            console.error('Token refresh error:', error);
        }
        return false;
    }

    // 인증 상태 변경 콜백
    onAuthStateChanged(isAuthenticated) {
        // UI 업데이트는 외부에서 처리
        if (window.updateAuthUI) {
            window.updateAuthUI(isAuthenticated);
        }
    }

    // API 키 저장
    async saveApiKey(provider, apiKey) {
        try {
            const response = await this.makeAuthRequest(
                `${this.apiUrl}/api/user/api-keys`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ provider, api_key: apiKey })
                }
            );

            return await response.json();
        } catch (error) {
            console.error('Save API key error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // API 키 목록 조회
    async getApiKeys() {
        try {
            const response = await this.makeAuthRequest(
                `${this.apiUrl}/api/user/api-keys`
            );
            return await response.json();
        } catch (error) {
            console.error('Get API keys error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // API 키 테스트
    async testApiKey(provider) {
        try {
            const response = await this.makeAuthRequest(
                `${this.apiUrl}/api/user/api-keys/test`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ provider })
                }
            );

            return await response.json();
        } catch (error) {
            console.error('Test API key error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // 프로필 조회
    async getProfile() {
        try {
            const response = await this.makeAuthRequest(
                `${this.apiUrl}/api/user/profile`
            );
            return await response.json();
        } catch (error) {
            console.error('Get profile error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // 프로필 업데이트
    async updateProfile(data) {
        try {
            const response = await this.makeAuthRequest(
                `${this.apiUrl}/api/user/profile`,
                {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                }
            );
            
            const result = await response.json();
            if (result.success) {
                this.user = result.user;
                localStorage.setItem('user', JSON.stringify(result.user));
            }
            
            return result;
        } catch (error) {
            console.error('Update profile error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
}

// 전역 인스턴스 생성
window.authManager = new AuthManager(); 