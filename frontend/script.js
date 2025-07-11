// 최적화된 JavaScript - 성능 개선 및 핵심 기능 중심
// 전역 변수
let currentJobId = null;
let currentData = null;
let currentBatchJobId = null;
let currentBatchData = null;
let extractedNews = [];
let selectedNewsUrls = [];
let generatedContentData = [];
let currentTheme = 'auto';
let urlInputCount = 1;
const maxUrlInputs = 10;
const API_BASE_URL = window.ENV?.API_BASE_URL || 'http://localhost:8081';

// DOM 요소 캐싱
const elements = {
    urlForm: document.getElementById('urlForm'),
    urlInputsContainer: document.getElementById('urlInputsContainer'),
    themeToggle: document.getElementById('themeToggle'),
    themeIcon: document.getElementById('themeIcon'),
    themeText: document.getElementById('themeText'),
    newsExtractorBtn: document.getElementById('newsExtractorBtn'),
    newsExtractorSection: document.getElementById('newsExtractorSection'),
    newsKeyword: document.getElementById('newsKeyword'),
    newsCount: document.getElementById('newsCount'),
    extractNewsBtn: document.getElementById('extractNewsBtn'),
    cancelNewsExtractorBtn: document.getElementById('cancelNewsExtractorBtn'),
    newsSelectionSection: document.getElementById('newsSelectionSection'),
    newsExtractionInfo: document.getElementById('newsExtractionInfo'),
    newsList: document.getElementById('newsList'),
    selectAllNewsBtn: document.getElementById('selectAllNewsBtn'),
    deselectAllNewsBtn: document.getElementById('deselectAllNewsBtn'),
    generateSelectedBtn: document.getElementById('generateSelectedBtn'),
    generatedContentListSection: document.getElementById('generatedContentListSection'),
    generatedContentList: document.getElementById('generatedContentList'),
    downloadAllGeneratedBtn: document.getElementById('downloadAllGeneratedBtn'),
    copyAllGeneratedBtn: document.getElementById('copyAllGeneratedBtn'),
    resetAllBtn: document.getElementById('resetAllBtn'),
    apiSettingsBtn: document.getElementById('apiSettingsBtn'),
    apiStatus: document.getElementById('apiStatus'),
    apiSettingsSection: document.getElementById('apiSettingsSection'),
    apiProviderSelect: document.getElementById('apiProviderSelect'),
    apiKeyInput: document.getElementById('apiKeyInput'),
    validateApiKeyBtn: document.getElementById('validateApiKeyBtn'),
    saveApiKeyBtn: document.getElementById('saveApiKeyBtn'),
    deleteApiKeyBtn: document.getElementById('deleteApiKeyBtn'),
    cancelApiSettingsBtn: document.getElementById('cancelApiSettingsBtn'),
    apiValidationResult: document.getElementById('apiValidationResult'),
    progressSection: document.getElementById('progressSection'),
    progressTitle: document.getElementById('progressTitle'),
    progressFill: document.getElementById('progressFill'),
    progressText: document.getElementById('progressText'),
    resultSection: document.getElementById('resultSection'),
    markdownPreview: document.getElementById('markdownPreview'),
    downloadBtn: document.getElementById('downloadBtn'),
    copyBtn: document.getElementById('copyBtn'),
    resetBtn: document.getElementById('resetBtn'),
    errorSection: document.getElementById('errorSection'),
    errorMessage: document.getElementById('errorMessage'),
    retryBtn: document.getElementById('retryBtn'),
    toastContainer: document.getElementById('toastContainer')
};

// 앱 초기화
document.addEventListener('DOMContentLoaded', function() {
    initEventListeners();
    loadApiSettings();
    initTheme();
    updateUrlInputButtons();
    initKeyboardShortcuts();
    loadUserPreferences();
    
    // 마크다운 라이브러리 확인
    if (typeof marked === 'undefined') {
        console.warn('마크다운 라이브러리를 로드할 수 없습니다.');
    }
});

