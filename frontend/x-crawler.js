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
        
        // 인플루언서 목록 로드
        this.loadInfluencers();
        
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
        
        // X API 설정 - 읽기 권한
        document.getElementById('validateReadApiBtn')?.addEventListener('click', () => {
            this.validateXApi('read');
        });
        
        document.getElementById('saveReadApiBtn')?.addEventListener('click', () => {
            this.saveXApi('read');
        });
        
        document.getElementById('loadReadApiBtn')?.addEventListener('click', () => {
            this.loadXApi('read');
        });
        
        // X API 설정 - 쓰기 권한
        document.getElementById('useSameCredentials')?.addEventListener('change', (e) => {
            this.toggleWriteApiFields(e.target.checked);
        });
        
        document.getElementById('validateWriteApiBtn')?.addEventListener('click', () => {
            this.validateXApi('write');
        });
        
        document.getElementById('saveWriteApiBtn')?.addEventListener('click', () => {
            this.saveXApi('write');
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
            case 'statistics':
                this.loadStatistics();
                break;
        }
    },
    
    // X API 설정 관리
    async validateXApi(type) {
        const credentials = this.getXApiCredentials(type);
        
        if (!credentials.consumer_key || !credentials.consumer_secret || 
            !credentials.access_token || !credentials.access_token_secret) {
            this.showValidationResult(type, 'error', '모든 필드를 입력해주세요.');
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
                this.showValidationResult(type, 'success', 'X API 인증이 확인되었습니다!');
            } else {
                this.showValidationResult(type, 'error', result.error || '인증에 실패했습니다.');
            }
        } catch (error) {
            console.error('X API 인증 오류:', error);
            this.showValidationResult(type, 'error', '인증 확인 중 오류가 발생했습니다.');
        }
    },
    
    saveXApi(type) {
        const credentials = this.getXApiCredentials(type);
        
        if (type === 'read') {
            // 읽기 권한은 기존 x_credentials 키 사용 (호환성 유지)
            localStorage.setItem('x_credentials', btoa(JSON.stringify(credentials)));
            this.showNotification('읽기 권한 API 정보가 저장되었습니다.', 'success');
        } else {
            // 쓰기 권한은 별도 키 사용
            localStorage.setItem('x_write_credentials', btoa(JSON.stringify(credentials)));
            this.showNotification('쓰기 권한 API 정보가 저장되었습니다.', 'success');
        }
    },
    
    loadXApi(type) {
        let storedData;
        
        if (type === 'read') {
            storedData = localStorage.getItem('x_credentials');
        } else {
            storedData = localStorage.getItem('x_write_credentials');
        }
        
        if (storedData) {
            try {
                const credentials = JSON.parse(atob(storedData));
                this.setXApiCredentials(type, credentials);
                this.showNotification('저장된 API 정보를 불러왔습니다.', 'info');
            } catch (error) {
                console.error('API 정보 불러오기 오류:', error);
                this.showNotification('저장된 정보를 불러올 수 없습니다.', 'error');
            }
        } else {
            this.showNotification('저장된 API 정보가 없습니다.', 'info');
        }
    },
    
    getXApiCredentials(type) {
        const prefix = type === 'read' ? 'xRead' : 'xWrite';
        return {
            consumer_key: document.getElementById(`${prefix}ConsumerKey`)?.value || '',
            consumer_secret: document.getElementById(`${prefix}ConsumerSecret`)?.value || '',
            access_token: document.getElementById(`${prefix}AccessToken`)?.value || '',
            access_token_secret: document.getElementById(`${prefix}AccessTokenSecret`)?.value || ''
        };
    },
    
    setXApiCredentials(type, credentials) {
        const prefix = type === 'read' ? 'xRead' : 'xWrite';
        document.getElementById(`${prefix}ConsumerKey`).value = credentials.consumer_key || '';
        document.getElementById(`${prefix}ConsumerSecret`).value = credentials.consumer_secret || '';
        document.getElementById(`${prefix}AccessToken`).value = credentials.access_token || '';
        document.getElementById(`${prefix}AccessTokenSecret`).value = credentials.access_token_secret || '';
    },
    
    toggleWriteApiFields(useSame) {
        const writeFields = document.getElementById('writeApiFields');
        if (writeFields) {
            writeFields.style.display = useSame ? 'none' : 'block';
        }
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
    
    showValidationResult(type, status, message) {
        const resultElement = document.getElementById(`${type}ApiValidationResult`);
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
        const username = document.getElementById('influencerUsername')?.value;
        
        if (!username) {
            this.showNotification('사용자명을 입력해주세요.', 'error');
            return;
        }
        
        const influencer = {
            id: Date.now().toString(),
            username: username.startsWith('@') ? username : '@' + username,
            name: '',
            profileImage: 'https://via.placeholder.com/60',
            isActive: true,
            addedAt: new Date().toISOString(),
            lastFetched: null,
            stats: {
                followers: 0,
                posts: 0
            }
        };
        
        this.influencers.push(influencer);
        this.saveInfluencers();
        this.renderInfluencers();
        this.hideModal();
        
        this.showNotification('인플루언서가 추가되었습니다.', 'success');
    },
    
    saveInfluencers() {
        localStorage.setItem('x_crawler_influencers', JSON.stringify(this.influencers));
    },
    
    loadInfluencers() {
        const saved = localStorage.getItem('x_crawler_influencers');
        if (saved) {
            try {
                this.influencers = JSON.parse(saved);
            } catch (error) {
                console.error('인플루언서 목록 로드 오류:', error);
            }
        }
    },
    
    renderInfluencers() {
        // 인플루언서 카드 렌더링 로직
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
        // 상태 카드 업데이트
        this.updateStatusCards();
        
        // 타임라인 업데이트
        this.updateTimeline();
        
        // 게시 큐 업데이트
        this.updateQueue();
    },
    
    updateStatusCards() {
        // 실제 데이터로 업데이트하는 로직
    },
    
    updateTimeline() {
        // 오늘의 스케줄 업데이트
    },
    
    updateQueue() {
        // 게시 큐 업데이트
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
        // 읽기 권한 자동 로드
        this.loadXApi('read');
        
        // 쓰기 권한 자동 로드
        this.loadXApi('write');
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
