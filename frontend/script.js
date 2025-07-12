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
const API_BASE_URL = window.ENV?.API_BASE_URL || 'http://localhost:8080';

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
    
    // API 키 설정 모달 관련 요소들
    apiSettingsBtn: document.getElementById('apiSettingsBtn'),
    apiStatus: document.getElementById('apiStatus'),
    apiSettingsModalSection: document.getElementById('apiSettingsModalSection'),
    apiSettingsModalOverlay: document.getElementById('apiSettingsModalOverlay'),
    closeApiSettingsModalBtn: document.getElementById('closeApiSettingsModalBtn'),
    apiProviderSelect: document.getElementById('apiProviderSelect'),
    apiKeyInput: document.getElementById('apiKeyInput'),
    toggleApiKeyBtn: document.getElementById('toggleApiKeyBtn'),
    validateApiKeyBtn: document.getElementById('validateApiKeyBtn'),
    saveApiKeyBtn: document.getElementById('saveApiKeyBtn'),
    deleteApiKeyBtn: document.getElementById('deleteApiKeyBtn'),
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
    toastContainer: document.getElementById('toastContainer'),
    
    // 출처 관리 관련 요소들
    sourceManagementBtn: document.getElementById('sourceManagementBtn'),
    sourceManagementSection: document.getElementById('sourceManagementSection'),
    closeSourceManagementBtn: document.getElementById('closeSourceManagementBtn'),
    sourcesList: document.getElementById('sourcesList'),
    addSourceBtn: document.getElementById('addSourceBtn'),
    
    // 출처 선택 관련 요소들
    selectedSources: document.getElementById('selectedSources'),
    selectSourcesBtn: document.getElementById('selectSourcesBtn'),
    sourceSelectionModalSection: document.getElementById('sourceSelectionModalSection'),
    sourceSelectionModalOverlay: document.getElementById('sourceSelectionModalOverlay'),
    closeSourceSelectionModalBtn: document.getElementById('closeSourceSelectionModalBtn'),
    
    // 2단계 선택 시스템 요소들
    step1Nav: document.getElementById('step1Nav'),
    step2Nav: document.getElementById('step2Nav'),
    step1Content: document.getElementById('step1Content'),
    step2Content: document.getElementById('step2Content'),
    sourceTypeList: document.getElementById('sourceTypeList'),
    subcategorySelectionList: document.getElementById('subcategorySelectionList'),
    nextToStep2Btn: document.getElementById('nextToStep2Btn'),
    backToStep1Btn: document.getElementById('backToStep1Btn'),
    selectedSourceName: document.getElementById('selectedSourceName'),
    selectionSummary: document.getElementById('selectionSummary'),
    selectedItemsSummary: document.getElementById('selectedItemsSummary'),
    
    selectAllSourcesBtn: document.getElementById('selectAllSourcesBtn'),
    deselectAllSourcesBtn: document.getElementById('deselectAllSourcesBtn'),
    confirmSourceSelectionBtn: document.getElementById('confirmSourceSelectionBtn'),
    
    // 출처 추가/수정 모달 관련 요소들
    sourceModalSection: document.getElementById('sourceModalSection'),
    sourceModalOverlay: document.getElementById('sourceModalOverlay'),
    closeSourceModalBtn: document.getElementById('closeSourceModalBtn'),
    sourceModalTitle: document.getElementById('sourceModalTitle'),
    sourceForm: document.getElementById('sourceForm'),
    sourceNameInput: document.getElementById('sourceNameInput'),
    sourceUrlInput: document.getElementById('sourceUrlInput'),
    sourceIsParentCheckbox: document.getElementById('sourceIsParentCheckbox'),
    sourceParserTypeSelect: document.getElementById('sourceParserTypeSelect'),
    sourceDescriptionInput: document.getElementById('sourceDescriptionInput'),
    sourceActiveCheckbox: document.getElementById('sourceActiveCheckbox'),
    saveSourceBtn: document.getElementById('saveSourceBtn'),
    
    // 서브 카테고리 관련 요소들
    subcategoriesSection: document.getElementById('subcategoriesSection'),
    subcategoriesList: document.getElementById('subcategoriesList'),
    addSubcategoryBtn: document.getElementById('addSubcategoryBtn'),
    parserTypeGroup: document.getElementById('parserTypeGroup')
};