// 이벤트 리스너 초기화
function initEventListeners() {
    // 폼 제출
    if (elements.urlForm) {
        elements.urlForm.addEventListener('submit', handleFormSubmit);
    }
    
    // 테마 토글
    if (elements.themeToggle) {
        elements.themeToggle.addEventListener('click', toggleTheme);
    }
    
    // 뉴스 추출 관련 (메인 흐름)
    if (elements.extractNewsBtn) {
        elements.extractNewsBtn.addEventListener('click', handleNewsExtraction);
    }
    
    // URL 직접 입력 관련 (서브 흐름)
    const directUrlBtn = document.getElementById('directUrlBtn');
    if (directUrlBtn) {
        directUrlBtn.addEventListener('click', showUrlInputSection);
    }
    const backToNewsExtractorBtn = document.getElementById('backToNewsExtractorBtn');
    if (backToNewsExtractorBtn) {
        backToNewsExtractorBtn.addEventListener('click', hideUrlInputSection);
    }
    const resetUrlInputBtn = document.getElementById('resetUrlInputBtn');
    if (resetUrlInputBtn) {
        resetUrlInputBtn.addEventListener('click', resetUrlInputForm);
    }
    if (elements.selectAllNewsBtn) {
        elements.selectAllNewsBtn.addEventListener('click', selectAllNews);
    }
    if (elements.deselectAllNewsBtn) {
        elements.deselectAllNewsBtn.addEventListener('click', deselectAllNews);
    }
    if (elements.generateSelectedBtn) {
        elements.generateSelectedBtn.addEventListener('click', handleGenerateSelectedNews);
    }
    
    // 생성된 콘텐츠 관련
    if (elements.downloadAllGeneratedBtn) {
        elements.downloadAllGeneratedBtn.addEventListener('click', downloadAllGeneratedContent);
    }
    if (elements.copyAllGeneratedBtn) {
        elements.copyAllGeneratedBtn.addEventListener('click', copyAllGeneratedContent);
    }
    if (elements.resetAllBtn) {
        elements.resetAllBtn.addEventListener('click', resetAllFeatures);
    }
    
    // 뉴스 정렬 관련
    const newsSortSelect = document.getElementById('newsSortSelect');
    if (newsSortSelect) {
        newsSortSelect.addEventListener('change', handleNewsSortChange);
    }
    
    // API 설정 관련
    if (elements.apiSettingsBtn) {
        elements.apiSettingsBtn.addEventListener('click', showApiSettingsSection);
    }
    if (elements.apiProviderSelect) {
        elements.apiProviderSelect.addEventListener('change', onApiProviderChange);
    }
    if (elements.apiKeyInput) {
        elements.apiKeyInput.addEventListener('input', onApiKeyInput);
    }
    if (elements.validateApiKeyBtn) {
        elements.validateApiKeyBtn.addEventListener('click', validateApiKey);
    }
    if (elements.saveApiKeyBtn) {
        elements.saveApiKeyBtn.addEventListener('click', saveApiKey);
    }
    if (elements.deleteApiKeyBtn) {
        elements.deleteApiKeyBtn.addEventListener('click', deleteApiKey);
    }
    if (elements.cancelApiSettingsBtn) {
        elements.cancelApiSettingsBtn.addEventListener('click', hideApiSettingsSection);
    }
    
    // 기타 버튼들
    if (elements.downloadBtn) {
        elements.downloadBtn.addEventListener('click', downloadFile);
    }
    if (elements.copyBtn) {
        elements.copyBtn.addEventListener('click', copyToClipboard);
    }
    if (elements.resetBtn) {
        elements.resetBtn.addEventListener('click', resetForm);
    }
    if (elements.retryBtn) {
        elements.retryBtn.addEventListener('click', retryGeneration);
    }
}

// URL 입력 관리
function addUrlInput(currentIndex) {
    if (urlInputCount >= maxUrlInputs) {
        showToast(`최대 ${maxUrlInputs}개의 URL까지 입력할 수 있습니다.`, 'warning');
        return;
    }
    
    const newIndex = urlInputCount;
    const urlInputRow = document.createElement('div');
    urlInputRow.className = 'url-input-row';
    urlInputRow.setAttribute('data-index', newIndex);
    
    urlInputRow.innerHTML = `
        <div class="form-group">
            <div class="input-with-buttons">
                <input 
                    type="url" 
                    id="urlInput-${newIndex}" 
                    name="urlInput[]"
                    placeholder="https://news.example.com/article"
                    required
                    data-clicked="false"
                >
                <button type="button" class="btn btn-icon add-url-btn" onclick="addUrlInput(${newIndex})">
                    <i class="fas fa-plus"></i>
                </button>
                <button type="button" class="btn btn-icon remove-url-btn" onclick="removeUrlInput(${newIndex})">
                    <i class="fas fa-minus"></i>
                </button>
            </div>
        </div>
    `;
    
    elements.urlInputsContainer.appendChild(urlInputRow);
    urlInputCount++;
    updateUrlInputButtons();
}

function removeUrlInput(index) {
    const urlInputRow = document.querySelector(`[data-index="${index}"]`);
    if (urlInputRow) {
        urlInputRow.remove();
        urlInputCount--;
        updateUrlInputButtons();
    }
}

function updateUrlInputButtons() {
    const rows = document.querySelectorAll('.url-input-row');
    rows.forEach((row, index) => {
        const addBtn = row.querySelector('.add-url-btn');
        const removeBtn = row.querySelector('.remove-url-btn');
        
        if (addBtn) {
            addBtn.style.display = (index === rows.length - 1 && urlInputCount < maxUrlInputs) ? 'block' : 'none';
        }
        if (removeBtn) {
            removeBtn.style.display = rows.length > 1 ? 'block' : 'none';
        }
    });
}

function getAllUrls() {
    return Array.from(document.querySelectorAll('input[name="urlInput[]"]'))
        .map(input => input.value.trim())
        .filter(url => url);
}

