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
        
        // 테마 토글 (메인과 동일한 방식)
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
        
        // 수동 수집 버튼 (중복 제거를 위해 기존 리스너 제거)
        const collectBtn = document.getElementById('manualCollectBtn');
        if (collectBtn) {
            // 기존 리스너 제거를 위해 새로운 버튼으로 교체
            const newCollectBtn = collectBtn.cloneNode(true);
            collectBtn.parentNode.replaceChild(newCollectBtn, collectBtn);
            newCollectBtn.addEventListener('click', () => {
                this.collectPosts();
            });
        }
        
        // 수동 게시 버튼
        document.getElementById('manualPublishBtn')?.addEventListener('click', () => {
            this.publishToX();
        });
        
        // 대시보드 새로고침 버튼
        document.getElementById('refreshDashboardBtn')?.addEventListener('click', async () => {
            const btn = document.getElementById('refreshDashboardBtn');
            if (btn) {
                btn.disabled = true;
                btn.textContent = '🔄 새로고침 중...';
                await this.updateDashboard();
                btn.disabled = false;
                btn.textContent = '🔄 새로고침';
                this.showNotification('대시보드가 업데이트되었습니다', 'info');
            }
        });
    },
    
    // 마지막 수집 결과 저장
    lastCollectionResult: null,
    
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
                
                // 수집 결과 저장
                this.lastCollectionResult = result.data;
                
                // 게시 버튼 표시
                const publishBtn = document.getElementById('manualPublishBtn');
                if (publishBtn && result.data.summary) {
                    publishBtn.style.display = 'inline-block';
                }
                
                // 인플루언서 목록 새로고침
                await this.loadInfluencers();
                if (this.currentSection === 'influencers') {
                    this.renderInfluencers();
                }
                
                // 대시보드 업데이트
                if (this.currentSection === 'dashboard') {
                    this.updateDashboard();
                    this.updateQueue(); // 큐 업데이트 추가
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
    
    // X에 게시
    async publishToX() {
        const statusDiv = document.getElementById('publishStatus');
        const publishBtn = document.getElementById('manualPublishBtn');
        
        // X API 자격증명 확인
        const credentials = localStorage.getItem('x_credentials');
        if (!credentials) {
            this.showNotification('X API 설정이 필요합니다.', 'error');
            return;
        }
        
        // 수집 결과 확인
        if (!this.lastCollectionResult) {
            this.showNotification('먼저 포스트를 수집해주세요.', 'error');
            return;
        }
        
        // 로딩 상태
        publishBtn.disabled = true;
        publishBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 게시 중...';
        statusDiv.className = 'publish-status loading';
        statusDiv.textContent = 'X에 게시하고 있습니다...';
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/x-crawler/publish`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Credentials': credentials
                },
                body: JSON.stringify({
                    content: {
                        text: this.lastCollectionResult.summary,
                        summary: this.lastCollectionResult.summary,
                        hashtags: this.lastCollectionResult.hashtags || []
                    }
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 성공
                statusDiv.className = 'publish-status success';
                statusDiv.innerHTML = `
                    <strong>✅ 게시 완료!</strong><br>
                    ${result.message}<br>
                    <a href="${result.data.url}" target="_blank" style="color: var(--x-primary);">
                        게시물 보기 →
                    </a>
                `;
                
                // 게시 버튼 숨기기
                publishBtn.style.display = 'none';
                
                // 수집 결과 초기화
                this.lastCollectionResult = null;
                
                this.showNotification('X에 성공적으로 게시되었습니다!', 'success');
            } else {
                // 실패
                statusDiv.className = 'publish-status error';
                statusDiv.textContent = `❌ 오류: ${result.error}`;
                this.showNotification(result.error || '게시 실패', 'error');
            }
        } catch (error) {
            console.error('게시 오류:', error);
            statusDiv.className = 'publish-status error';
            statusDiv.textContent = '❌ 게시 중 오류가 발생했습니다.';
            this.showNotification('게시 중 오류가 발생했습니다.', 'error');
        } finally {
            // 버튼 복원
            publishBtn.disabled = false;
            publishBtn.innerHTML = '<i class="fas fa-paper-plane"></i> X에 게시하기';
            
            // 5초 후 상태 메시지 숨기기
            setTimeout(() => {
                statusDiv.className = 'publish-status';
                statusDiv.textContent = '';
            }, 5000);
        }
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
    
    // X API 설정 관리 (디바운싱 추가)
    async validateXApi() {
        // 연속 호출 방지 (5초 쿨다운)
        if (this.isValidating) {
            this.showValidationResult('warning', '인증 확인 중입니다. 잠시 기다려주세요.');
            return;
        }
        
        const credentials = this.getXApiCredentials();
        
        if (!credentials.consumer_key || !credentials.consumer_secret || 
            !credentials.access_token || !credentials.access_token_secret) {
            this.showValidationResult('error', '모든 필드를 입력해주세요.');
            return;
        }
        
        // 디바운싱 플래그 설정
        this.isValidating = true;
        
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
        } finally {
            // 5초 후 플래그 해제
            setTimeout(() => {
                this.isValidating = false;
            }, 5000);
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
        // 자동 업데이트 제거 - 수동 새로고침 또는 이벤트 발생 시만 업데이트
        // API 호출 절약을 위해 주기적 업데이트 비활성화
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
                
                // 히스토리 업데이트
                await this.updateHistory();
                
                // 타임라인 업데이트 (최근 활동)
                if (stats.recent_activity) {
                    this.updateTimeline(stats.recent_activity);
                }
                
                // 게시 큐 업데이트
                this.updateQueue(stats);
            }
        } catch (error) {
            console.error('대시보드 업데이트 오류:', error);
        }
    },
    
    // 히스토리 업데이트
    async updateHistory() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/x-crawler/history`);
            const result = await response.json();
            
            if (result.success && result.data) {
                const history = result.data;
                this.historyData = history; // 히스토리 데이터 저장
                
                // 타임라인에 최근 활동 표시
                const container = document.querySelector('.timeline-items');
                if (container) {
                    container.innerHTML = '';
                    
                    // 수집 기록과 게시 기록을 합쳐서 시간순 정렬
                    const allEvents = [];
                    
                    // 수집 기록 추가
                    if (history.collections) {
                        history.collections.forEach(item => {
                            allEvents.push({
                                ...item,
                                type: 'collection',
                                icon: '📥',
                                description: `@${item.influencer}: ${item.posts_count}개 수집`
                            });
                        });
                    }
                    
                    // 게시 기록 추가
                    if (history.publishes) {
                        history.publishes.forEach(item => {
                            allEvents.push({
                                ...item,
                                type: 'publish',
                                icon: '📤',
                                description: '요약 게시 완료'
                            });
                        });
                    }
                    
                    // 시간순 정렬 (최신순)
                    allEvents.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
                    
                    // 최근 10개만 표시
                    allEvents.slice(0, 10).forEach(event => {
                        const item = document.createElement('div');
                        item.className = `timeline-item ${event.success ? 'completed' : 'failed'}`;
                        
                        const time = new Date(event.timestamp);
                        item.innerHTML = `
                            <span class="time">${time.toLocaleTimeString('ko-KR', {
                                hour: '2-digit',
                                minute: '2-digit'
                            })}</span>
                            <span class="status">${event.icon}</span>
                            <span class="description">${event.description}</span>
                        `;
                        
                        container.appendChild(item);
                    });
                }
            }
        } catch (error) {
            console.error('히스토리 업데이트 오류:', error);
        }
    },
    
    updateStatusCards(stats) {
        // 컴팩트 상태바 업데이트
        const overview = stats?.overview || {};
        const last24h = stats?.last_24h || {};
        const apiStatus = stats?.api_status || {};
        
        // 컴팩트 상태바 요소 업데이트
        const collectedEl = document.getElementById('statusCollected');
        if (collectedEl) collectedEl.textContent = overview.total_collected || 0;
        
        const pendingEl = document.getElementById('statusPending');
        if (pendingEl) pendingEl.textContent = this.publishQueue?.length || 0;
        
        const publishedEl = document.getElementById('statusPublished');
        if (publishedEl) publishedEl.textContent = overview.total_published || 0;
        
        const successRateEl = document.getElementById('statusSuccessRate');
        if (successRateEl) successRateEl.textContent = (last24h.success_rate || 100) + '%';
        
        // API 상태
        const xConnected = apiStatus.x_api?.connected;
        const aiConnected = apiStatus.ai_api?.connected;
        const apiIcon = document.getElementById('apiStatusIcon');
        const apiText = document.getElementById('apiStatusText');
        
        if (apiIcon && apiText) {
            if (xConnected && aiConnected) {
                apiIcon.textContent = '🟢';
                apiText.textContent = '정상';
            } else if (xConnected || aiConnected) {
                apiIcon.textContent = '🟡';
                apiText.textContent = '부분';
            } else {
                apiIcon.textContent = '🔴';
                apiText.textContent = '오프';
            }
        }
    },
    
    updateTimeline(stats) {
        const container = document.getElementById('scheduleTimeline') || document.querySelector('.timeline-items');
        if (!container) return;
        
        container.innerHTML = '';
        
        // 실제 데이터 기반 타임라인 생성
        const allEvents = [];
        const now = new Date();
        const today = now.toDateString();
        
        // 히스토리 데이터 (실제 실행된 이벤트)
        if (this.historyData) {
            // 수집 기록
            if (this.historyData.collections) {
                this.historyData.collections.forEach(item => {
                    const eventTime = new Date(item.timestamp);
                    if (eventTime.toDateString() === today) {
                        allEvents.push({
                            time: eventTime,
                            status: item.success ? '✅' : '❌',
                            description: `수집 ${item.success ? '완료' : '실패'} - @${item.influencer}`,
                            className: item.success ? 'completed' : 'failed'
                        });
                    }
                });
            }
            
            // 게시 기록
            if (this.historyData.publishes) {
                this.historyData.publishes.forEach(item => {
                    const eventTime = new Date(item.timestamp);
                    if (eventTime.toDateString() === today) {
                        allEvents.push({
                            time: eventTime,
                            status: item.success ? '✅' : '❌',
                            description: `게시 ${item.success ? '완료' : '실패'}`,
                            className: item.success ? 'completed' : 'failed'
                        });
                    }
                });
            }
        }
        
        // 예정된 스케줄
        if (stats?.scheduler?.next_schedules) {
            stats.scheduler.next_schedules.forEach(schedule => {
                const scheduleTime = new Date(schedule.next_run);
                if (scheduleTime.toDateString() === today && scheduleTime > now) {
                    const isUpcoming = scheduleTime - now < 30 * 60 * 1000;
                    allEvents.push({
                        time: scheduleTime,
                        status: isUpcoming ? '⏳' : '⏰',
                        description: schedule.job_type === 'collect' ? '수집 예정' : '게시 예정',
                        className: isUpcoming ? 'upcoming' : 'scheduled'
                    });
                }
            });
        }
        
        // 시간순 정렬
        allEvents.sort((a, b) => a.time - b.time);
        
        // 렌더링
        if (allEvents.length > 0) {
            allEvents.forEach(event => {
                const item = document.createElement('div');
                item.className = `timeline-item ${event.className}`;
                
                item.innerHTML = `
                    <span class="time">${event.time.toLocaleTimeString('ko-KR', {
                        hour: '2-digit',
                        minute: '2-digit'
                    })}</span>
                    <span class="status">${event.status}</span>
                    <span class="description">${event.description}</span>
                `;
                
                container.appendChild(item);
            });
        } else {
            container.innerHTML = '<div class="timeline-empty">오늘 예정된 스케줄이 없습니다</div>';
        }
    },
    
    updateQueue(stats) {
        const container = document.getElementById('queueItems');
        const emptyState = document.getElementById('queueEmpty');
        const queueCount = document.getElementById('queueCount');
        
        if (!container) return;
        
        // 대기 중인 콘텐츠 표시 (lastCollectionResult 사용)
        if (this.lastCollectionResult && this.lastCollectionResult.summary) {
            container.style.display = 'block';
            if (emptyState) emptyState.style.display = 'none';
            if (queueCount) queueCount.textContent = '1개 대기중';
            
            const summary = this.lastCollectionResult.summary;
            const hashtags = this.lastCollectionResult.hashtags || [];
            const preview = summary.substring(0, 100) + '...';
            
            container.innerHTML = `
                <div class="queue-item">
                    <div class="queue-time">즉시</div>
                    <div class="queue-content">
                        <h4>📱 AI 요약 콘텐츠</h4>
                        <p>${preview}</p>
                    </div>
                    <div class="queue-actions">
                        <button onclick="XCrawler.publishToX()">게시</button>
                    </div>
                </div>
            `;
        } else {
            container.style.display = 'none';
            if (emptyState) {
                emptyState.style.display = 'flex';
                emptyState.style.flexDirection = 'column';
                emptyState.style.alignItems = 'center';
                emptyState.style.padding = '2rem';
            }
            if (queueCount) queueCount.textContent = '0개 대기중';
        }
    },
    
    // 통계
    async loadStatistics() {
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/x-crawler/stats`);
            const result = await response.json();
            
            if (result.success && result.data) {
                const stats = result.data.crawler || result.data; // crawler 통계 우선 사용
                
                // 24시간 통계 업데이트
                const last24hColl = document.getElementById('last24hCollections');
                if (last24hColl) last24hColl.textContent = stats.last_24h?.collections || 0;
                
                const last24hPub = document.getElementById('last24hPublishes');
                if (last24hPub) last24hPub.textContent = stats.last_24h?.publishes || 0;
                
                const successRateEl = document.getElementById('successRate');
                if (successRateEl) successRateEl.textContent = (stats.last_24h?.success_rate || 100) + '%';
                
                // API 상태 업데이트
                const xConnected = stats.api_status?.x_api?.connected;
                const aiConnected = stats.api_status?.ai_api?.connected;
                const statusElement = document.getElementById('apiHealthStatus');
                
                if (statusElement) {
                    if (xConnected && aiConnected) {
                        statusElement.textContent = '🟢';
                    } else if (xConnected || aiConnected) {
                        statusElement.textContent = '🟡';
                    } else {
                        statusElement.textContent = '🔴';
                    }
                }
                
                // API 호출 통계 업데이트
                if (stats.api_calls) {
                    // 오늘 통계
                    const todayUserEl = document.getElementById('todayUserLookups');
                    if (todayUserEl) todayUserEl.textContent = stats.api_calls.today.user_lookups || 0;
                    
                    const todayTimelineEl = document.getElementById('todayTimelineFetches');
                    if (todayTimelineEl) todayTimelineEl.textContent = stats.api_calls.today.timeline_fetches || 0;
                    
                    const todayTotalEl = document.getElementById('todayTotalCalls');
                    if (todayTotalEl) todayTotalEl.textContent = stats.api_calls.today.total || 0;
                    
                    // 24시간 통계
                    const last24hUserEl = document.getElementById('last24hUserLookups');
                    if (last24hUserEl) last24hUserEl.textContent = stats.api_calls.last_24h.user_lookups || 0;
                    
                    const last24hTimelineEl = document.getElementById('last24hTimelineFetches');
                    if (last24hTimelineEl) last24hTimelineEl.textContent = stats.api_calls.last_24h.timeline_fetches || 0;
                    
                    const last24hTotalEl = document.getElementById('last24hTotalCalls');
                    if (last24hTotalEl) last24hTotalEl.textContent = stats.api_calls.last_24h.total || 0;
                }
                
                this.renderStatistics(stats);
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
    
    // 테마 관리 (메인과 통합된 시스템)
    initTheme() {
        // 메인과 동일한 키 사용하여 테마 동기화
        const savedTheme = localStorage.getItem('theme') || 'auto';
        
        if (savedTheme === 'auto') {
            // 시스템 테마 따르기
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
            this.updateThemeDisplay(prefersDark ? 'dark' : 'light', 'auto');
        } else {
            document.documentElement.setAttribute('data-theme', savedTheme);
            this.updateThemeDisplay(savedTheme, savedTheme);
        }
        
        // 시스템 테마 변경 감지
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            const currentTheme = localStorage.getItem('theme') || 'auto';
            if (currentTheme === 'auto') {
                const theme = e.matches ? 'dark' : 'light';
                document.documentElement.setAttribute('data-theme', theme);
                this.updateThemeDisplay(theme, 'auto');
            }
        });
    },
    
    toggleTheme() {
        // 메인과 동일한 3단계 토글: light -> dark -> auto
        const themes = ['light', 'dark', 'auto'];
        const currentSaved = localStorage.getItem('theme') || 'auto';
        const currentIndex = themes.indexOf(currentSaved);
        const nextIndex = (currentIndex + 1) % themes.length;
        const nextTheme = themes[nextIndex];
        
        localStorage.setItem('theme', nextTheme);
        
        if (nextTheme === 'auto') {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
            this.updateThemeDisplay(prefersDark ? 'dark' : 'light', 'auto');
        } else {
            document.documentElement.setAttribute('data-theme', nextTheme);
            this.updateThemeDisplay(nextTheme, nextTheme);
        }
    },
    
    updateThemeDisplay(actualTheme, savedTheme) {
        const icon = document.getElementById('themeIcon');
        const text = document.getElementById('themeText');
        
        if (icon && text) {
            if (savedTheme === 'auto') {
                icon.className = 'fas fa-adjust';
                text.textContent = '자동';
            } else if (actualTheme === 'dark') {
                icon.className = 'fas fa-sun';
                text.textContent = '라이트 모드';
            } else {
                icon.className = 'fas fa-moon';
                text.textContent = '다크 모드';
            }
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