// 앱 초기화
document.addEventListener('DOMContentLoaded', function() {
    initEventListeners();
    loadApiSettings();
    initTheme();
    updateUrlInputButtons();
    initKeyboardShortcuts();
    loadUserPreferences();
    
    // 출처 관리 초기화
    loadAvailableSources();
    
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
    // 블로그 콘텐츠 생성 버튼 이벤트 리스너
    const generateBlogBtn = document.getElementById('generateBlogBtn');
    if (generateBlogBtn) {
        generateBlogBtn.addEventListener('click', handleBlogGeneration);
    }
    const generateSelectedBlogBtn = document.getElementById('generateSelectedBlogBtn');
    if (generateSelectedBlogBtn) {
        generateSelectedBlogBtn.addEventListener('click', handleGenerateSelectedBlogNews);
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
    
    // API 설정 모달 관련
    if (elements.apiSettingsBtn) {
        elements.apiSettingsBtn.addEventListener('click', showApiSettingsModal);
    }
    if (elements.closeApiSettingsModalBtn) {
        elements.closeApiSettingsModalBtn.addEventListener('click', hideApiSettingsModal);
    }
    if (elements.apiSettingsModalOverlay) {
        elements.apiSettingsModalOverlay.addEventListener('click', function(e) {
            if (e.target === elements.apiSettingsModalOverlay) {
                hideApiSettingsModal();
            }
        });
    }
    if (elements.apiProviderSelect) {
        elements.apiProviderSelect.addEventListener('change', onApiProviderChange);
    }
    if (elements.apiKeyInput) {
        elements.apiKeyInput.addEventListener('input', onApiKeyInput);
    }
    if (elements.toggleApiKeyBtn) {
        elements.toggleApiKeyBtn.addEventListener('click', toggleApiKeyVisibility);
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
    
    // 출처 관리 관련
    if (elements.sourceManagementBtn) {
        elements.sourceManagementBtn.addEventListener('click', showSourceManagementModal);
    }
    if (elements.closeSourceManagementBtn) {
        elements.closeSourceManagementBtn.addEventListener('click', hideSourceManagementModal);
    }
    if (elements.addSourceBtn) {
        elements.addSourceBtn.addEventListener('click', showAddSourceModal);
    }
    
    // 출처 선택 관련
    if (elements.selectSourcesBtn) {
        elements.selectSourcesBtn.addEventListener('click', showSourceSelectionModal);
    }
    if (elements.closeSourceSelectionModalBtn) {
        elements.closeSourceSelectionModalBtn.addEventListener('click', hideSourceSelectionModal);
    }
    if (elements.sourceSelectionModalOverlay) {
        elements.sourceSelectionModalOverlay.addEventListener('click', function(e) {
            if (e.target === elements.sourceSelectionModalOverlay) {
                hideSourceSelectionModal();
            }
        });
    }
    if (elements.selectAllSourcesBtn) {
        elements.selectAllSourcesBtn.addEventListener('click', selectAllSources);
    }
    if (elements.deselectAllSourcesBtn) {
        elements.deselectAllSourcesBtn.addEventListener('click', deselectAllSources);
    }
    if (elements.confirmSourceSelectionBtn) {
        elements.confirmSourceSelectionBtn.addEventListener('click', confirmSourceSelection);
    }
    
    // 출처 추가/수정 모달 관련
    if (elements.closeSourceModalBtn) {
        elements.closeSourceModalBtn.addEventListener('click', hideSourceModal);
    }
    if (elements.sourceModalOverlay) {
        elements.sourceModalOverlay.addEventListener('click', function(e) {
            if (e.target === elements.sourceModalOverlay) {
                hideSourceModal();
            }
        });
    }
    if (elements.sourceIsParentCheckbox) {
        elements.sourceIsParentCheckbox.addEventListener('change', toggleParentSourceFields);
    }
    if (elements.addSubcategoryBtn) {
        elements.addSubcategoryBtn.addEventListener('click', addSubcategoryForm);
    }
    if (elements.saveSourceBtn) {
        elements.saveSourceBtn.addEventListener('click', saveSource);
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
    
    // 2단계 선택 시스템 이벤트 리스너
    if (elements.nextToStep2Btn) {
        elements.nextToStep2Btn.addEventListener('click', goToStep2);
    }
    if (elements.backToStep1Btn) {
        elements.backToStep1Btn.addEventListener('click', goToStep1);
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

// 폼 제출 처리 (표준 콘텐츠 생성)
async function handleFormSubmit(e) {
    e.preventDefault();
    
    // 클릭된 버튼의 콘텐츠 타입 확인
    const submitter = e.submitter;
    const contentType = submitter?.dataset?.contentType || 'standard';
    
    await generateContent(contentType);
}

// 블로그 콘텐츠 생성 처리
async function handleBlogGeneration() {
    await generateContent('blog');
}

// 공통 콘텐츠 생성 함수
async function generateContent(contentType = 'standard') {
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
        
        // 콘텐츠 타입에 따른 진행률 표시
        const progressTitle = document.getElementById('progressTitle');
        if (progressTitle) {
            progressTitle.textContent = contentType === 'blog' ? '블로그 콘텐츠 생성 중...' : '콘텐츠 생성 중...';
        }
        
        // 프로그레스 시뮬레이션 시작 (블로그 콘텐츠는 더 오래 걸림)
        const duration = contentType === 'blog' ? 45000 : 30000;
        startProgressSimulation(duration);
            
            const response = await fetch(`${API_BASE_URL}/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            body: JSON.stringify({ 
                url: urls[0], // 단일 URL 전송
                api_provider: apiSettings.provider,
                api_key: apiSettings.key,
                content_type: contentType
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

// 출처 관리 관련 변수
let availableSources = [];
let selectedSourceIds = [];
let currentEditingSource = null;

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
    
    if (selectedSourceIds.length === 0) {
        showToast('출처를 선택해주세요.', 'error');
        return;
    }
    
    try {
        if (elements.extractNewsBtn) {
            elements.extractNewsBtn.disabled = true;
            elements.extractNewsBtn.innerHTML = '<div class="spinner"></div> 추출 중...';
        }
        
        const requestData = {
            keyword, 
            count,
            sources: selectedSourceIds  // 선택된 출처들 전송
        };
        
        const response = await fetch(`${API_BASE_URL}/api/extract-news-links`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
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
        
        // 출처별 결과 표시
        if (result.data.source_results) {
            const sourceResults = result.data.source_results;
            const successSources = sourceResults.filter(s => s.success);
            const failedSources = sourceResults.filter(s => !s.success);
            
            let message = `${extractedNews.length}개의 뉴스를 추출했습니다.`;
            if (successSources.length > 0) {
                message += ` (성공: ${successSources.map(s => s.source_name).join(', ')})`;
            }
            if (failedSources.length > 0) {
                message += ` (실패: ${failedSources.length}개 출처)`;
            }
            
            showToast(message, 'success');
        } else {
            showToast(`${extractedNews.length}개의 뉴스를 추출했습니다.`, 'success');
        }
        
        showNewsSelectionSection();
        
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
    
    // 뉴스 추출 정보 및 출처별 통계 표시
    if (elements.newsExtractionInfo && extractedNews.length > 0) {
        // 출처별 뉴스 개수 계산
        const sourceStats = {};
        extractedNews.forEach(news => {
            if (news.source_name) {
                sourceStats[news.source_name] = (sourceStats[news.source_name] || 0) + 1;
            }
        });
        
        const sourceStatsHtml = Object.keys(sourceStats).length > 0 ? `
            <div class="news-extraction-stats">
                ${Object.entries(sourceStats).map(([sourceName, count]) => `
                    <div class="source-stat">
                        <i class="fas fa-globe"></i>
                        <span>${sourceName}:</span>
                        <span class="count">${count}개</span>
                    </div>
                `).join('')}
            </div>
        ` : '';
        
        elements.newsExtractionInfo.innerHTML = `
            <h3>뉴스 추출 완료</h3>
            <p>총 ${extractedNews.length}개의 뉴스를 추출했습니다. 콘텐츠로 변환할 뉴스를 선택해주세요.</p>
            ${sourceStatsHtml}
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
                    <div class="news-item-meta">
                        <div class="news-item-url">${article.url}</div>
                        ${article.source_name ? `<div class="news-source-tag" data-source-id="${article.source_id || ''}">
                            <i class="fas fa-globe"></i> ${article.source_name}
                        </div>` : ''}
                    </div>
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
    const hasSelected = selectedNewsUrls.length > 0;
    const count = selectedNewsUrls.length;
    
    if (elements.generateSelectedBtn) {
        elements.generateSelectedBtn.disabled = !hasSelected;
        elements.generateSelectedBtn.innerHTML = hasSelected ? 
            `<i class="fas fa-magic"></i> 선택된 뉴스 일괄 생성 (${count}개)` : 
            '<i class="fas fa-magic"></i> 선택된 뉴스 일괄 생성';
    }
    
    // 블로그 생성 버튼도 동일하게 활성화/비활성화
    const generateSelectedBlogBtn = document.getElementById('generateSelectedBlogBtn');
    if (generateSelectedBlogBtn) {
        generateSelectedBlogBtn.disabled = !hasSelected;
        generateSelectedBlogBtn.innerHTML = hasSelected ? 
            `<i class="fas fa-blog"></i> 선택된 뉴스 블로그 생성 (${count}개)` : 
            '<i class="fas fa-blog"></i> 선택된 뉴스 블로그 생성';
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
    await generateSelectedNews('standard');
}

async function handleGenerateSelectedBlogNews() {
    await generateSelectedNews('blog');
}

async function generateSelectedNews(contentType = 'standard') {
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
        
        // 콘텐츠 타입에 따른 진행률 표시
        const progressTitle = document.getElementById('progressTitle');
        if (progressTitle) {
            progressTitle.textContent = contentType === 'blog' ? '블로그 콘텐츠 일괄 생성 중...' : '일괄 콘텐츠 생성 중...';
        }
        
        // 배치 프로그레스 시뮬레이션 시작 (블로그 콘텐츠는 더 오래 걸림)
        const timePerItem = contentType === 'blog' ? 15000 : 10000; // 블로그 콘텐츠는 15초, 표준은 10초
        const estimatedTime = selectedNewsUrls.length * timePerItem;
        startProgressSimulation(estimatedTime);
        
        const response = await fetch(`${API_BASE_URL}/api/batch-generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                urls: selectedNewsUrls,
                api_provider: apiSettings.provider,
                api_key: apiSettings.key,
                content_type: contentType
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
                
                const successCount = result.data.success_count || 0;
                const totalCount = result.data.total_count || result.data.results.length;
                const contentTypeName = contentType === 'blog' ? '블로그 ' : '';
                
                showToast(`일괄 ${contentTypeName}콘텐츠 생성이 완료되었습니다! (성공: ${successCount}/${totalCount})`, 'success');
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

function showApiSettingsModal() {
    hideAllSections();
    if (elements.apiSettingsModalSection) {
        elements.apiSettingsModalSection.style.display = 'block';
    }
    
    const settings = getApiSettings();
    if (elements.apiProviderSelect) {
        elements.apiProviderSelect.value = settings.provider;
    }
    if (elements.apiKeyInput) {
        elements.apiKeyInput.value = settings.key;
    }
}

function hideApiSettingsModal() {
    if (elements.apiSettingsModalSection) {
        elements.apiSettingsModalSection.style.display = 'none';
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
    hideApiSettingsModal();
    showToast('API 키가 저장되었습니다.', 'success');
}

function deleteApiKey() {
        deleteApiSettings();
    updateApiStatus('', false);
        hideApiSettingsModal();
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
    const apiSettingsSection = document.getElementById('apiSettingsModalSection');
    
    if (apiSettingsSection && apiSettingsSection.style.display !== 'none') {
        hideApiSettingsModal();
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
    try {
        localStorage.removeItem('newsPreferences');
        localStorage.removeItem('selectedNewsUrls');
        
        selectedNewsUrls = [];
        sortedNews = [];
        
        console.log('사용자 설정이 초기화되었습니다.');
    } catch (error) {
        console.error('사용자 설정 초기화 중 오류:', error);
    }
}

// ============================================================================
// 출처 관리 관련 함수들
// ============================================================================

async function loadAvailableSources() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/sources/extractable`);
        const result = await response.json();
        
        if (result.success) {
            availableSources = result.data.sources;
            
            // 기본 선택: 모든 활성화된 출처
            selectedSourceIds = availableSources
                .filter(source => source.active)
                .map(source => source.id);
            
            updateSelectedSourcesDisplay();
            console.log(`${availableSources.length}개의 추출 가능한 출처를 로드했습니다.`);
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('출처 로드 오류:', error);
        showToast('출처 정보를 불러오는 중 오류가 발생했습니다.', 'error');
        
        // 기본 출처 설정 (계층적 구조 기반)
        availableSources = [
            {
                id: 'yahoo_finance_latest',
                name: 'Latest News',
                full_url: 'https://finance.yahoo.com/topic/latest-news/',
                active: true,
                description: 'Yahoo Finance 최신 뉴스'
            },
            {
                id: 'yahoo_finance_crypto',
                name: 'Crypto',
                full_url: 'https://finance.yahoo.com/topic/crypto/',
                active: true,
                description: 'Yahoo Finance 암호화폐 뉴스'
            },
            {
                id: 'yahoo_finance_tech',
                name: 'Tech',
                full_url: 'https://finance.yahoo.com/topic/tech/',
                active: true,
                description: 'Yahoo Finance 기술 뉴스'
            }
        ];
        selectedSourceIds = ['yahoo_finance_latest'];
        updateSelectedSourcesDisplay();
    }
}

function updateSelectedSourcesDisplay() {
    if (!elements.selectedSources) return;
    
    if (selectedSourceIds.length === 0) {
        elements.selectedSources.innerHTML = '<span class="loading">출처를 선택해주세요</span>';
        return;
    }
    
    const selectedSources = availableSources.filter(source => 
        selectedSourceIds.includes(source.id)
    );
    
    elements.selectedSources.innerHTML = selectedSources.map(source => `
        <span class="source-tag">
            ${source.name}
            <span class="remove" onclick="removeSelectedSource('${source.id}')">×</span>
        </span>
    `).join('');
}

function removeSelectedSource(sourceId) {
    selectedSourceIds = selectedSourceIds.filter(id => id !== sourceId);
    updateSelectedSourcesDisplay();
    
    if (selectedSourceIds.length === 0) {
        showToast('최소 하나의 출처는 선택되어야 합니다.', 'warning');
    }
}

function showSourceManagementModal() {
    hideAllSections();
    if (elements.sourceManagementSection) {
        elements.sourceManagementSection.style.display = 'block';
        displaySourcesList();
    }
}

function hideSourceManagementModal() {
    if (elements.sourceManagementSection) {
        elements.sourceManagementSection.style.display = 'none';
    }
    showNewsExtractorSection();
}

function displaySourcesList() {
    if (!elements.sourcesList) return;
    
    if (availableSources.length === 0) {
        elements.sourcesList.innerHTML = `
            <div class="no-sources">
                <i class="fas fa-globe"></i>
                <h4>등록된 출처가 없습니다</h4>
                <p>새 출처를 추가하여 뉴스 추출을 시작해보세요.</p>
            </div>
        `;
        return;
    }
    
    elements.sourcesList.innerHTML = '';
    
    availableSources.forEach(source => {
        const sourceElement = document.createElement('div');
        sourceElement.className = `source-item ${source.active ? 'active' : 'inactive'}`;
        
        let subcategoriesHtml = '';
        if (source.is_parent && source.subcategories && source.subcategories.length > 0) {
            subcategoriesHtml = `
                <div class="subcategories-display">
                    <h5><i class="fas fa-list"></i> 서브 카테고리 (${source.subcategories.length}개)</h5>
                    <div class="subcategories-grid">
                        ${source.subcategories.map(sub => `
                            <div class="subcategory-card ${sub.active ? 'active' : 'inactive'}">
                                <div class="subcategory-info">
                                    <h6><i class="fas fa-tag"></i> ${sub.name}</h6>
                                    <div class="subcategory-url">${sub.url}</div>
                                    <div>
                                        <span class="subcategory-parser">${sub.parser_type || 'universal'}</span>
                                        <span class="subcategory-status ${sub.active ? 'active' : 'inactive'}">
                                            ${sub.active ? '활성' : '비활성'}
                                        </span>
                                    </div>
                                    ${sub.description ? `<div style="margin-top: 6px; font-size: 0.8rem; color: var(--text-secondary); font-style: italic;">${sub.description}</div>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        sourceElement.innerHTML = `
            <div class="source-header">
                <div class="source-info">
                    <div class="source-name">
                        <i class="fas ${source.is_parent ? 'fa-sitemap' : 'fa-globe'}"></i>
                        ${source.name}
                        ${source.is_parent ? '<span class="parent-badge">상위 출처</span>' : ''}
                    </div>
                    <div class="source-meta">
                        <div class="source-url">${source.url}</div>
                        ${!source.is_parent ? `<span class="source-parser">${source.parser_type || 'universal'}</span>` : ''}
                        <span class="source-status ${source.active ? 'active' : 'inactive'}">
                            ${source.active ? '활성' : '비활성'}
                        </span>
                    </div>
                    ${source.description ? `<div class="source-description">${source.description}</div>` : ''}
                </div>
                <div class="source-actions">
                    <button type="button" class="btn btn-primary" onclick="editSource('${source.id}')">
                        <i class="fas fa-edit"></i>
                        수정
                    </button>
                    <button type="button" class="btn btn-danger" onclick="deleteSource('${source.id}')">
                        <i class="fas fa-trash"></i>
                        삭제
                    </button>
                </div>
            </div>
            ${subcategoriesHtml}
        `;
        
        elements.sourcesList.appendChild(sourceElement);
    });
}

function showAddSourceModal() {
    currentEditingSource = null;
    
    if (elements.sourceModalTitle) {
        elements.sourceModalTitle.innerHTML = '<i class="fas fa-plus"></i> 새 출처 추가';
    }
    
    // 폼 초기화
    if (elements.sourceForm) {
        elements.sourceForm.reset();
    }
    if (elements.sourceActiveCheckbox) {
        elements.sourceActiveCheckbox.checked = true;
    }
    
    showSourceModal();
}

function editSource(sourceId) {
    const source = availableSources.find(s => s.id === sourceId);
    if (!source) {
        showToast('출처를 찾을 수 없습니다.', 'error');
        return;
    }
    
    currentEditingSource = source;
    
    if (elements.sourceModalTitle) {
        elements.sourceModalTitle.innerHTML = '<i class="fas fa-edit"></i> 출처 수정';
    }
    
    // 폼 초기화
    if (elements.sourceForm) {
        elements.sourceForm.reset();
    }
    
    // 기본 정보 채우기
    if (elements.sourceNameInput) elements.sourceNameInput.value = source.name || '';
    if (elements.sourceUrlInput) elements.sourceUrlInput.value = source.url || '';
    if (elements.sourceDescriptionInput) elements.sourceDescriptionInput.value = source.description || '';
    if (elements.sourceActiveCheckbox) elements.sourceActiveCheckbox.checked = source.active !== false;
    
    // 부모 출처 여부 설정
    if (elements.sourceIsParentCheckbox) {
        elements.sourceIsParentCheckbox.checked = source.is_parent === true;
        toggleParentSourceFields(); // UI 상태 업데이트
    }
    
    // 부모 출처가 아닌 경우 파서 타입 설정
    if (!source.is_parent) {
        if (elements.sourceParserTypeSelect) {
            elements.sourceParserTypeSelect.value = source.parser_type || 'universal';
        }
    }
    
    // 부모 출처인 경우 서브 카테고리 데이터 복원
    if (source.is_parent && source.subcategories && source.subcategories.length > 0) {
        // 서브 카테고리 리스트 초기화
        if (elements.subcategoriesList) {
            elements.subcategoriesList.innerHTML = '';
        }
        
        // 각 서브 카테고리 폼 생성
        source.subcategories.forEach((subcategory, index) => {
            const subcategoryId = `subcategory-${Date.now()}-${index}`;
            const subcategoryHtml = `
                <div class="subcategory-item" data-subcategory-id="${subcategoryId}">
                    <div class="subcategory-header">
                        <h5><i class="fas fa-tag"></i> 서브 카테고리 ${index + 1}</h5>
                        <button type="button" class="btn btn-danger btn-sm" onclick="removeSubcategoryForm('${subcategoryId}')">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="subcategory-form">
                        <div class="form-group">
                            <label>이름 *</label>
                            <input type="text" class="subcategory-name" value="${subcategory.name || ''}" placeholder="예: Latest News, Tech, Crypto" required>
                        </div>
                        <div class="form-group">
                            <label>URL 경로 *</label>
                            <input type="text" class="subcategory-url" value="${subcategory.url || ''}" placeholder="예: /topic/latest-news/" required>
                        </div>
                        <div class="form-group">
                            <label>파서 타입</label>
                            <select class="subcategory-parser-type">
                                <option value="universal" ${subcategory.parser_type === 'universal' ? 'selected' : ''}>Universal</option>
                                <option value="yahoo_finance" ${subcategory.parser_type === 'yahoo_finance' ? 'selected' : ''}>Yahoo Finance</option>
                                <option value="generic" ${subcategory.parser_type === 'generic' ? 'selected' : ''}>일반</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>설명</label>
                            <textarea class="subcategory-description" rows="2" placeholder="서브 카테고리 설명">${subcategory.description || ''}</textarea>
                        </div>
                        <div class="form-group">
                            <label class="checkbox-label">
                                <input type="checkbox" class="subcategory-active" ${subcategory.active !== false ? 'checked' : ''}>
                                <span class="checkmark"></span>
                                활성화
                            </label>
                        </div>
                    </div>
                </div>
            `;
            
            if (elements.subcategoriesList) {
                elements.subcategoriesList.insertAdjacentHTML('beforeend', subcategoryHtml);
            }
        });
    }
    
    showSourceModal();
}

async function deleteSource(sourceId) {
    const source = availableSources.find(s => s.id === sourceId);
    if (!source) return;
    
    if (!confirm(`'${source.name}' 출처를 삭제하시겠습니까?`)) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/sources/${sourceId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('출처가 성공적으로 삭제되었습니다.', 'success');
            
            // 로컬 데이터 업데이트
            availableSources = availableSources.filter(s => s.id !== sourceId);
            selectedSourceIds = selectedSourceIds.filter(id => id !== sourceId);
            
            displaySourcesList();
            updateSelectedSourcesDisplay();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('출처 삭제 오류:', error);
        showToast('출처 삭제 중 오류가 발생했습니다.', 'error');
    }
}

function showSourceModal() {
    if (elements.sourceModalSection) {
        elements.sourceModalSection.style.display = 'block';
    }
}

function hideSourceModal() {
    if (elements.sourceModalSection) {
        elements.sourceModalSection.style.display = 'none';
    }
    currentEditingSource = null;
}

async function saveSource() {
    if (!elements.sourceForm) return;
    
    // 폼 데이터 수집
    const formData = {
        name: elements.sourceNameInput?.value.trim(),
        url: elements.sourceUrlInput?.value.trim(),
        parser_type: elements.sourceParserTypeSelect?.value || 'yahoo_finance',
        description: elements.sourceDescriptionInput?.value.trim(),
        active: elements.sourceActiveCheckbox?.checked !== false
    };
    
    // 유효성 검증
    if (!formData.name) {
        showToast('출처명을 입력해주세요.', 'error');
        return;
    }
    
    if (!formData.url) {
        showToast('URL을 입력해주세요.', 'error');
        return;
    }
    
    if (!isValidUrl(formData.url)) {
        showToast('올바른 URL 형식을 입력해주세요.', 'error');
        return;
    }
    
    try {
        let response;
        
        if (currentEditingSource) {
            // 수정
            response = await fetch(`${API_BASE_URL}/api/sources/${currentEditingSource.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
        } else {
            // 추가
            response = await fetch(`${API_BASE_URL}/api/sources`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
        }
        
        const result = await response.json();
        
        if (result.success) {
            const action = currentEditingSource ? '수정' : '추가';
            showToast(`출처가 성공적으로 ${action}되었습니다.`, 'success');
            
            // 출처 목록 새로고침
            await loadAvailableSources();
            displaySourcesList();
            hideSourceModal();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('출처 저장 오류:', error);
        showToast('출처 저장 중 오류가 발생했습니다.', 'error');
    }
}

function showSourceSelectionModal() {
    if (elements.sourceSelectionModalSection) {
        elements.sourceSelectionModalSection.style.display = 'block';
        resetSelectionSteps();
        displaySourceTypes();
    }
}

function hideSourceSelectionModal() {
    if (elements.sourceSelectionModalSection) {
        elements.sourceSelectionModalSection.style.display = 'none';
    }
    resetSelectionSteps();
}

function resetSelectionSteps() {
    // 단계 네비게이션 리셋
    if (elements.step1Nav) elements.step1Nav.classList.add('active');
    if (elements.step2Nav) elements.step2Nav.classList.remove('active', 'completed');
    
    // 콘텐츠 표시 리셋
    if (elements.step1Content) elements.step1Content.style.display = 'block';
    if (elements.step2Content) elements.step2Content.style.display = 'none';
    if (elements.selectionSummary) elements.selectionSummary.style.display = 'none';
    
    // 상태 리셋
    currentSelectedParentSource = null;
    tempSelectedSubcategories = [];
    
    // 버튼 상태 리셋
    if (elements.nextToStep2Btn) elements.nextToStep2Btn.disabled = true;
}

function displaySourceTypes() {
    if (!elements.sourceTypeList) return;
    
    elements.sourceTypeList.innerHTML = '';
    
    // 부모 출처들과 독립 출처들을 분리
    const parentSources = availableSources.filter(source => source.is_parent);
    const standaloneSources = availableSources.filter(source => !source.is_parent);
    
    // 부모 출처들 표시
    parentSources.forEach(source => {
        const subcategoryCount = source.subcategories ? source.subcategories.filter(sub => sub.active).length : 0;
        
        const sourceTypeCard = document.createElement('div');
        sourceTypeCard.className = 'source-type-card';
        sourceTypeCard.dataset.sourceId = source.id;
        
        sourceTypeCard.innerHTML = `
            <div class="source-icon">
                <i class="fas fa-sitemap"></i>
            </div>
            <div class="source-name">${source.name}</div>
            <div class="source-description">${source.description || '다양한 카테고리의 뉴스를 제공합니다'}</div>
            <div class="source-stats">
                <span>상위 출처</span>
                <span class="subcategory-count">${subcategoryCount}개 카테고리</span>
            </div>
        `;
        
        sourceTypeCard.addEventListener('click', () => selectSourceType(source));
        elements.sourceTypeList.appendChild(sourceTypeCard);
    });
    
    // 독립 출처들 표시
    standaloneSources.forEach(source => {
        const sourceTypeCard = document.createElement('div');
        sourceTypeCard.className = 'source-type-card';
        sourceTypeCard.dataset.sourceId = source.id;
        
        sourceTypeCard.innerHTML = `
            <div class="source-icon">
                <i class="fas fa-globe"></i>
            </div>
            <div class="source-name">${source.name}</div>
            <div class="source-description">${source.description || '단일 출처 뉴스를 제공합니다'}</div>
            <div class="source-stats">
                <span>독립 출처</span>
                <span class="subcategory-count">직접 추출</span>
            </div>
        `;
        
        sourceTypeCard.addEventListener('click', () => selectSourceType(source));
        elements.sourceTypeList.appendChild(sourceTypeCard);
    });
}

function selectSourceType(source) {
    // 이전 선택 해제
    elements.sourceTypeList.querySelectorAll('.source-type-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // 새 선택 표시
    const selectedCard = elements.sourceTypeList.querySelector(`[data-source-id="${source.id}"]`);
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }
    
    currentSelectedParentSource = source;
    
    // 다음 단계 버튼 활성화
    if (elements.nextToStep2Btn) {
        elements.nextToStep2Btn.disabled = false;
    }
}

function goToStep2() {
    if (!currentSelectedParentSource) return;
    
    // 단계 네비게이션 업데이트
    if (elements.step1Nav) {
        elements.step1Nav.classList.remove('active');
        elements.step1Nav.classList.add('completed');
    }
    if (elements.step2Nav) elements.step2Nav.classList.add('active');
    
    // 콘텐츠 전환
    if (elements.step1Content) elements.step1Content.style.display = 'none';
    if (elements.step2Content) elements.step2Content.style.display = 'block';
    
    // 선택된 출처명 표시
    if (elements.selectedSourceName) {
        elements.selectedSourceName.textContent = `${currentSelectedParentSource.name}의 카테고리를 선택해주세요`;
    }
    
    // 독립 출처인 경우 바로 확인
    if (!currentSelectedParentSource.is_parent) {
        window.selectedSourceIds = [currentSelectedParentSource.id];
        updateSelectionSummary();
        if (elements.selectionSummary) elements.selectionSummary.style.display = 'block';
        return;
    }
    
    // 서브 카테고리 표시
    displaySubcategories();
}

function displaySubcategories() {
    if (!elements.subcategorySelectionList || !currentSelectedParentSource) return;
    
    elements.subcategorySelectionList.innerHTML = '';
    
    if (!currentSelectedParentSource.subcategories || currentSelectedParentSource.subcategories.length === 0) {
        elements.subcategorySelectionList.innerHTML = `
            <div style="text-align: center; padding: 40px; color: var(--text-secondary);">
                <i class="fas fa-info-circle" style="font-size: 2rem; margin-bottom: 16px;"></i>
                <p>이 출처에는 서브 카테고리가 없습니다.</p>
            </div>
        `;
        return;
    }
    
    currentSelectedParentSource.subcategories.forEach(subcategory => {
        const subcategoryCard = document.createElement('div');
        subcategoryCard.className = 'subcategory-selection-card';
        subcategoryCard.dataset.subcategoryId = subcategory.id;
        
        subcategoryCard.innerHTML = `
            <div class="category-checkbox"></div>
            <div class="category-icon">
                <i class="fas fa-tag"></i>
            </div>
            <div class="category-name">${subcategory.name}</div>
            <div class="category-url">${currentSelectedParentSource.url}${subcategory.url}</div>
            ${subcategory.description ? `<div class="category-description">${subcategory.description}</div>` : ''}
            <div class="category-meta">
                <span class="category-parser">${subcategory.parser_type || 'universal'}</span>
                <span class="category-status ${subcategory.active ? 'active' : 'inactive'}">
                    ${subcategory.active ? '활성' : '비활성'}
                </span>
            </div>
        `;
        
        subcategoryCard.addEventListener('click', () => toggleSubcategorySelection(subcategory.id));
        elements.subcategorySelectionList.appendChild(subcategoryCard);
    });
}

function toggleSubcategorySelection(subcategoryId) {
    const index = tempSelectedSubcategories.indexOf(subcategoryId);
    
    if (index > -1) {
        tempSelectedSubcategories.splice(index, 1);
    } else {
        tempSelectedSubcategories.push(subcategoryId);
    }
    
    updateSubcategorySelectionDisplay();
    updateSelectionSummary();
}

function updateSubcategorySelectionDisplay() {
    if (!elements.subcategorySelectionList) return;
    
    elements.subcategorySelectionList.querySelectorAll('.subcategory-selection-card').forEach(card => {
        const subcategoryId = card.dataset.subcategoryId;
        const isSelected = tempSelectedSubcategories.includes(subcategoryId);
        
        if (isSelected) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    });
}

function selectAllSources() {
    if (!currentSelectedParentSource || !currentSelectedParentSource.subcategories) return;
    
    tempSelectedSubcategories = currentSelectedParentSource.subcategories
        .filter(sub => sub.active)
        .map(sub => sub.id);
    
    updateSubcategorySelectionDisplay();
    updateSelectionSummary();
}

function deselectAllSources() {
    tempSelectedSubcategories = [];
    updateSubcategorySelectionDisplay();
    updateSelectionSummary();
}

function updateSelectionSummary() {
    if (!elements.selectedItemsSummary) return;
    
    let selectedItems = [];
    
    if (currentSelectedParentSource) {
        if (currentSelectedParentSource.is_parent && tempSelectedSubcategories.length > 0) {
            // 부모 출처의 서브 카테고리들
            tempSelectedSubcategories.forEach(subId => {
                const subcategory = currentSelectedParentSource.subcategories.find(sub => sub.id === subId);
                if (subcategory) {
                    selectedItems.push(`${currentSelectedParentSource.name} - ${subcategory.name}`);
                }
            });
        } else if (!currentSelectedParentSource.is_parent) {
            // 독립 출처
            selectedItems.push(currentSelectedParentSource.name);
        }
    }
    
    elements.selectedItemsSummary.innerHTML = selectedItems.map(item => `
        <span class="selected-item-tag">
            <i class="fas fa-check"></i>
            ${item}
        </span>
    `).join('');
    
    if (selectedItems.length > 0 && elements.selectionSummary) {
        elements.selectionSummary.style.display = 'block';
    }
}

function goToStep1() {
    // 단계 네비게이션 업데이트
    if (elements.step1Nav) {
        elements.step1Nav.classList.add('active');
        elements.step1Nav.classList.remove('completed');
    }
    if (elements.step2Nav) {
        elements.step2Nav.classList.remove('active');
    }
    
    // 콘텐츠 전환
    if (elements.step1Content) elements.step1Content.style.display = 'block';
    if (elements.step2Content) elements.step2Content.style.display = 'none';
    if (elements.selectionSummary) elements.selectionSummary.style.display = 'none';
    
    // 2단계 상태 리셋
    tempSelectedSubcategories = [];
}

function confirmSourceSelection() {
    if (!currentSelectedParentSource) {
        showToast('출처를 선택해주세요.', 'error');
        return;
    }
    
    // 선택된 항목들을 전역 상태에 저장
    if (currentSelectedParentSource.is_parent) {
        if (tempSelectedSubcategories.length === 0) {
            showToast('최소 하나의 카테고리를 선택해주세요.', 'error');
            return;
        }
        window.selectedSourceIds = [...tempSelectedSubcategories];
    } else {
        window.selectedSourceIds = [currentSelectedParentSource.id];
    }
    
    // 모달 닫기 및 메인 화면 업데이트
    hideSourceSelectionModal();
    updateSelectedSourcesDisplay();
    saveUserPreferences();
    
    showToast(`${window.selectedSourceIds.length}개 출처가 선택되었습니다.`, 'success');
}

// ============================================================================
// 계층적 출처 관리 함수들
// ============================================================================

function toggleParentSourceFields() {
    if (!elements.sourceIsParentCheckbox) return;
    
    const isParent = elements.sourceIsParentCheckbox.checked;
    
    if (isParent) {
        elements.subcategoriesSection.style.display = 'block';
        elements.parserTypeGroup.style.display = 'none';
    } else {
        elements.subcategoriesSection.style.display = 'none';
        elements.parserTypeGroup.style.display = 'block';
        // 서브 카테고리 리스트 비우기
        elements.subcategoriesList.innerHTML = '';
    }
}

function addSubcategoryForm() {
    if (!elements.subcategoriesList) return;
    
    const subcategoryId = `subcategory-${Date.now()}`;
    const subcategoryHtml = `
        <div class="subcategory-item" data-subcategory-id="${subcategoryId}">
            <div class="subcategory-header">
                <h5><i class="fas fa-tag"></i> 서브 카테고리</h5>
                <button type="button" class="btn btn-danger btn-sm" onclick="removeSubcategoryForm('${subcategoryId}')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="subcategory-form">
                <div class="form-group">
                    <label>이름 *</label>
                    <input type="text" class="subcategory-name" placeholder="예: Latest News, Tech, Crypto" required>
                </div>
                <div class="form-group">
                    <label>URL 경로 *</label>
                    <input type="text" class="subcategory-url" placeholder="예: /topic/latest-news/" required>
                </div>
                <div class="form-group">
                    <label>파서 타입</label>
                    <select class="subcategory-parser-type">
                        <option value="universal">Universal</option>
                        <option value="yahoo_finance">Yahoo Finance</option>
                        <option value="generic">일반</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>설명</label>
                    <textarea class="subcategory-description" rows="2" placeholder="서브 카테고리 설명"></textarea>
                </div>
                <div class="form-group">
                    <label class="checkbox-label">
                        <input type="checkbox" class="subcategory-active" checked>
                        <span class="checkmark"></span>
                        활성화
                    </label>
                </div>
            </div>
        </div>
    `;
    
    elements.subcategoriesList.insertAdjacentHTML('beforeend', subcategoryHtml);
}

function removeSubcategoryForm(subcategoryId) {
    const subcategoryElement = document.querySelector(`[data-subcategory-id="${subcategoryId}"]`);
    if (subcategoryElement) {
        subcategoryElement.remove();
    }
}

function getSubcategoriesData() {
    const subcategoryItems = document.querySelectorAll('.subcategory-item');
    const subcategories = [];
    
    subcategoryItems.forEach(item => {
        const name = item.querySelector('.subcategory-name').value.trim();
        const url = item.querySelector('.subcategory-url').value.trim();
        const parserType = item.querySelector('.subcategory-parser-type').value;
        const description = item.querySelector('.subcategory-description').value.trim();
        const active = item.querySelector('.subcategory-active').checked;
        
        if (name && url) {
            subcategories.push({
                name,
                url,
                parser_type: parserType,
                description,
                active
            });
        }
    });
    
    return subcategories;
}

// 계층적 출처 목록 표시 함수 재정의
function displaySourcesList() {
    if (!elements.sourcesList) return;
    
    if (availableSources.length === 0) {
        elements.sourcesList.innerHTML = '<div class="no-sources">등록된 출처가 없습니다.</div>';
        return;
    }
    
    elements.sourcesList.innerHTML = '';
    
    availableSources.forEach(source => {
        const sourceHtml = `
            <div class="source-item ${source.active ? 'active' : 'inactive'}">
                <div class="source-header">
                    <div class="source-info">
                        <h4>
                            <i class="fas ${source.is_parent ? 'fa-sitemap' : 'fa-globe'}"></i>
                            ${source.name}
                            ${source.is_parent ? '<span class="parent-badge">상위 출처</span>' : ''}
                        </h4>
                        <div class="source-meta">
                            <span class="source-url">${source.url}</span>
                            ${!source.is_parent ? `<span class="source-parser">${source.parser_type}</span>` : ''}
                            <span class="source-status ${source.active ? 'active' : 'inactive'}">
                                ${source.active ? '활성' : '비활성'}
                            </span>
                        </div>
                        ${source.description ? `<p class="source-description">${source.description}</p>` : ''}
                    </div>
                    <div class="source-actions">
                        <button type="button" class="btn btn-sm btn-primary" onclick="editSource('${source.id}')">
                            <i class="fas fa-edit"></i>
                            수정
                        </button>
                        <button type="button" class="btn btn-sm btn-danger" onclick="deleteSource('${source.id}')">
                            <i class="fas fa-trash"></i>
                            삭제
                        </button>
                    </div>
                </div>
                
                ${source.is_parent && source.subcategories && source.subcategories.length > 0 ? `
                    <div class="subcategories-display">
                        <h5><i class="fas fa-list"></i> 서브 카테고리</h5>
                        <div class="subcategories-grid">
                            ${source.subcategories.map(sub => `
                                <div class="subcategory-card ${sub.active ? 'active' : 'inactive'}">
                                    <div class="subcategory-info">
                                        <h6>${sub.name}</h6>
                                        <span class="subcategory-url">${sub.url}</span>
                                        <span class="subcategory-parser">${sub.parser_type}</span>
                                        <span class="subcategory-status ${sub.active ? 'active' : 'inactive'}">
                                            ${sub.active ? '활성' : '비활성'}
                                        </span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        elements.sourcesList.insertAdjacentHTML('beforeend', sourceHtml);
    });
}

// 계층적 출처 선택 리스트 표시 함수 재정의
function displaySourceSelectionList() {
    // 이 함수는 새로운 2단계 선택 시스템으로 대체됨
    console.log('이 함수는 더 이상 사용되지 않습니다. showSourceSelectionModal을 사용하세요.');
}

// 출처 저장 함수 재정의 (계층적 구조 지원)
async function saveSource() {
    if (!elements.sourceNameInput || !elements.sourceUrlInput) return;
    
    const isParent = elements.sourceIsParentCheckbox ? elements.sourceIsParentCheckbox.checked : false;
    
    const formData = {
        name: elements.sourceNameInput.value.trim(),
        url: elements.sourceUrlInput.value.trim(),
        is_parent: isParent,
        active: elements.sourceActiveCheckbox ? elements.sourceActiveCheckbox.checked : true,
        description: elements.sourceDescriptionInput ? elements.sourceDescriptionInput.value.trim() : ''
    };
    
    // 단독 출처인 경우에만 parser_type 추가
    if (!isParent) {
        formData.parser_type = elements.sourceParserTypeSelect ? elements.sourceParserTypeSelect.value : 'universal';
    }
    
    // 상위 출처인 경우 서브 카테고리 추가
    if (isParent) {
        formData.subcategories = getSubcategoriesData();
        
        if (formData.subcategories.length === 0) {
            showToast('상위 출처는 최소 하나의 서브 카테고리가 필요합니다.', 'error');
            return;
        }
    }
    
    // 유효성 검증
    if (!formData.name) {
        showToast('출처명을 입력해주세요.', 'error');
        return;
    }
    
    if (!formData.url) {
        showToast('URL을 입력해주세요.', 'error');
        return;
    }
    
    if (!isValidUrl(formData.url)) {
        showToast('올바른 URL 형식을 입력해주세요.', 'error');
        return;
    }
    
    try {
        let response;
        
        if (currentEditingSource) {
            // 수정
            response = await fetch(`${API_BASE_URL}/api/sources/${currentEditingSource.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
        } else {
            // 추가
            response = await fetch(`${API_BASE_URL}/api/sources`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
        }
        
        const result = await response.json();
        
        if (result.success) {
            const action = currentEditingSource ? '수정' : '추가';
            showToast(`출처가 성공적으로 ${action}되었습니다.`, 'success');
            
            // 출처 목록 새로고침
            await loadAvailableSources();
            displaySourcesList();
            hideSourceModal();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('출처 저장 오류:', error);
        showToast('출처 저장 중 오류가 발생했습니다.', 'error');
    }
}

// API 키 토글 기능
function toggleApiKeyVisibility() {
    const apiKeyInput = elements.apiKeyInput;
    const toggleBtn = elements.toggleApiKeyBtn;
    
    if (apiKeyInput && toggleBtn) {
        const isPassword = apiKeyInput.type === 'password';
        apiKeyInput.type = isPassword ? 'text' : 'password';
        toggleBtn.innerHTML = isPassword ? '<i class="fas fa-eye-slash"></i>' : '<i class="fas fa-eye"></i>';
    }
}