// 폼 제출 처리
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const urls = getAllUrls();
    if (urls.length === 0) {
        showToast('최소 하나의 URL을 입력해주세요.', 'error');
        return;
    }
    
    // 유효한 URL인지 확인
    const invalidUrls = urls.filter(url => !isValidUrl(url));
    if (invalidUrls.length > 0) {
        showToast('유효하지 않은 URL이 있습니다.', 'error');
        return;
    }
    
    // API 키 확인
    const apiSettings = getApiSettings();
    if (!apiSettings.provider || !apiSettings.key) {
        showToast('API 키를 먼저 설정해주세요.', 'error');
        return;
    }
    
    try {
        hideAllSections();
        showProgressSection();
        
        // 프로그레스 시뮬레이션 시작 (단일 URL: 30초 예상)
        startProgressSimulation(30000);
        
        const response = await fetch(`${API_BASE_URL}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                url: urls[0], // 단일 URL 전송
                api_provider: apiSettings.provider,
                api_key: apiSettings.key
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.job_id) {
            currentJobId = result.job_id;
            pollJobStatus(result.job_id);
        } else {
            throw new Error('작업 ID를 받지 못했습니다.');
        }
        
    } catch (error) {
        console.error('Error:', error);
        stopProgressSimulation();
        showErrorSection(error.message);
    }
}

// 작업 상태 폴링
async function pollJobStatus(jobId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/status/${jobId}`);
        const result = await response.json();
        
        if (result.status === 'completed') {
            completeProgress();
            currentData = result.data;
            setTimeout(() => {
                showResultSection();
                showToast('콘텐츠 생성이 완료되었습니다!', 'success');
            }, 500); // 프로그레스 완료 애니메이션 후 결과 표시
        } else if (result.status === 'failed') {
            stopProgressSimulation();
            showErrorSection(result.error || '작업이 실패했습니다.');
        } else if (result.status === 'in_progress') {
            // 백엔드에서 실제 progress가 있으면 사용, 없으면 시뮬레이션 계속
            if (result.progress && result.progress > simulatedProgress) {
                updateProgress(result.progress);
            }
            setTimeout(() => pollJobStatus(jobId), 1000);
        }
    } catch (error) {
        console.error('Error polling job status:', error);
        showErrorSection('작업 상태를 확인하는 중 오류가 발생했습니다.');
    }
}

// 섹션 표시/숨기기
function hideAllSections() {
    const sections = [
        elements.progressSection,
        elements.resultSection,
        elements.errorSection,
        elements.newsSelectionSection,
        elements.generatedContentListSection
    ];
    
    sections.forEach(section => {
        if (section) section.style.display = 'none';
    });
    
    // URL 입력 섹션 숨기기
    const urlInputSection = document.getElementById('urlInputSection');
    if (urlInputSection) {
        urlInputSection.style.display = 'none';
    }
    
    // 메인 뉴스 추출 섹션은 항상 표시
    const newsExtractorSection = document.getElementById('newsExtractorSection');
    if (newsExtractorSection) {
        newsExtractorSection.style.display = 'block';
    }
}

function showProgressSection() {
    hideAllSections();
    if (elements.progressSection) {
        elements.progressSection.style.display = 'block';
    }
    
    // 프로그레스 바 초기화
    updateProgress(0);
}

// 프로그레스 바 시뮬레이션 관련 변수
let progressTimer = null;
let simulatedProgress = 0;
let estimatedDuration = 30000; // 30초 기본 예상 시간

function updateProgress(percentage) {
    if (elements.progressFill) {
        elements.progressFill.style.width = `${percentage}%`;
    }
    if (elements.progressText) {
        elements.progressText.textContent = `${Math.round(percentage)}%`;
    }
}

function startProgressSimulation(duration = 30000) {
    // 기존 타이머 정리
    if (progressTimer) {
        clearInterval(progressTimer);
    }
    
    simulatedProgress = 0;
    estimatedDuration = duration;
    
    // 100ms마다 진행률 업데이트
    progressTimer = setInterval(() => {
        // 90%까지는 빠르게, 90% 이후는 천천히 진행
        if (simulatedProgress < 90) {
            simulatedProgress += Math.random() * 2 + 0.5; // 0.5-2.5% 증가
        } else {
            simulatedProgress += Math.random() * 0.5 + 0.1; // 0.1-0.6% 증가
        }
        
        // 95%에서 정지 (실제 완료 시까지 대기)
        if (simulatedProgress >= 95) {
            simulatedProgress = 95;
        }
        
        updateProgress(simulatedProgress);
    }, 100);
}

function stopProgressSimulation() {
    if (progressTimer) {
        clearInterval(progressTimer);
        progressTimer = null;
    }
}

function completeProgress() {
    stopProgressSimulation();
    
    // 부드러운 완료 애니메이션
    const targetProgress = 100;
    const currentProgress = simulatedProgress;
    const step = (targetProgress - currentProgress) / 10;
    
    let animationProgress = currentProgress;
    const completeAnimation = setInterval(() => {
        animationProgress += step;
        if (animationProgress >= targetProgress) {
            animationProgress = targetProgress;
            clearInterval(completeAnimation);
        }
        updateProgress(animationProgress);
    }, 50);
}

function showResultSection() {
    hideAllSections();
    if (elements.resultSection) {
        elements.resultSection.style.display = 'block';
    }
    
    if (currentData && elements.markdownPreview) {
        elements.markdownPreview.innerHTML = typeof marked !== 'undefined' ? 
            marked.parse(currentData.content) : 
            `<pre>${currentData.content}</pre>`;
    }
}

function showErrorSection(message) {
    hideAllSections();
    if (elements.errorSection) {
        elements.errorSection.style.display = 'block';
    }
    if (elements.errorMessage) {
        elements.errorMessage.textContent = message;
    }
}

// 뉴스 추출 관련 함수
function showNewsExtractorSection() {
    hideAllSections();
    if (elements.newsExtractorSection) {
        elements.newsExtractorSection.style.display = 'block';
    }
}

function hideNewsExtractorSection() {
    if (elements.newsExtractorSection) {
        elements.newsExtractorSection.style.display = 'none';
    }
}

// URL 직접 입력 섹션 관리
function showUrlInputSection() {
    hideAllSections();
    const urlInputSection = document.getElementById('urlInputSection');
    if (urlInputSection) {
        urlInputSection.style.display = 'block';
    }
}

function hideUrlInputSection() {
    const urlInputSection = document.getElementById('urlInputSection');
    if (urlInputSection) {
        urlInputSection.style.display = 'none';
    }
    // 메인 뉴스 추출 섹션은 항상 표시
    const newsExtractorSection = document.getElementById('newsExtractorSection');
    if (newsExtractorSection) {
        newsExtractorSection.style.display = 'block';
    }
}

