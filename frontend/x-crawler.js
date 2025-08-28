// X Crawler JavaScript
// 독립적인 네임스페이스로 기존 코드와 충돌 방지

const XCrawler = {
    // API 기본 URL
    API_BASE_URL: window.ENV?.API_BASE_URL || 'http://localhost:8080',
    
    // 한국 시간대 설정
    TIMEZONE: 'Asia/Seoul',
    
    // 현재 활성 섹션
    currentSection: 'dashboard',
    
    // 스케줄 설정
    scheduleConfig: {
        collection: {
            enabled: true,
            frequency: 'daily',
            times: ['09:00', '15:00', '21:00'],
            influencers: []
        },
        publishing: {
            enabled: true,
            mode: 'auto',
            delay: 60,
            times: ['10:00', '16:00', '22:00']
        }
    },
    
    // 인플루언서 목록
    influencers: [],
    
    // 게시 큐
    publishQueue: [],
    
    // 초기화
    init() {
        console.log('🚀 X Crawler 초기화 시작');
        
        // 이벤트 리스너 설정
        this.setupEventListeners();
        
        // X API 설정 로드
        this.loadXApiSettings();
        
        // 스케줄 설정 로드
        this.loadScheduleConfig();
        
        // 인플루언서 목록 로드 (백엔드에서)
        this.loadInfluencers().then(() => {
            console.log('✅ 인플루언서 목록 초기화 완료');
        });
        
        // 대시보드 초기화
        this.initDashboard();
        
        // 테마 설정
        this.initTheme();
    },
    
    // 이벤트 리스너 설정
    setupEventListeners() {
        // 메인으로 돌아가기
        document.getElementById('backToMainBtn')?.addEventListener('click', () => {
            window.location.href = './index.html';
        });
        
        // 메뉴 네비게이션
        document.querySelectorAll('.x-menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                this.switchSection(e.target.dataset.section);
            });
        });
        
        // X API 설정 (통합)
        document.getElementById('validateApiBtn')?.addEventListener('click', () => {
            this.validateXApi();
        });
        
        document.getElementById('saveApiBtn')?.addEventListener('click', () => {
            this.saveXApi();
        });
        
        document.getElementById('loadApiBtn')?.addEventListener('click', () => {
            this.loadXApi();
        });
        
        document.getElementById('deleteApiBtn')?.addEventListener('click', () => {
            this.deleteXApi();
        });
        
        // AI API 저장
        document.getElementById('saveAiApiBtn')?.addEventListener('click', () => {
            this.saveAiApi();
        });
        
        // AI API 불러오기
        document.getElementById('loadAiApiBtn')?.addEventListener('click', () => {
            this.loadAiApi();
        });
        
        // AI API 삭제
        document.getElementById('deleteAiApiBtn')?.addEventListener('click', () => {
            this.deleteAiApi();
        });
        
        // 비밀번호 토글
        document.querySelectorAll('.toggle-visibility').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.togglePasswordVisibility(e.target.dataset.target);
            });
        });
        
        // 스케줄 설정
        document.getElementById('saveScheduleBtn')?.addEventListener('click', () => {
            this.saveScheduleConfig();
        });
        
        document.getElementById('testScheduleBtn')?.addEventListener('click', () => {
            this.testSchedule();
        });
        
        // 인플루언서 추가
        document.getElementById('addInfluencerBtn')?.addEventListener('click', () => {
            this.showAddInfluencerModal();
        });
        
        document.getElementById('confirmAddInfluencerBtn')?.addEventListener('click', () => {
            this.addInfluencer();
        });
        
        // 모달 닫기
        document.querySelectorAll('.close-modal').forEach(btn => {
            btn.addEventListener('click', () => {
                this.hideModal();
            });
        });
        
        // 테마 토글
        document.getElementById('xThemeToggle')?.addEventListener('click', () => {
            this.toggleTheme();
        });
        
        // 수동 수집 버튼
        document.getElementById('manualCollectBtn')?.addEventListener('click', () => {
            this.collectPosts();
        });
    },
    
    // 포스트 수집
    async collectPosts() {
        const statusDiv = document.getElementById('collectionStatus');
        const collectBtn = document.getElementById('manualCollectBtn');
        
        // X API 자격증명 확인
        const credentials = localStorage.getItem('x_credentials');
        if (!credentials) {
            this.showNotification('X API 설정이 필요합니다. API 설정 메뉴에서 설정해주세요.', 'error');
            return;
        }
        
        // 인플루언서 확인
        if (this.influencers.length === 0) {
            this.showNotification('먼저 인플루언서를 추가해주세요.', 'error');
            return;
        }
        
        // AI API 설정 가져오기 (선택적)
        const aiProvider = localStorage.getItem('ai_provider');
        const aiKey = localStorage.getItem('ai_key');
        
        // 요청 데이터 준비
        const requestData = {};
        if (aiProvider && aiKey) {
            requestData.ai_provider = aiProvider;
            requestData.ai_key = aiKey;
        }
        
        // 로딩 상태
        collectBtn.disabled = true;
        collectBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 수집 중...';
        statusDiv.className = 'collection-status loading';
        statusDiv.textContent = '포스트를 수집하고 있습니다...';
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/x-crawler/collect`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Credentials': credentials
                },
                body: JSON.stringify(requestData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 성공
                let statusHtml = `
                    <strong>✅ 수집 완료!</strong><br>
                    ${result.message}<br>
                    <small>${result.data.influencers.map(inf => 
                        `@${inf.username}: ${inf.posts_collected}개`
                    ).join(', ')}</small>
                `;
                
                // AI 요약이 있으면 표시
                if (result.data.summary) {
                    statusHtml += `<br><br><strong>📝 AI 요약:</strong><br>${result.data.summary}`;
                    
                    if (result.data.hashtags && result.data.hashtags.length > 0) {
                        statusHtml += `<br><small>${result.data.hashtags.join(' ')}</small>`;
                    }
                }
                
                statusDiv.className = 'collection-status success';
                statusDiv.innerHTML = statusHtml;
                
                // 인플루언서 목록 새로고침
                await this.loadInfluencers();
                if (this.currentSection === 'influencers') {
                    this.renderInfluencers();
                }
                
                // 대시보드 업데이트
                if (this.currentSection === 'dashboard') {
                    this.updateDashboard();
                }
                
                // 수집된 포스트 표시 (선택적)
                if (result.data.posts && result.data.posts.length > 0) {
                    this.displayCollectedPosts(result.data.posts);
                }
                
                this.showNotification(result.message, 'success');
            } else {
                // 실패
                statusDiv.className = 'collection-status error';
                statusDiv.textContent = `❌ 오류: ${result.error}`;
                this.showNotification(result.error || '수집 실패', 'error');
            }
        } catch (error) {
            console.error('수집 오류:', error);
            statusDiv.className = 'collection-status error';
            statusDiv.textContent = '❌ 수집 중 오류가 발생했습니다.';
            this.showNotification('수집 중 오류가 발생했습니다.', 'error');
        } finally {
            // 버튼 복원
            collectBtn.disabled = false;
            collectBtn.innerHTML = '<i class="fas fa-sync-alt"></i> 수동 수집 실행';
            
            // 5초 후 상태 메시지 숨기기
            setTimeout(() => {
                statusDiv.className = 'collection-status';
                statusDiv.textContent = '';
            }, 5000);
        }
    },
    
    // 수집된 포스트 표시
    displayCollectedPosts(posts) {
        // 게시 큐에 포스트 샘플 표시
        const queueContainer = document.querySelector('.queue-items');
        if (!queueContainer || posts.length === 0) return;
        
        // 기존 내용 제거
        queueContainer.innerHTML = '';
        
        // 최대 3개만 표시
        posts.slice(0, 3).forEach((post, index) => {
            const item = document.createElement('div');
            item.className = 'queue-item';
            item.innerHTML = `
                <div class="queue-time">@${post.author}</div>
                <div class="queue-content">
                    <p>${post.text.substring(0, 100)}${post.text.length > 100 ? '...' : ''}</p>
                    <small>❤️ ${post.likes} 🔁 ${post.retweets}</small>
                </div>
            `;
            queueContainer.appendChild(item);
        });
    },
    
    // 섹션 전환
    switchSection(sectionName) {
        if (!sectionName) return;
        
        // 모든 섹션 숨기기
        document.querySelectorAll('.x-section').forEach(section => {
            section.classList.remove('active');
        });
        
        // 모든 메뉴 아이템 비활성화
        document.querySelectorAll('.x-menu-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // 선택된 섹션 표시
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
        }
        
        // 선택된 메뉴 활성화
        const targetMenu = document.querySelector(`.x-menu-item[data-section="${sectionName}"]`);
        if (targetMenu) {
            targetMenu.classList.add('active');
        }
        
        this.currentSection = sectionName;
        
        // 섹션별 초기화
        switch(sectionName) {
            case 'dashboard':
                this.updateDashboard();
                break;
            case 'influencers':
                this.loadInfluencers().then(() => {
                    this.renderInfluencers();
                });
                break;
            case 'statistics':
                this.loadStatistics();
                break;
        }
    },
    
    // X API 설정 관리
    async validateXApi() {
        const credentials = this.getXApiCredentials();
        
        if (!credentials.consumer_key || !credentials.consumer_secret || 
            !credentials.access_token || !credentials.access_token_secret) {
            this.showValidationResult('error', '모든 필드를 입력해주세요.');
            return;
        }
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/validate/x-credentials`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showValidationResult('success', 'X API 인증이 확인되었습니다!');
            } else {
                this.showValidationResult('error', result.error || '인증에 실패했습니다.');
            }
        } catch (error) {
            console.error('X API 인증 오류:', error);
            this.showValidationResult('error', '인증 확인 중 오류가 발생했습니다.');
        }
    },
    
    saveXApi() {
        const credentials = this.getXApiCredentials();
        
        if (!credentials.consumer_key || !credentials.consumer_secret || 
            !credentials.access_token || !credentials.access_token_secret) {
            this.showNotification('모든 필드를 입력해주세요.', 'error');
            return;
        }
        
        // 통합된 키로 저장 (기존 x_credentials 키 사용하여 호환성 유지)
        localStorage.setItem('x_credentials', btoa(JSON.stringify(credentials)));
        this.showNotification('X API 정보가 저장되었습니다.', 'success');
    },
    
    loadXApi() {
        const storedData = localStorage.getItem('x_credentials');
        
        if (storedData) {
            try {
                const credentials = JSON.parse(atob(storedData));
                this.setXApiCredentials(credentials);
                this.showNotification('저장된 X API 정보를 불러왔습니다.', 'info');
            } catch (error) {
                console.error('API 정보 불러오기 오류:', error);
                this.showNotification('저장된 정보를 불러올 수 없습니다.', 'error');
            }
        } else {
            this.showNotification('저장된 X API 정보가 없습니다.', 'info');
        }
    },
    
    deleteXApi() {
        if (confirm('저장된 X API 정보를 삭제하시겠습니까?')) {
            localStorage.removeItem('x_credentials');
            localStorage.removeItem('x_write_credentials'); // 구버전 호환성
            this.clearXApiFields();
            this.showNotification('X API 정보가 삭제되었습니다.', 'success');
        }
    },
    
    // AI API 저장
    saveAiApi() {
        const provider = document.getElementById('aiProvider').value;
        const apiKey = document.getElementById('aiApiKey').value;
        const statusDiv = document.getElementById('aiApiStatus');
        
        if (!provider || !apiKey) {
            statusDiv.className = 'validation-result error';
            statusDiv.textContent = '❌ AI 제공자와 API Key를 모두 입력해주세요';
            return;
        }
        
        // localStorage에 저장
        localStorage.setItem('ai_provider', provider);
        localStorage.setItem('ai_key', apiKey);
        
        statusDiv.className = 'validation-result success';
        statusDiv.textContent = '✅ AI API 정보가 저장되었습니다';
        
        this.showNotification('AI API 정보가 저장되었습니다', 'success');
    },
    
    // AI API 불러오기
    loadAiApi() {
        const provider = localStorage.getItem('ai_provider');
        const apiKey = localStorage.getItem('ai_key');
        const statusDiv = document.getElementById('aiApiStatus');
        
        if (provider && apiKey) {
            document.getElementById('aiProvider').value = provider;
            document.getElementById('aiApiKey').value = apiKey;
            
            statusDiv.className = 'validation-result success';
            statusDiv.textContent = '✅ AI API 정보를 불러왔습니다';
            
            this.showNotification('AI API 정보를 불러왔습니다', 'success');
        } else {
            statusDiv.className = 'validation-result error';
            statusDiv.textContent = '❌ 저장된 AI API 정보가 없습니다';
        }
    },
    
    // AI API 삭제
    deleteAiApi() {
        if (confirm('저장된 AI API 정보를 삭제하시겠습니까?')) {
            document.getElementById('aiProvider').value = '';
            document.getElementById('aiApiKey').value = '';
            localStorage.removeItem('ai_provider');
            localStorage.removeItem('ai_key');
            
            const statusDiv = document.getElementById('aiApiStatus');
            statusDiv.className = 'validation-result success';
            statusDiv.textContent = '✅ AI API 정보가 삭제되었습니다';
            
            this.showNotification('AI API 정보가 삭제되었습니다', 'success');
        }
    },
    
    getXApiCredentials() {
        return {
            consumer_key: document.getElementById('xConsumerKey')?.value || '',
            consumer_secret: document.getElementById('xConsumerSecret')?.value || '',
            access_token: document.getElementById('xAccessToken')?.value || '',
            access_token_secret: document.getElementById('xAccessTokenSecret')?.value || ''
        };
    },
    
    setXApiCredentials(credentials) {
        const consumerKey = document.getElementById('xConsumerKey');
        const consumerSecret = document.getElementById('xConsumerSecret');
        const accessToken = document.getElementById('xAccessToken');
        const accessTokenSecret = document.getElementById('xAccessTokenSecret');
        
        if (consumerKey) consumerKey.value = credentials.consumer_key || '';
        if (consumerSecret) consumerSecret.value = credentials.consumer_secret || '';
        if (accessToken) accessToken.value = credentials.access_token || '';
        if (accessTokenSecret) accessTokenSecret.value = credentials.access_token_secret || '';
    },
    
    clearXApiFields() {
        const consumerKey = document.getElementById('xConsumerKey');
        const consumerSecret = document.getElementById('xConsumerSecret');
        const accessToken = document.getElementById('xAccessToken');
        const accessTokenSecret = document.getElementById('xAccessTokenSecret');
        
        if (consumerKey) consumerKey.value = '';
        if (consumerSecret) consumerSecret.value = '';
        if (accessToken) accessToken.value = '';
        if (accessTokenSecret) accessTokenSecret.value = '';
    },
    

    
    togglePasswordVisibility(targetId) {
        const input = document.getElementById(targetId);
        const button = document.querySelector(`[data-target="${targetId}"]`);
        
        if (input && button) {
            if (input.type === 'password') {
                input.type = 'text';
                button.innerHTML = '<i class="fas fa-eye-slash"></i>';
            } else {
                input.type = 'password';
                button.innerHTML = '<i class="fas fa-eye"></i>';
            }
        }
    },
    
    showValidationResult(status, message) {
        const resultElement = document.getElementById('apiValidationResult');
        if (resultElement) {
            resultElement.className = `validation-result ${status}`;
            resultElement.textContent = message;
            resultElement.style.display = 'block';
            
            setTimeout(() => {
                resultElement.style.display = 'none';
            }, 5000);
        }
    },
    
    // 스케줄 관리
    saveScheduleConfig() {
        // 수집 스케줄 설정
        const collectionFrequency = document.querySelector('input[name="collection-frequency"]:checked')?.value;
        const collectionTimes = Array.from(document.querySelectorAll('.time-inputs input[type="time"]'))
            .map(input => input.value)
            .filter(time => time);
        
        // 게시 스케줄 설정
        const publishMode = document.querySelector('input[name="publish-mode"]:checked')?.value;
        const publishDelay = document.getElementById('publishDelay')?.value;
        
        this.scheduleConfig = {
            collection: {
                enabled: true,
                frequency: collectionFrequency,
                times: collectionTimes,
                influencers: this.influencers.map(i => i.username)
            },
            publishing: {
                enabled: true,
                mode: publishMode,
                delay: parseInt(publishDelay) || 60,
                times: []
            }
        };
        
        // localStorage에 저장
        localStorage.setItem('x_crawler_schedule', JSON.stringify(this.scheduleConfig));
        
        // 백엔드에 동기화
        this.syncScheduleWithBackend();
        
        this.showNotification('스케줄 설정이 저장되었습니다.', 'success');
    },
    
    async syncScheduleWithBackend() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/x-crawler/schedule`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.scheduleConfig)
            });
            
            const result = await response.json();
            if (result.success) {
                console.log('스케줄 백엔드 동기화 완료');
            }
        } catch (error) {
            console.error('스케줄 동기화 오류:', error);
        }
    },
    
    async testSchedule() {
        this.showNotification('테스트 실행 중...', 'info');
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/x-crawler/test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            if (result.success) {
                this.showNotification('테스트 실행 완료! 결과를 확인하세요.', 'success');
                this.updateDashboard();
            } else {
                this.showNotification('테스트 실행 실패: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('테스트 실행 오류:', error);
            this.showNotification('테스트 실행 중 오류가 발생했습니다.', 'error');
        }
    },
    
    loadScheduleConfig() {
        const saved = localStorage.getItem('x_crawler_schedule');
        if (saved) {
            try {
                this.scheduleConfig = JSON.parse(saved);
            } catch (error) {
                console.error('스케줄 설정 로드 오류:', error);
            }
        }
    },
    
    // 인플루언서 관리
    showAddInfluencerModal() {
        const modal = document.getElementById('addInfluencerModal');
        if (modal) {
            modal.style.display = 'flex';
        }
    },
    
    hideModal() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    },
    
    async addInfluencer() {
        const usernameInput = document.getElementById('influencerUsername');
        const username = usernameInput?.value?.trim();
        
        if (!username) {
            this.showNotification('사용자명을 입력해주세요.', 'error');
            return;
        }
        
        // @ 제거
        const cleanUsername = username.replace('@', '');
        
        try {
            // 백엔드에 추가 요청
            const response = await fetch(`${this.API_BASE_URL}/api/x-crawler/influencers`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: cleanUsername,
                    name: cleanUsername,
                    isActive: true
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 로컬 목록 업데이트
                await this.loadInfluencers();
                this.renderInfluencers();
                this.hideModal();
                
                // 입력 필드 초기화
                usernameInput.value = '';
                
                this.showNotification(result.message || '인플루언서가 추가되었습니다.', 'success');
            } else {
                this.showNotification(result.error || '추가 실패', 'error');
            }
        } catch (error) {
            console.error('인플루언서 추가 오류:', error);
            this.showNotification('인플루언서 추가 중 오류가 발생했습니다.', 'error');
        }
    },
    
    async removeInfluencer(influencerId) {
        if (!confirm('이 인플루언서를 삭제하시겠습니까?')) {
            return;
        }
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/x-crawler/influencers?id=${influencerId}`, {
                method: 'DELETE'
            });
            
            const result = await response.json();
            
            if (result.success) {
                await this.loadInfluencers();
                this.renderInfluencers();
                this.showNotification('인플루언서가 삭제되었습니다.', 'success');
            } else {
                this.showNotification(result.error || '삭제 실패', 'error');
            }
        } catch (error) {
            console.error('인플루언서 삭제 오류:', error);
            this.showNotification('삭제 중 오류가 발생했습니다.', 'error');
        }
    },
    
    saveInfluencers() {
        // 이제 백엔드에서 관리하므로 로컬 저장 불필요
    },
    
    async loadInfluencers() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/x-crawler/influencers`);
            const result = await response.json();
            
            if (result.success) {
                this.influencers = result.data || [];
                console.log(`✅ ${this.influencers.length}명의 인플루언서 로드됨`);
            }
        } catch (error) {
            console.error('인플루언서 목록 로드 오류:', error);
            this.influencers = [];
        }
    },
    
    renderInfluencers() {
        const container = document.querySelector('.influencer-grid');
        if (!container) return;
        
        // 기존 카드 제거 (추가 버튼 제외)
        const existingCards = container.querySelectorAll('.influencer-card:not(.add-new)');
        existingCards.forEach(card => card.remove());
        
        // 인플루언서 카드 생성
        this.influencers.forEach(influencer => {
            const card = document.createElement('div');
            card.className = 'influencer-card';
            card.innerHTML = `
                <div class="influencer-avatar">
                    <img src="${influencer.profileImage}" alt="@${influencer.username}">
                </div>
                <div class="influencer-info">
                    <h4>@${influencer.username}</h4>
                    <p>${influencer.name}</p>
                    <span class="status-badge ${influencer.isActive ? 'active' : 'inactive'}">
                        ${influencer.isActive ? '활성' : '비활성'}
                    </span>
                </div>
                <div class="influencer-stats">
                    <p>${influencer.stats?.postsCollected || 0} 포스트 수집됨</p>
                    <p>${influencer.lastFetched ? `마지막 수집: ${this.formatRelativeTime(influencer.lastFetched)}` : '아직 수집 안됨'}</p>
                </div>
                <div class="influencer-actions">
                    <button class="btn-small btn-toggle" data-id="${influencer.id}">
                        ${influencer.isActive ? '일시정지' : '활성화'}
                    </button>
                    <button class="btn-small btn-danger btn-delete" data-id="${influencer.id}">삭제</button>
                </div>
            `;
            
            // 추가 버튼 앞에 삽입
            const addButton = container.querySelector('.add-new');
            container.insertBefore(card, addButton);
        });
        
        // 이벤트 리스너 추가
        container.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.dataset.id;
                this.removeInfluencer(id);
            });
        });
        
        container.querySelectorAll('.btn-toggle').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const id = e.target.dataset.id;
                this.toggleInfluencerStatus(id);
            });
        });
    },
    
    formatRelativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = Math.floor((now - date) / 1000); // 초 단위
        
        if (diff < 60) return '방금 전';
        if (diff < 3600) return `${Math.floor(diff / 60)}분 전`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}시간 전`;
        return `${Math.floor(diff / 86400)}일 전`;
    },
    
    async toggleInfluencerStatus(influencerId) {
        // TODO: 백엔드 API 구현 후 연동
        console.log('Toggle status for:', influencerId);
    },
    
    // 대시보드
    initDashboard() {
        this.updateDashboard();
        // 1분마다 대시보드 업데이트
        setInterval(() => {
            if (this.currentSection === 'dashboard') {
                this.updateDashboard();
            }
        }, 60000);
    },
    
    // 한국 시간 포맷팅
    formatKoreanTime(date = new Date()) {
        return new Intl.DateTimeFormat('ko-KR', {
            timeZone: this.TIMEZONE,
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        }).format(date);
    },
    
    // 한국 시간으로 변환
    toKoreanTime(date = new Date()) {
        return new Date(date.toLocaleString("en-US", {timeZone: this.TIMEZONE}));
    },
    
    async updateDashboard() {
        try {
            // 백엔드에서 통계 가져오기
            const response = await fetch(`${this.API_BASE_URL}/api/x-crawler/stats`);
            const result = await response.json();
            
            if (result.success) {
                const stats = result.data;
                
                // 상태 카드 업데이트
                this.updateStatusCards(stats);
                
                // 타임라인 업데이트
                this.updateTimeline(stats);
                
                // 게시 큐 업데이트
                this.updateQueue(stats);
            }
        } catch (error) {
            console.error('대시보드 업데이트 오류:', error);
        }
    },
    
    updateStatusCards(stats) {
        // 수집 예정
        const collectingCount = document.querySelector('.status-card:nth-child(1) .status-count');
        if (collectingCount) {
            collectingCount.textContent = stats?.scheduler?.next_schedules?.filter(s => s.type === 'collection').length || 0;
        }
        
        // 게시 대기
        const pendingCount = document.querySelector('.status-card:nth-child(2) .status-count');
        if (pendingCount) {
            pendingCount.textContent = stats?.scheduler?.queue_size || 0;
        }
        
        // 완료
        const completedCount = document.querySelector('.status-card:nth-child(3) .status-count');
        if (completedCount) {
            completedCount.textContent = stats?.scheduler?.history_count || 0;
        }
    },
    
    updateTimeline(stats) {
        const container = document.querySelector('.timeline-items');
        if (!container || !stats?.scheduler?.next_schedules) return;
        
        container.innerHTML = '';
        
        stats.scheduler.next_schedules.forEach(schedule => {
            const item = document.createElement('div');
            item.className = 'timeline-item scheduled';
            
            const scheduleTime = new Date(schedule.next_run);
            const now = new Date();
            
            if (scheduleTime < now) {
                item.className = 'timeline-item completed';
            } else if (scheduleTime - now < 30 * 60 * 1000) {
                item.className = 'timeline-item upcoming';
            }
            
            item.innerHTML = `
                <span class="time">${scheduleTime.toLocaleTimeString('ko-KR', {hour: '2-digit', minute: '2-digit'})}</span>
                <span class="status">${scheduleTime < now ? '✅' : scheduleTime - now < 30 * 60 * 1000 ? '⏳' : '⏰'}</span>
                <span class="description">${schedule.name}</span>
            `;
            
            container.appendChild(item);
        });
    },
    
    updateQueue(stats) {
        // 게시 큐 업데이트 (추후 구현)
    },
    
    // 통계
    async loadStatistics() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/x-crawler/stats`);
            const stats = await response.json();
            
            if (stats.success) {
                this.renderStatistics(stats.data);
            }
        } catch (error) {
            console.error('통계 로드 오류:', error);
        }
    },
    
    renderStatistics(data) {
        // 통계 렌더링 로직
    },
    
    // X API 설정 로드
    loadXApiSettings() {
        const storedData = localStorage.getItem('x_credentials');
        if (storedData) {
            try {
                const credentials = JSON.parse(atob(storedData));
                this.setXApiCredentials(credentials);
                console.log('✅ X API 설정 자동 로드 완료');
            } catch (error) {
                console.error('X API 설정 로드 오류:', error);
            }
        }
    },
    
    // 테마 관리
    initTheme() {
        const savedTheme = localStorage.getItem('x_crawler_theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        this.updateThemeIcon(savedTheme);
    },
    
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('x_crawler_theme', newTheme);
        this.updateThemeIcon(newTheme);
    },
    
    updateThemeIcon(theme) {
        const icon = document.querySelector('#xThemeToggle i');
        if (icon) {
            icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
    },
    
    // 알림 표시
    showNotification(message, type = 'info') {
        // 간단한 알림 표시 (추후 토스트 UI로 개선 가능)
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        // 임시 알림 구현
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${type === 'success' ? '#17BF63' : type === 'error' ? '#E0245E' : '#1DA1F2'};
            color: white;
            border-radius: 8px;
            z-index: 10000;
            animation: slideIn 0.3s;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
};

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    XCrawler.init();
});

// 메인 페이지에서 X 크롤러 버튼 클릭 처리
if (document.getElementById('xCrawlerBtn')) {
    document.getElementById('xCrawlerBtn').addEventListener('click', () => {
        window.location.href = './x-crawler.html';
    });
}
