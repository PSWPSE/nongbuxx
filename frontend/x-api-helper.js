/**
 * X API Rate Limit 관리 도우미
 * 브라우저 콘솔에서 사용할 수 있는 유틸리티 함수들
 */

// 1. 전체 X API 상태 확인
function checkXApiStatus() {
    console.log('🔍 X API 상태 확인\n');
    
    // Rate Limit 상태
    const rateLimitStatus = checkRateLimit();
    if (rateLimitStatus.isLimited) {
        console.log('❌ Rate Limit 활성');
        console.log(`   ⏰ ${rateLimitStatus.message}`);
        console.log(`   📅 리셋 시간: ${rateLimitStatus.resetTime}`);
    } else {
        console.log('✅ Rate Limit 없음 - API 사용 가능');
    }
    
    // 캐시된 인증 정보
    const cachedAuth = getCachedXAuth();
    if (cachedAuth) {
        const age = Date.now() - cachedAuth.timestamp;
        const remaining = 900000 - age; // 15분
        console.log('\n📦 캐시된 인증 정보');
        console.log(`   👤 사용자: @${cachedAuth.user.username}`);
        console.log(`   ⏱️ 남은 시간: ${Math.round(remaining / 60000)}분`);
    } else {
        console.log('\n❌ 캐시된 인증 정보 없음');
    }
    
    // API 키 저장 여부
    const hasKeys = localStorage.getItem('x_api_credentials');
    console.log('\n🔑 API 키:', hasKeys ? '저장됨' : '없음');
    
    return {
        rateLimited: rateLimitStatus.isLimited,
        cached: !!cachedAuth,
        hasKeys: !!hasKeys
    };
}

// 2. Rate Limit 강제 해제 (주의해서 사용!)
function forceResetRateLimit() {
    console.log('⚠️ Rate Limit 강제 해제 중...');
    localStorage.removeItem('x_rate_limit_until');
    localStorage.removeItem('x_last_api_attempt');
    console.log('✅ Rate Limit 해제 완료');
    console.log('⚠️ 주의: 실제 서버의 Rate Limit은 여전히 활성일 수 있습니다!');
    console.log('💡 권장: 15-20분 대기 후 시도하세요.');
}

// 3. 모든 X API 캐시 초기화
function clearAllXApiCache() {
    console.log('🧹 X API 캐시 초기화 중...\n');
    
    const items = [
        'x_auth_cache',
        'x_rate_limit_until', 
        'x_last_api_attempt'
    ];
    
    items.forEach(key => {
        if (localStorage.getItem(key)) {
            localStorage.removeItem(key);
            console.log(`   ✅ ${key} 삭제됨`);
        }
    });
    
    console.log('\n✅ 캐시 초기화 완료');
    console.log('💡 다음 단계:');
    console.log('1. 15-20분 대기');
    console.log('2. 페이지 새로고침 (F5)');
    console.log('3. 인증 확인 버튼 1회만 클릭');
}

// 4. Rate Limit 카운트다운
function startRateLimitCountdown() {
    const status = checkRateLimit();
    
    if (!status.isLimited) {
        console.log('✅ Rate Limit이 없습니다. API 사용 가능!');
        return;
    }
    
    console.log('⏰ Rate Limit 카운트다운 시작...');
    console.log(`📅 리셋 시간: ${status.resetTime}`);
    
    const interval = setInterval(() => {
        const currentStatus = checkRateLimit();
        
        if (!currentStatus.isLimited) {
            console.log('\n🎉 Rate Limit 해제됨! API 사용 가능!');
            clearInterval(interval);
        } else {
            const minutes = Math.floor(currentStatus.remainingTime / 60000);
            const seconds = Math.floor((currentStatus.remainingTime % 60000) / 1000);
            console.log(`⏱️ ${minutes}:${seconds.toString().padStart(2, '0')} 남음`);
        }
    }, 1000);
    
    // 30초 후 자동 중지
    setTimeout(() => {
        clearInterval(interval);
        console.log('⏹️ 카운트다운 중지 (30초 경과)');
    }, 30000);
    
    return interval;
}

// 5. 안전한 재시도 가이드
function safeRetryGuide() {
    const status = checkXApiStatus();
    
    console.log('\n📋 안전한 재시도 가이드\n');
    
    if (status.rateLimited) {
        const rateLimitStatus = checkRateLimit();
        console.log('❌ 현재 Rate Limit 활성 중');
        console.log(`⏰ ${rateLimitStatus.message}`);
        console.log(`📅 ${rateLimitStatus.resetTime}에 재시도 가능`);
        console.log('\n💡 대기하는 동안:');
        console.log('- startRateLimitCountdown() 실행으로 남은 시간 확인');
        console.log('- 다른 탭/브라우저에서 API 호출 금지');
    } else if (status.cached) {
        console.log('✅ 캐시된 인증 정보 있음');
        console.log('💡 추가 인증 확인 불필요');
        console.log('👉 바로 X에 게시 가능');
    } else if (status.hasKeys) {
        console.log('🔑 API 키 저장됨');
        console.log('💡 인증 확인 가능');
        console.log('⚠️ 주의: 1회만 시도하세요!');
        console.log('\n실행 순서:');
        console.log('1. 페이지 새로고침 (F5)');
        console.log('2. X에 게시 모달 열기');
        console.log('3. 인증 확인 버튼 1회 클릭');
    } else {
        console.log('❌ API 키 없음');
        console.log('💡 먼저 X API 키를 입력하세요');
    }
}

// 6. 디버그 모드
function enableXApiDebug() {
    window.X_API_DEBUG = true;
    
    // 원래 fetch 함수 백업
    const originalFetch = window.fetch;
    
    // fetch 래퍼
    window.fetch = async function(...args) {
        const [url, options] = args;
        
        // X API 관련 요청만 로깅
        if (url && url.includes('/api/validate/x-credentials')) {
            console.group('🔍 X API 요청 감지');
            console.log('URL:', url);
            console.log('Method:', options?.method || 'GET');
            console.log('시간:', new Date().toLocaleTimeString('ko-KR'));
            console.groupEnd();
        }
        
        try {
            const response = await originalFetch(...args);
            
            if (url && url.includes('/api/validate/x-credentials')) {
                console.group(`📡 X API 응답: ${response.status}`);
                console.log('Status:', response.status, response.statusText);
                
                if (response.status === 429) {
                    console.error('⚠️ Rate Limit 도달!');
                    setRateLimit(1200000); // 20분
                }
                
                console.groupEnd();
            }
            
            return response;
        } catch (error) {
            console.error('X API 요청 실패:', error);
            throw error;
        }
    };
    
    console.log('🐛 X API 디버그 모드 활성화됨');
    console.log('💡 모든 X API 요청이 콘솔에 표시됩니다');
}

// 자동 실행: 현재 상태 표시
console.log('🚀 X API 도우미 로드됨\n');
console.log('사용 가능한 명령어:');
console.log('- checkXApiStatus(): 전체 상태 확인');
console.log('- clearAllXApiCache(): 캐시 초기화');
console.log('- startRateLimitCountdown(): 남은 시간 카운트다운');
console.log('- safeRetryGuide(): 안전한 재시도 가이드');
console.log('- forceResetRateLimit(): Rate Limit 강제 해제 (주의!)');
console.log('- enableXApiDebug(): 디버그 모드 활성화\n');

// 초기 상태 확인
checkXApiStatus();