function resetUrlInputForm() {
    // URL 입력 폼 초기화
    const urlInputs = document.querySelectorAll('input[name="urlInput[]"]');
    urlInputs.forEach(input => {
        input.value = '';
    });
    
    // 추가된 URL 입력 필드들 제거 (첫 번째 제외)
    const urlInputRows = document.querySelectorAll('.url-input-row');
    urlInputRows.forEach((row, index) => {
        if (index > 0) {
            row.remove();
        }
    });
    
    urlInputCount = 1;
    updateUrlInputButtons();
    
    showToast('URL 입력이 초기화되었습니다.', 'info');
}

async function handleNewsExtraction() {
    const keyword = elements.newsKeyword ? elements.newsKeyword.value.trim() : '';
    const count = elements.newsCount ? parseInt(elements.newsCount.value) || 10 : 10;
    
    if (count < 1 || count > 50) {
        showToast('추출할 뉴스 개수는 1-50개 사이여야 합니다.', 'error');
        return;
    }
    
    try {
        if (elements.extractNewsBtn) {
            elements.extractNewsBtn.disabled = true;
            elements.extractNewsBtn.innerHTML = '<div class="spinner"></div> 추출 중...';
        }
        
        const response = await fetch(`${API_BASE_URL}/api/extract-news-links`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ keyword, count })
        });
        
        if (!response.ok) {
            if (response.status === 404) {
                showToast('해당 키워드로 뉴스를 찾을 수 없습니다.', 'warning');
                return;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        extractedNews = result.data ? result.data.news_items || [] : [];
        
        if (extractedNews.length === 0) {
            showToast('추출된 뉴스가 없습니다.', 'warning');
            return;
        }
        
        showNewsSelectionSection();
        showToast(`${extractedNews.length}개의 뉴스를 추출했습니다.`, 'success');
        
    } catch (error) {
        console.error('뉴스 추출 오류:', error);
        showToast('뉴스 추출 중 오류가 발생했습니다.', 'error');
    } finally {
        if (elements.extractNewsBtn) {
            elements.extractNewsBtn.disabled = false;
            elements.extractNewsBtn.innerHTML = '<i class="fas fa-search"></i> 뉴스 추출';
        }
    }
}

function showNewsSelectionSection() {
    hideAllSections();
    if (elements.newsSelectionSection) {
        elements.newsSelectionSection.style.display = 'block';
    }
    
    // 뉴스 추출 정보 표시
    if (elements.newsExtractionInfo && extractedNews.length > 0) {
        elements.newsExtractionInfo.innerHTML = `
            <h3>뉴스 추출 완료</h3>
            <p>총 ${extractedNews.length}개의 뉴스를 추출했습니다. 콘텐츠로 변환할 뉴스를 선택해주세요.</p>
        `;
    }
    
    displayNewsList();
    updateSelectedCount();
    saveUserPreferences();
}

