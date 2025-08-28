// X API 캐시 완전 초기화 스크립트
// 브라우저 콘솔에서 실행하세요

function clearAllXCache() {
    console.log('🧹 X API 관련 모든 캐시를 초기화합니다...');
    
    // 1. X API 인증 캐시 삭제
    const cacheKey = 'x_auth_cache';
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
        const data = JSON.parse(cached);
        const age = Date.now() - data.timestamp;
        console.log(`📦 기존 캐시 발견 (${Math.round(age / 60000)}분 경과)`);
        localStorage.removeItem(cacheKey);
        console.log('✅ 인증 캐시 삭제 완료');
    } else {
        console.log('ℹ️ 인증 캐시가 없습니다');
    }
    
    // 2. Rate Limit 정보 확인
    console.log('\n📊 Rate Limit 정보:');
    console.log('- Free Tier: 75회/15분 (verify_credentials)');
    console.log('- 현재 시간:', new Date().toLocaleString('ko-KR'));
    console.log('- 15분 후:', new Date(Date.now() + 15 * 60 * 1000).toLocaleString('ko-KR'));
    
    // 3. 저장된 API 키 확인 (키 자체는 유지)
    const apiKeys = localStorage.getItem('x_api_credentials');
    if (apiKeys) {
        console.log('\n🔑 API 키는 저장되어 있습니다 (유지됨)');
    }
    
    // 4. 다음 단계 안내
    console.log('\n💡 다음 단계:');
    console.log('1. 15분 대기 (정확한 시간: ' + new Date(Date.now() + 15 * 60 * 1000).toLocaleTimeString('ko-KR') + ')');
    console.log('2. 페이지 새로고침 (F5)');
    console.log('3. X API 인증 확인 버튼 클릭 (1회만!)');
    console.log('4. 성공 시 15분간 추가 인증 확인 불필요');
    
    return '✅ 캐시 초기화 완료';
}

// 실행
clearAllXCache();

// Rate Limit 상태 추적 함수
function checkRateLimitStatus() {
    const lastAttempt = localStorage.getItem('last_x_api_attempt');
    if (lastAttempt) {
        const timePassed = Date.now() - parseInt(lastAttempt);
        const timeRemaining = Math.max(0, 15 * 60 * 1000 - timePassed);
        
        if (timeRemaining > 0) {
            const minutes = Math.floor(timeRemaining / 60000);
            const seconds = Math.floor((timeRemaining % 60000) / 1000);
            console.log(`⏰ Rate Limit 대기 시간: ${minutes}분 ${seconds}초 남음`);
            
            // 카운트다운
            const countdown = setInterval(() => {
                const now = Date.now() - parseInt(lastAttempt);
                const remaining = Math.max(0, 15 * 60 * 1000 - now);
                
                if (remaining === 0) {
                    console.log('✅ Rate Limit 리셋! 이제 API를 사용할 수 있습니다.');
                    clearInterval(countdown);
                } else {
                    const m = Math.floor(remaining / 60000);
                    const s = Math.floor((remaining % 60000) / 1000);
                    console.log(`⏰ ${m}:${s.toString().padStart(2, '0')} 남음`);
                }
            }, 1000);
            
            // 30초 후 자동 중지
            setTimeout(() => clearInterval(countdown), 30000);
        } else {
            console.log('✅ Rate Limit 대기 시간이 지났습니다. API 사용 가능!');
        }
    } else {
        console.log('ℹ️ 이전 API 시도 기록이 없습니다.');
    }
}

// Rate Limit 기록 함수
function recordApiAttempt() {
    localStorage.setItem('last_x_api_attempt', Date.now().toString());
    console.log('📝 API 시도 시간 기록됨');
}

console.log('\n💡 추가 명령어:');
console.log('- checkRateLimitStatus(): Rate Limit 상태 확인');
console.log('- recordApiAttempt(): API 시도 기록 (자동으로 호출됨)');