function displayNewsList() {
    if (!elements.newsList) return;
    
    // 현재 정렬 옵션 가져오기
    const sortOption = document.getElementById('newsSortSelect')?.value || 'newest';
    
    // 뉴스 정렬
    const sortedNews = getSortedNews(extractedNews, sortOption);
    
    elements.newsList.innerHTML = sortedNews.map((article, index) => `
        <div class="news-item" data-index="${index}" data-url="${article.url}">
            <div class="news-item-header">
                <div class="news-checkbox" data-index="${index}"></div>
                <div class="news-item-content">
                    <h4 class="news-item-title">${article.title}</h4>
                    <div class="news-item-url">${article.url}</div>
                    <div class="news-item-keywords">
                        ${article.keywords ? article.keywords.map(keyword => 
                            `<span class="keyword-tag">${keyword}</span>`
                        ).join('') : ''}
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    // 선택 상태 복원
    restoreNewsSelection();
    
    // 클릭 이벤트 추가
    elements.newsList.querySelectorAll('.news-item').forEach(item => {
        item.addEventListener('click', function() {
            const url = this.dataset.url;
            toggleNewsSelectionByUrl(url);
        });
    });
}

function getSortedNews(newsArray, sortOption) {
    const sortedArray = [...newsArray];
    
    switch (sortOption) {
        case 'newest':
            // 최신순 (날짜가 있다면 날짜순, 없다면 순서 그대로)
            return sortedArray.sort((a, b) => {
                if (a.published_date && b.published_date) {
                    return new Date(b.published_date) - new Date(a.published_date);
                }
                return 0; // 날짜가 없으면 원본 순서 유지
            });
        case 'oldest':
            // 오래된순
            return sortedArray.sort((a, b) => {
                if (a.published_date && b.published_date) {
                    return new Date(a.published_date) - new Date(b.published_date);
                }
                return 0;
            });
        case 'title':
            // 제목순
            return sortedArray.sort((a, b) => a.title.localeCompare(b.title));
        default:
            return sortedArray;
    }
}

function handleNewsSortChange() {
    displayNewsList();
}

function restoreNewsSelection() {
    // 기존 선택 상태 복원
    elements.newsList.querySelectorAll('.news-item').forEach(item => {
        const url = item.dataset.url;
        if (selectedNewsUrls.includes(url)) {
            item.classList.add('selected');
            item.querySelector('.news-checkbox').classList.add('checked');
        }
    });
}

function toggleNewsSelectionByUrl(url) {
    const newsItem = elements.newsList.querySelector(`[data-url="${url}"]`);
    const checkbox = newsItem.querySelector('.news-checkbox');
    
    if (selectedNewsUrls.includes(url)) {
        // 선택 해제
        selectedNewsUrls = selectedNewsUrls.filter(selectedUrl => selectedUrl !== url);
        newsItem.classList.remove('selected');
        checkbox.classList.remove('checked');
    } else {
        // 선택
        selectedNewsUrls.push(url);
        newsItem.classList.add('selected');
        checkbox.classList.add('checked');
    }
    
    updateSelectedCount();
}

function toggleNewsSelection(index) {
    const newsItem = elements.newsList.querySelector(`[data-index="${index}"]`);
    const checkbox = newsItem.querySelector('.news-checkbox');
    const article = extractedNews[index];
    
    if (selectedNewsUrls.includes(article.url)) {
        // 선택 해제
        selectedNewsUrls = selectedNewsUrls.filter(url => url !== article.url);
        newsItem.classList.remove('selected');
        checkbox.classList.remove('checked');
    } else {
        // 선택
        selectedNewsUrls.push(article.url);
        newsItem.classList.add('selected');
        checkbox.classList.add('checked');
    }
    
    updateSelectedCount();
}

function updateSelectedCount() {
    updateGenerateButtonState();
}

function updateGenerateButtonState() {
    if (elements.generateSelectedBtn) {
        elements.generateSelectedBtn.disabled = selectedNewsUrls.length === 0;
        elements.generateSelectedBtn.innerHTML = selectedNewsUrls.length > 0 ? 
            `<i class="fas fa-magic"></i> 선택된 뉴스 일괄 생성 (${selectedNewsUrls.length}개)` : 
            '<i class="fas fa-magic"></i> 선택된 뉴스 일괄 생성';
    }
}

function selectAllNews() {
    selectedNewsUrls = extractedNews.map(article => article.url);
    elements.newsList.querySelectorAll('.news-item').forEach(item => {
        item.classList.add('selected');
        item.querySelector('.news-checkbox').classList.add('checked');
    });
    updateSelectedCount();
    saveUserPreferences();
    showToast('모든 뉴스가 선택되었습니다.', 'info');
}

function deselectAllNews() {
    selectedNewsUrls = [];
    elements.newsList.querySelectorAll('.news-item').forEach(item => {
        item.classList.remove('selected');
        item.querySelector('.news-checkbox').classList.remove('checked');
    });
    updateSelectedCount();
    saveUserPreferences();
    showToast('모든 뉴스 선택이 해제되었습니다.', 'info');
}

async function handleGenerateSelectedNews() {
    if (selectedNewsUrls.length === 0) {
        showToast('선택된 뉴스가 없습니다.', 'warning');
        return;
    }
    
    // API 키 확인
    const apiSettings = getApiSettings();
    if (!apiSettings.provider || !apiSettings.key) {
        showToast('API 키를 먼저 설정해주세요.', 'error');
        return;
    }
    
    try {
        hideAllSections();
        showProgressSection();
        
        // 배치 프로그레스 시뮬레이션 시작 (선택된 뉴스 개수 * 10초)
        const estimatedTime = selectedNewsUrls.length * 10000; // 뉴스 하나당 10초
        startProgressSimulation(estimatedTime);
        
        const response = await fetch(`${API_BASE_URL}/api/batch-generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                urls: selectedNewsUrls,
                api_provider: apiSettings.provider,
                api_key: apiSettings.key
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success && result.data && result.data.results) {
            // 배치 생성이 즉시 완료되므로 프로그레스 완료 애니메이션 후 결과 처리
            completeProgress();
            currentBatchData = result.data;
            generatedContentData = result.data.results;
            
            setTimeout(() => {
                showGeneratedContentListSection();
                
                const successCount = result.data.summary ? result.data.summary.successful : 0;
                const totalCount = result.data.summary ? result.data.summary.total : result.data.results.length;
                
                showToast(`일괄 콘텐츠 생성이 완료되었습니다! (성공: ${successCount}/${totalCount})`, 'success');
            }, 500); // 프로그레스 완료 애니메이션 후 결과 표시
        } else {
            stopProgressSimulation();
            throw new Error(result.error || '일괄 생성에 실패했습니다.');
        }
        
    } catch (error) {
        console.error('일괄 생성 오류:', error);
        stopProgressSimulation();
        showErrorSection(error.message);
    }
}

async function pollBatchJobStatus(jobId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/status/${jobId}`);
        const result = await response.json();
        
        if (result.status === 'completed') {
            completeProgress();
            // 상태 API에서 data가 없는 경우를 대비한 안전한 처리
            if (result.data && result.data.results) {
                currentBatchData = result.data;
                generatedContentData = result.data.results;
                setTimeout(() => {
                    showGeneratedContentListSection();
                    showToast('일괄 콘텐츠 생성이 완료되었습니다!', 'success');
                }, 500); // 프로그레스 완료 애니메이션 후 결과 표시
            } else {
                // data가 없는 경우 에러 처리
                setTimeout(() => {
                    showErrorSection('작업은 완료되었지만 결과 데이터를 찾을 수 없습니다.');
                }, 500);
            }
        } else if (result.status === 'failed') {
            stopProgressSimulation();
            showErrorSection(result.error || '일괄 작업이 실패했습니다.');
        } else if (result.status === 'in_progress') {
            // 백엔드에서 실제 progress가 있으면 사용, 없으면 시뮬레이션 계속
            if (result.progress && result.progress > simulatedProgress) {
                updateProgress(result.progress);
            }
            setTimeout(() => pollBatchJobStatus(jobId), 1000);
        } else {
            stopProgressSimulation();
            showErrorSection('알 수 없는 작업 상태입니다.');
        }
    } catch (error) {
        console.error('일괄 작업 상태 확인 오류:', error);
        showErrorSection('일괄 작업 상태를 확인하는 중 오류가 발생했습니다.');
    }
}

function showGeneratedContentListSection() {
    hideAllSections();
    if (elements.generatedContentListSection) {
        elements.generatedContentListSection.style.display = 'block';
    }
    displayGeneratedContentList();
}

function displayGeneratedContentList() {
    if (!elements.generatedContentList) return;
    
    elements.generatedContentList.innerHTML = generatedContentData.map((item, index) => `
        <div class="generated-content-item">
            <div class="generated-content-header">
                <div class="generated-content-title">${item.title || `콘텐츠 ${index + 1}`}</div>
                <div class="generated-content-actions">
                    <button class="btn btn-mini btn-preview" onclick="toggleContentPreview(${index})">
                        <i class="fas fa-eye"></i> 미리보기
                    </button>
                    <button class="btn btn-mini btn-copy" onclick="copyGeneratedContent(${index})">
                        <i class="fas fa-copy"></i> 복사
                    </button>
                    <button class="btn btn-mini btn-download" onclick="downloadGeneratedContent(${index})">
                        <i class="fas fa-download"></i> 다운로드
                    </button>
                </div>
            </div>
            <div class="generated-content-preview" id="preview-${index}">
                ${typeof marked !== 'undefined' ? marked.parse(item.content) : `<pre>${item.content}</pre>`}
            </div>
        </div>
    `).join('');
}

function toggleContentPreview(index) {
    const preview = document.getElementById(`preview-${index}`);
    if (preview) {
        preview.classList.toggle('show');
    }
}

async function copyGeneratedContent(index) {
    const item = generatedContentData[index];
    if (!item) return;
    
    try {
        await navigator.clipboard.writeText(item.content);
        showToast('클립보드에 복사되었습니다.', 'success');
    } catch (error) {
        console.error('복사 오류:', error);
        showToast('복사 중 오류가 발생했습니다.', 'error');
    }
}

function downloadGeneratedContent(index) {
    const item = generatedContentData[index];
    if (!item) return;
    
    const blob = new Blob([item.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `content-${index + 1}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('다운로드가 시작되었습니다.', 'success');
}

async function downloadAllGeneratedContent() {
    if (generatedContentData.length === 0) {
        showToast('다운로드할 콘텐츠가 없습니다.', 'warning');
        return;
    }
    
    try {
        const allContent = generatedContentData.map((item, index) => 
            `# 콘텐츠 ${index + 1}\n\n${item.content}\n\n---\n\n`
        ).join('');
        
        const blob = new Blob([allContent], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `all-content-${Date.now()}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showToast('전체 콘텐츠 다운로드가 시작되었습니다.', 'success');
    } catch (error) {
        console.error('전체 다운로드 오류:', error);
        showToast('전체 다운로드 중 오류가 발생했습니다.', 'error');
    }
}

async function copyAllGeneratedContent() {
    if (generatedContentData.length === 0) {
        showToast('복사할 콘텐츠가 없습니다.', 'warning');
        return;
    }
    
    try {
        const allContent = generatedContentData.map((item, index) => 
            `# 콘텐츠 ${index + 1}\n\n${item.content}\n\n---\n\n`
        ).join('');
        
        await navigator.clipboard.writeText(allContent);
        showToast('전체 콘텐츠가 클립보드에 복사되었습니다.', 'success');
    } catch (error) {
        console.error('전체 복사 오류:', error);
        showToast('전체 복사 중 오류가 발생했습니다.', 'error');
    }
}

function resetAllFeatures() {
    // 모든 상태 초기화
    currentJobId = null;
    currentData = null;
    currentBatchJobId = null;
    currentBatchData = null;
    extractedNews = [];
    selectedNewsUrls = [];
    generatedContentData = [];
    
    // 모든 섹션 숨기기 (이미 메인 뉴스 추출 섹션 표시됨)
    hideAllSections();
    
    // URL 입력 필드 초기화
    const urlInputs = document.querySelectorAll('input[name="urlInput[]"]');
    urlInputs.forEach(input => input.value = '');
    
    // 추가 URL 입력 필드 제거
    const additionalRows = document.querySelectorAll('.url-input-row:not(:first-child)');
    additionalRows.forEach(row => row.remove());
    
    // 뉴스 추출 입력 필드 초기화
    if (elements.newsKeyword) elements.newsKeyword.value = '';
    if (elements.newsCount) elements.newsCount.value = '10';
    
    // 메인 뉴스 추출 섹션 확실히 표시
    showNewsExtractorSection();
    
    // 저장된 사용자 설정 초기화
    clearUserPreferences();
    
    showToast('모든 기능이 초기화되었습니다.', 'info');
}

// 파일 다운로드 및 복사 함수
async function downloadFile() {
    if (!currentData) return;
    
    const blob = new Blob([currentData.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `content-${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('다운로드가 시작되었습니다.', 'success');
}

async function copyToClipboard() {
    if (!currentData) return;
    
    try {
        await navigator.clipboard.writeText(currentData.content);
        showToast('클립보드에 복사되었습니다.', 'success');
    } catch (error) {
        console.error('복사 오류:', error);
        showToast('복사 중 오류가 발생했습니다.', 'error');
    }
}

function resetForm() {
    // URL 입력 필드 초기화
    const urlInputs = document.querySelectorAll('input[name="urlInput[]"]');
    urlInputs.forEach(input => input.value = '');
    
    // 추가 URL 입력 필드 제거
    const additionalRows = document.querySelectorAll('.url-input-row:not(:first-child)');
    additionalRows.forEach(row => row.remove());
    
    urlInputCount = 1;
    updateUrlInputButtons();
    
    // 상태 초기화
    currentJobId = null;
    currentData = null;
    
    showToast('폼이 초기화되었습니다.', 'info');
}

function retryGeneration() {
    if (elements.urlForm) {
        elements.urlForm.dispatchEvent(new Event('submit'));
    }
}

// 유틸리티 함수
function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    if (elements.toastContainer) {
        elements.toastContainer.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// API 설정 관련 함수
function loadApiSettings() {
    const settings = getApiSettings();
    if (settings.provider && settings.key) {
        updateApiStatus(settings.provider, true);
        if (elements.apiProviderSelect) {
            elements.apiProviderSelect.value = settings.provider;
        }
    }
}

function getApiSettings() {
    return {
        provider: localStorage.getItem('apiProvider') || 'anthropic',
        key: localStorage.getItem('apiKey') || ''
    };
}

function saveApiSettings(provider, key) {
    localStorage.setItem('apiProvider', provider);
    localStorage.setItem('apiKey', key);
}

function deleteApiSettings() {
    localStorage.removeItem('apiProvider');
    localStorage.removeItem('apiKey');
}

function updateApiStatus(provider, isConfigured) {
    if (elements.apiStatus) {
        elements.apiStatus.classList.toggle('configured', isConfigured);
        const statusText = elements.apiStatus.querySelector('.status-text');
        if (statusText) {
            statusText.textContent = isConfigured ? `${provider} 활성` : 'AI 비활성';
        }
    }
}

function showApiSettingsSection() {
    hideAllSections();
    if (elements.apiSettingsSection) {
        elements.apiSettingsSection.style.display = 'block';
    }
    
    const settings = getApiSettings();
    if (elements.apiProviderSelect) {
        elements.apiProviderSelect.value = settings.provider;
    }
    if (elements.apiKeyInput) {
        elements.apiKeyInput.value = settings.key;
    }
}

function hideApiSettingsSection() {
    if (elements.apiSettingsSection) {
        elements.apiSettingsSection.style.display = 'none';
    }
}

function onApiProviderChange() {
    const settings = getApiSettings();
    if (elements.apiProviderSelect) {
        settings.provider = elements.apiProviderSelect.value;
        saveApiSettings(settings.provider, settings.key);
    }
}

function onApiKeyInput() {
    // 실시간 검증은 제거하고 단순화
}

async function validateApiKey() {
    const provider = elements.apiProviderSelect ? elements.apiProviderSelect.value : 'anthropic';
    const key = elements.apiKeyInput ? elements.apiKeyInput.value.trim() : '';
    
    if (!key) {
        showToast('API 키를 입력해주세요.', 'error');
        return;
    }
    
    try {
        if (elements.validateApiKeyBtn) {
            elements.validateApiKeyBtn.disabled = true;
            elements.validateApiKeyBtn.innerHTML = '<div class="spinner"></div> 검증 중...';
        }
        
        const response = await fetch(`${API_BASE_URL}/api/validate-key`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ api_provider: provider, api_key: key })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('API 키가 유효합니다.', 'success');
            saveApiSettings(provider, key);
            updateApiStatus(provider, true);
        } else {
            showToast(result.error || 'API 키가 유효하지 않습니다.', 'error');
        }
        
    } catch (error) {
        console.error('API 키 검증 오류:', error);
        showToast('API 키 검증 중 오류가 발생했습니다.', 'error');
    } finally {
        if (elements.validateApiKeyBtn) {
            elements.validateApiKeyBtn.disabled = false;
            elements.validateApiKeyBtn.innerHTML = '<i class="fas fa-check"></i> 키 검증';
        }
    }
}

function saveApiKey() {
    const provider = elements.apiProviderSelect ? elements.apiProviderSelect.value : 'anthropic';
    const key = elements.apiKeyInput ? elements.apiKeyInput.value.trim() : '';
    
    if (!key) {
        showToast('API 키를 입력해주세요.', 'error');
        return;
    }
    
    saveApiSettings(provider, key);
    updateApiStatus(provider, true);
    hideApiSettingsSection();
    showToast('API 키가 저장되었습니다.', 'success');
}

function deleteApiKey() {
    deleteApiSettings();
    updateApiStatus('', false);
    hideApiSettingsSection();
    showToast('API 키가 삭제되었습니다.', 'info');
}

// 테마 관련 함수
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'auto';
    setTheme(savedTheme);
}

function setTheme(theme) {
    currentTheme = theme;
    localStorage.setItem('theme', theme);
    
    const root = document.documentElement;
    
    if (theme === 'auto') {
        root.removeAttribute('data-theme');
    } else {
        root.setAttribute('data-theme', theme);
    }
    
    updateThemeToggle(getCurrentDisplayTheme());
}

function updateThemeToggle(displayTheme) {
    if (elements.themeIcon && elements.themeText) {
        if (displayTheme === 'dark') {
            elements.themeIcon.className = 'fas fa-sun';
            elements.themeText.textContent = '라이트 모드';
        } else {
            elements.themeIcon.className = 'fas fa-moon';
            elements.themeText.textContent = '다크 모드';
        }
    }
}

function toggleTheme() {
    const themes = ['light', 'dark', 'auto'];
    const currentIndex = themes.indexOf(currentTheme);
    const nextIndex = (currentIndex + 1) % themes.length;
    setTheme(themes[nextIndex]);
    
    const themeNames = {
        'light': '라이트 모드',
        'dark': '다크 모드',
        'auto': '자동 모드'
    };
    
    showToast(`${themeNames[currentTheme]}로 변경되었습니다.`, 'info');
}

function getCurrentDisplayTheme() {
    if (currentTheme === 'auto') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return currentTheme;
}

// 사용자 편의기능
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl+A (전체 선택)
        if (e.ctrlKey && e.key === 'a') {
            const newsSelectionSection = document.getElementById('newsSelectionSection');
            if (newsSelectionSection && newsSelectionSection.style.display !== 'none') {
                e.preventDefault();
                selectAllNews();
            }
        }
        
        // Ctrl+D (전체 해제)
        if (e.ctrlKey && e.key === 'd') {
            const newsSelectionSection = document.getElementById('newsSelectionSection');
            if (newsSelectionSection && newsSelectionSection.style.display !== 'none') {
                e.preventDefault();
                deselectAllNews();
            }
        }
        
        // Escape (뒤로가기)
        if (e.key === 'Escape') {
            handleEscapeKey();
        }
        
        // Enter (기본 액션)
        if (e.key === 'Enter' && !e.ctrlKey && !e.shiftKey && !e.altKey) {
            handleEnterKey(e);
        }
    });
}

function handleEscapeKey() {
    // 현재 활성 섹션에 따라 뒤로가기 처리
    const urlInputSection = document.getElementById('urlInputSection');
    const newsSelectionSection = document.getElementById('newsSelectionSection');
    const generatedContentListSection = document.getElementById('generatedContentListSection');
    const apiSettingsSection = document.getElementById('apiSettingsSection');
    
    if (apiSettingsSection && apiSettingsSection.style.display !== 'none') {
        hideApiSettingsSection();
    } else if (urlInputSection && urlInputSection.style.display !== 'none') {
        hideUrlInputSection();
    } else if (generatedContentListSection && generatedContentListSection.style.display !== 'none') {
        hideAllSections();
    } else if (newsSelectionSection && newsSelectionSection.style.display !== 'none') {
        hideAllSections();
    }
}

function handleEnterKey(e) {
    // 포커스된 요소가 입력 필드가 아닌 경우에만 처리
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
        return;
    }
    
    // 현재 활성 섹션의 주요 액션 실행
    const newsExtractorSection = document.getElementById('newsExtractorSection');
    const newsSelectionSection = document.getElementById('newsSelectionSection');
    
    if (newsExtractorSection && newsExtractorSection.style.display !== 'none') {
        const extractBtn = document.getElementById('extractNewsBtn');
        if (extractBtn && !extractBtn.disabled) {
            extractBtn.click();
        }
    } else if (newsSelectionSection && newsSelectionSection.style.display !== 'none') {
        const generateBtn = document.getElementById('generateSelectedBtn');
        if (generateBtn && !generateBtn.disabled) {
            generateBtn.click();
        }
    }
}

function saveUserPreferences() {
    const preferences = {
        selectedNewsUrls: selectedNewsUrls,
        newsSort: document.getElementById('newsSortSelect')?.value || 'newest',
        lastKeyword: document.getElementById('newsKeyword')?.value || '',
        lastCount: document.getElementById('newsCount')?.value || 10,
        timestamp: Date.now()
    };
    
    localStorage.setItem('nongbuxx_preferences', JSON.stringify(preferences));
}

function loadUserPreferences() {
    try {
        const saved = localStorage.getItem('nongbuxx_preferences');
        if (!saved) return;
        
        const preferences = JSON.parse(saved);
        
        // 1시간 이내 데이터만 복원
        if (Date.now() - preferences.timestamp > 3600000) {
            localStorage.removeItem('nongbuxx_preferences');
            return;
        }
        
        // 설정 복원
        if (preferences.newsSort) {
            const sortSelect = document.getElementById('newsSortSelect');
            if (sortSelect) {
                sortSelect.value = preferences.newsSort;
            }
        }
        
        if (preferences.lastKeyword) {
            const keywordInput = document.getElementById('newsKeyword');
            if (keywordInput) {
                keywordInput.value = preferences.lastKeyword;
            }
        }
        
        if (preferences.lastCount) {
            const countInput = document.getElementById('newsCount');
            if (countInput) {
                countInput.value = preferences.lastCount;
            }
        }
        
        // 선택된 뉴스 URL은 뉴스 추출 후에 복원
        if (preferences.selectedNewsUrls && Array.isArray(preferences.selectedNewsUrls)) {
            selectedNewsUrls = preferences.selectedNewsUrls;
        }
        
    } catch (error) {
        console.warn('사용자 설정 로드 중 오류:', error);
        localStorage.removeItem('nongbuxx_preferences');
    }
}

function clearUserPreferences() {
    localStorage.removeItem('nongbuxx_preferences');
}

// 전역 함수로 노출 (HTML에서 사용)
window.addUrlInput = addUrlInput;
window.removeUrlInput = removeUrlInput;
window.toggleContentPreview = toggleContentPreview;
window.copyGeneratedContent = copyGeneratedContent;
window.downloadGeneratedContent = downloadGeneratedContent; 