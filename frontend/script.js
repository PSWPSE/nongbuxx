// 최적화된 JavaScript - 성능 개선 및 핵심 기능 중심
// 전역 변수
let currentJobId = null;
let currentData = null;
let currentBatchJobId = null;
let currentBatchData = null;
let extractedNews = [];
let selectedNewsUrls = [];
let sessionContent = []; // 현재 세션에서 생성한 콘텐츠만 관리
let currentTheme = 'auto';
let urlInputCount = 1;
const maxUrlInputs = 20;
const API_BASE_URL = window.ENV?.API_BASE_URL || 'http://localhost:8080';

// 탭 상태 관리
const tabState = {
    current: 'news-extraction',
    tabs: ['news-extraction', 'content-generation', 'generated-content'],
    badges: {
        'news-extraction': 0,
        'content-generation': 0,
        'generated-content': 0
    }
};

// DOM 요소 캐싱
const elements = {
    urlForm: document.getElementById('urlForm'),
    urlInputsContainer: document.getElementById('urlInputsContainer'),
    themeToggle: document.getElementById('themeToggle'),
    themeIcon: document.getElementById('themeIcon'),
    themeText: document.getElementById('themeText'),
    newsExtractorBtn: document.getElementById('newsExtractorBtn'),
    newsExtractorSection: document.getElementById('newsExtractorSection'),
    newsCount: document.getElementById('newsCount'),
    extractNewsBtn: document.getElementById('extractNewsBtn'),
    cancelNewsExtractorBtn: document.getElementById('cancelNewsExtractorBtn'),
    newsSelectionSection: document.getElementById('newsSelectionSection'),
    newsExtractionInfo: document.getElementById('newsExtractionInfo'),
    newsList: document.getElementById('newsList'),
    selectAllNewsBtn: document.getElementById('selectAllNewsBtn'),
    deselectAllNewsBtn: document.getElementById('deselectAllNewsBtn'),
    generateSelectedBtn: document.getElementById('generateSelectedBtn'),
    generateSelectedBtn2: document.getElementById('generateSelectedBtn2'),
    generatedContentListSection: document.getElementById('generatedContentListSection'),
    generatedContentList: document.getElementById('generatedContentList'),
    downloadAllGeneratedBtn: document.getElementById('downloadAllGeneratedBtn'),

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
    initTabs();
    loadApiSettings();
    initTheme();
    updateUrlInputButtons();
    initKeyboardShortcuts();
    loadUserPreferences();
    
    // 콘텐츠 타입 선택 초기화
    handleContentTypeChange();
    
    // 출처 관리 초기화
    loadAvailableSources();
    
    // 생성된 콘텐츠 탭 기능 초기화
    
    // 세션 콘텐츠 배지 초기화
    setTimeout(() => {
        console.log('🚀 세션 콘텐츠 배지 초기화');
        updateGeneratedContentBadge();
    }, 1000);
    
    // 마크다운 라이브러리 확인
    if (typeof marked === 'undefined') {
        console.warn('마크다운 라이브러리를 로드할 수 없습니다.');
    }
});

// ============================================================================
// 탭 관리 시스템
// ============================================================================

function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
            switchTab(targetTab);
        });
    });
    
    // 초기 탭 설정
    switchTab('news-extraction');
    
    // 생성된 콘텐츠 배지 초기화
    updateGeneratedContentBadge();
}

async function loadInitialGeneratedContentBadge() {
    updateTabBadge('generated-content', sessionContent.length);
    console.log('📋 생성된 콘텐츠 배지 초기화: 0 (세션 시작)');
}

function switchTab(tabName) {
    console.log(`🔄 탭 전환 시도: ${tabName}`);
    
    // 유효한 탭인지 확인
    if (!tabState.tabs.includes(tabName)) {
        console.error(`❌ 유효하지 않은 탭: ${tabName}`);
        return;
    }
    
    // 이전 탭 비활성화
    const previousTab = document.getElementById(`${tabState.current}-tab`);
    const previousButton = document.querySelector(`[data-tab="${tabState.current}"]`);
    
    console.log(`📤 이전 탭 비활성화: ${tabState.current}`);
    if (previousTab) {
        previousTab.classList.remove('active');
        previousTab.style.display = 'none';
    }
    if (previousButton) {
        previousButton.classList.remove('active');
    }
    
    // 새 탭 활성화
    const newTab = document.getElementById(`${tabName}-tab`);
    const newButton = document.querySelector(`[data-tab="${tabName}"]`);
    
    console.log(`📥 새 탭 활성화: ${tabName}`, {
        newTab: !!newTab,
        newButton: !!newButton
    });
    
    if (newTab) {
        newTab.classList.add('active');
        newTab.style.display = 'block';
    }
    if (newButton) {
        newButton.classList.add('active');
    }
    
    // 상태 업데이트
    tabState.current = tabName;
    
    // 탭 전환 시 특별 처리
    if (tabName === 'content-generation') {
        updateSelectedNewsSummary();
    } else if (tabName === 'generated-content') {
        console.log('📋 생성된 콘텐츠 탭 표시');
        showSessionContent();
    }
    
    console.log(`✅ 탭 전환 완료: ${tabName}`);
}

function updateTabBadge(tabName, count) {
    const button = document.querySelector(`[data-tab="${tabName}"]`);
    if (!button) return;
    
    let badge = button.querySelector('.badge');
    
    if (count > 0) {
        if (!badge) {
            badge = document.createElement('span');
            badge.className = 'badge';
            button.appendChild(badge);
        }
        badge.textContent = count;
        badge.style.display = 'inline-block';
    } else {
        if (badge) {
            badge.style.display = 'none';
        }
    }
    
    tabState.badges[tabName] = count;
}

function updateGeneratedContentBadge() {
    const badge = document.getElementById('generated-content-badge');
    if (badge && sessionContent.length > 0) {
        badge.textContent = sessionContent.length;
        badge.style.display = 'inline-block';
    } else if (badge) {
        badge.style.display = 'none';
    }
    updateTabBadge('generated-content', sessionContent.length);
}

function updateSelectedNewsSummary() {
    const summaryElement = document.getElementById('selectedNewsSummary');
    
    if (!summaryElement) return;
    
    // 선택된 뉴스가 없을 때
    if (selectedNewsUrls.length === 0) {
        summaryElement.innerHTML = `
            <h3>선택된 뉴스</h3>
            <p>뉴스 추출 탭에서 뉴스를 선택해주세요.</p>
        `;
        return;
    }
    
    const selectedArticles = extractedNews.filter(article => 
        selectedNewsUrls.includes(article.url)
    );
    
    summaryElement.innerHTML = `
        <h3>선택된 뉴스 (${selectedArticles.length}개)</h3>
        <div class="selected-news-list">
            ${selectedArticles.map((article, index) => `
                <div class="selected-news-item">
                    <div class="news-item-number">${index + 1}</div>
                    <div class="news-item-content">
                        <div class="news-item-title">${article.title.length > 60 ? article.title.substring(0, 60) + '...' : article.title}</div>
                        <div class="news-item-meta">
                            <div class="news-url">${article.url}</div>
                            ${article.source_name ? `<div class="news-source">
                                <i class="fas fa-globe"></i> ${article.source_name}
                            </div>` : ''}
                        </div>
                        ${article.keywords ? `<div class="news-keywords">
                            ${article.keywords.map(keyword => 
                                `<span class="keyword-tag">${keyword}</span>`
                            ).join('')}
                        </div>` : ''}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    
    // 콘텐츠 생성 탭의 버튼 활성화
    const generateSelectedBtn2 = document.getElementById('generateSelectedBtn2');
    
    if (generateSelectedBtn2) {
        generateSelectedBtn2.disabled = selectedArticles.length === 0;
        
        // 선택된 콘텐츠 타입에 따라 버튼 텍스트 업데이트
        const selectedType = getSelectedContentType();
        const typeNames = {
            'standard': 'X(Twitter) Normal Form',
            'threads': 'Threads',
            'x': 'X(Twitter) Short Form',
            'enhanced_blog': 'Blog'
        };
        
        const typeName = typeNames[selectedType] || '콘텐츠';
        
        generateSelectedBtn2.innerHTML = selectedArticles.length > 0 ? 
            `<i class="fas fa-magic"></i> ${typeName} 생성 (${selectedArticles.length}개)` : 
            `<i class="fas fa-magic"></i> ${typeName} 생성`;
    }
}

// ============================================================================
// 기존 이벤트 리스너 및 함수들
// ============================================================================

// 이벤트 리스너 초기화
function initEventListeners() {
    // 폼 제출
    if (elements.urlForm) {
        elements.urlForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const urls = getUrlsFromForm();
            if (urls.length === 0) {
                showToast('URL을 입력해주세요.', 'error');
                return;
            }
            
            // 선택된 콘텐츠 타입 확인
            const contentType = e.submitter.dataset.contentType || 'standard';
            
            // 버튼 상태 업데이트
            const buttons = elements.urlForm.querySelectorAll('button[type="submit"]');
            buttons.forEach(btn => {
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 처리 중...';
            });
            
            try {
                await handleFormSubmit(urls, contentType);
            } catch (error) {
                console.error('Content generation error:', error);
                showToast('콘텐츠 생성 중 오류가 발생했습니다.', 'error');
            } finally {
                // 버튼 상태 복구
                buttons.forEach(btn => {
                    btn.disabled = false;
                    btn.innerHTML = btn.innerHTML.replace(/<i class="fas fa-spinner fa-spin"><\/i> 처리 중.../, btn.innerHTML);
                });
            }
        });
    }
    
    // 테마 토글
    if (elements.themeToggle) {
        elements.themeToggle.addEventListener('click', toggleTheme);
    }
    
    // 뉴스 추출 관련 (메인 흐름)
    if (elements.extractNewsBtn) {
        elements.extractNewsBtn.addEventListener('click', handleNewsExtraction);
    }
    
    // URL 직접 입력 관련 (서브 흐름) - 제거됨
    // 삭제된 버튼: backToNewsExtractorBtn
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
    
    // 콘텐츠 생성 탭의 버튼
    const generateSelectedBtn2 = document.getElementById('generateSelectedBtn2');
    
    if (generateSelectedBtn2) {
        generateSelectedBtn2.addEventListener('click', handleGenerateSelectedNewsWithType);
    }
    
    // 콘텐츠 타입 변경 이벤트 리스너
    const contentTypeRadios = document.querySelectorAll('input[name="contentType"]');
    contentTypeRadios.forEach(radio => {
        radio.addEventListener('change', handleContentTypeChange);
    });

    
    // Blog 콘텐츠 생성 버튼 이벤트 리스너
    const generateEnhancedBlogBtn = document.getElementById('generateEnhancedBlogBtn');
    
    if (generateEnhancedBlogBtn) {
        generateEnhancedBlogBtn.addEventListener('click', handleEnhancedBlogGeneration);
    }
    
    // 생성된 콘텐츠 관련
    if (elements.downloadAllGeneratedBtn) {
        elements.downloadAllGeneratedBtn.addEventListener('click', downloadAllGeneratedContent);
    }

    // 생성된 콘텐츠 탭 초기화 버튼 이벤트 리스너 추가
    const resetGeneratedContentBtn = document.getElementById('resetGeneratedContentBtn');
    if (resetGeneratedContentBtn) {
        resetGeneratedContentBtn.addEventListener('click', resetGeneratedContent);
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
        elements.sourceManagementBtn.addEventListener('click', showParentSourceManagementModal);
    }
    if (elements.closeSourceManagementBtn) {
        elements.closeSourceManagementBtn.addEventListener('click', hideParentSourceManagementModal);
    }
    
    // 부모 출처 관리
    const addParentSourceBtn = document.getElementById('addParentSourceBtn');
    if (addParentSourceBtn) {
        addParentSourceBtn.addEventListener('click', showAddParentSourceModal);
    }
    const closeParentSourceModalBtn = document.getElementById('closeParentSourceModalBtn');
    if (closeParentSourceModalBtn) {
        closeParentSourceModalBtn.addEventListener('click', hideParentSourceModal);
    }
    const saveParentSourceBtn = document.getElementById('saveParentSourceBtn');
    if (saveParentSourceBtn) {
        saveParentSourceBtn.addEventListener('click', saveParentSource);
    }
    
    // 서브카테고리 관리
    const backToParentSourcesBtn = document.getElementById('backToParentSourcesBtn');
    if (backToParentSourcesBtn) {
        backToParentSourcesBtn.addEventListener('click', showParentSourceManagementModal);
    }
    const closeSubcategoryManagementBtn = document.getElementById('closeSubcategoryManagementBtn');
    if (closeSubcategoryManagementBtn) {
        closeSubcategoryManagementBtn.addEventListener('click', hideSubcategoryManagementModal);
    }
    const addSubcategoryBtn = document.getElementById('addSubcategoryBtn');
    if (addSubcategoryBtn) {
        addSubcategoryBtn.addEventListener('click', showAddSubcategoryModal);
    }
    const closeSubcategoryModalBtn = document.getElementById('closeSubcategoryModalBtn');
    if (closeSubcategoryModalBtn) {
        closeSubcategoryModalBtn.addEventListener('click', hideSubcategoryModal);
    }
    const saveSubcategoryBtn = document.getElementById('saveSubcategoryBtn');
    if (saveSubcategoryBtn) {
        saveSubcategoryBtn.addEventListener('click', saveSubcategory);
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
    
    // 뉴스 추출 관련 버튼들
    const backToNewsExtractionBtn = document.getElementById('backToNewsExtractionBtn');
    if (backToNewsExtractionBtn) {
        backToNewsExtractionBtn.addEventListener('click', () => switchTab('news-extraction'));
    }
    
    // 삭제된 버튼: backToExtractorBtn
    
    const confirmSelectedNewsBtn = document.getElementById('confirmSelectedNewsBtn');
    if (confirmSelectedNewsBtn) {
        confirmSelectedNewsBtn.addEventListener('click', handleConfirmSelectedNews);
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

// Blog 콘텐츠 생성 처리
async function handleEnhancedBlogGeneration() {
    await generateContent('enhanced_blog');
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
            if (contentType === 'enhanced_blog') {
                progressTitle.textContent = 'Blog 콘텐츠 생성 중...';
            } else {
                progressTitle.textContent = '콘텐츠 생성 중...';
            }
        }
        
        // 프로그레스 시뮬레이션 시작 (Blog 콘텐츠는 가장 오래 걸림)
        let duration = 60000; // 기본값 (2배 증가)
        if (contentType === 'enhanced_blog') {
            duration = 120000; // Blog는 더 오래 걸림 (2배 증가)
        }
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
            if (response.status === 404) {
                // 키워드가 있는 경우와 없는 경우 구분
                if (keyword && keyword.trim() !== '') {
                    showToast(`"${keyword}" 키워드와 관련된 뉴스를 찾을 수 없습니다.`, 'warning');
                } else {
                    showToast('선택한 출처에서 뉴스를 찾을 수 없습니다.', 'warning');
                }
                return;
            }
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
        
        // 🚀 개선된 에러 메시지
        let userFriendlyMessage = error.message;
        
        if (error.message.includes('Maximum 20 URLs allowed') || error.message.includes('20 URLs')) {
            userFriendlyMessage = `⚠️ 뉴스 개수 제한: 최대 20개의 뉴스만 선택할 수 있습니다. 안정성을 위한 제한입니다.`;
        } else if (error.message.includes('INVALID_API_PROVIDER') || error.message.includes('API provider must be')) {
            userFriendlyMessage = `🔑 API 키 미설정: 우측 상단 'API 키 설정' 버튼을 클릭하여 Anthropic 또는 OpenAI API 키를 설정해주세요.`;
        } else if (error.message.includes('network') || error.message.includes('연결')) {
            userFriendlyMessage = `🌐 네트워크 오류: 인터넷 연결을 확인하고 다시 시도해주세요.`;
        } else if (error.message.includes('API')) {
            userFriendlyMessage = `🔑 API 오류: API 키를 확인하고 다시 시도해주세요.`;
        } else if (error.message.includes('500')) {
            userFriendlyMessage = `🔧 서버 오류: 서버에 일시적인 문제가 있습니다. 잠시 후 다시 시도해주세요.`;
        } else if (error.message.includes('400')) {
            userFriendlyMessage = `⚠️ 요청 오류: API 키 설정을 확인하고 다시 시도해주세요.`;
        }
        
        showErrorSection(userFriendlyMessage);
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

// 섹션 표시/숨기기 (탭 시스템 호환)
function hideAllSections() {
    const sections = [
        elements.progressSection,
        elements.resultSection,
        elements.errorSection,
        elements.generatedContentListSection
    ];
    
    // 기본 섹션들 숨기기
    sections.forEach(section => {
        if (section) section.style.display = 'none';
    });
    
    // URL 입력 섹션 숨기기
    // urlInputSection 제거됨
    
    // 뉴스 선택 섹션은 조건부로 숨기기 (뉴스가 있고 뉴스 추출 탭인 경우 유지)
    if (elements.newsSelectionSection) {
        if (tabState.current === 'news-extraction' && extractedNews.length > 0) {
            // 뉴스 추출 탭이고 추출된 뉴스가 있으면 뉴스 선택 섹션 유지
            elements.newsSelectionSection.style.display = 'block';
        } else {
            // 그 외의 경우 숨김
            elements.newsSelectionSection.style.display = 'none';
        }
    }
    
    // 현재 탭에 따라 기본 섹션 표시
    if (tabState.current === 'news-extraction') {
        const newsExtractorSection = document.getElementById('newsExtractorSection');
        if (newsExtractorSection) {
            newsExtractorSection.style.display = 'block';
        }
    } else if (tabState.current === 'content-generation') {
        const contentGenerationSection = document.getElementById('contentGenerationSection');
        if (contentGenerationSection) {
            contentGenerationSection.style.display = 'block';
        }
    }
}

function showProgressSection() {
    // 콘텐츠 생성 탭으로 전환
    switchTab('content-generation');
    
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
let parentSources = [];
let standaloneSources = [];
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
    // 콘텐츠 생성 탭으로 전환
    switchTab('content-generation');
    
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
    // 콘텐츠 생성 탭으로 전환
    switchTab('content-generation');
    
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
    // 뉴스 추출 탭으로 전환
    switchTab('news-extraction');
    
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

// URL 직접 입력 섹션 관리 함수들 - 제거됨

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
    const keyword = ''; // 키워드 입력 창이 제거되어 빈 문자열로 고정
    const count = elements.newsCount ? parseInt(elements.newsCount.value) || 10 : 10;
    
    if (count < 1 || count > 50) {
        showToast('추출할 뉴스 개수는 1-50개 사이여야 합니다.', 'error');
        return;
    }
    
    // 🚨 중요: 뉴스 추출 시 이전 선택 상태 완전 초기화
    selectedNewsUrls = [];
    console.log('🔄 뉴스 추출 시작: 이전 선택 상태 초기화 완료');
    
    // 🚀 선택된 출처 ID 최종 검증
    const validSourceIds = selectedSourceIds.filter(id => 
        availableSources.some(source => source.id === id && source.active)
    );
    
    if (validSourceIds.length === 0) {
        showToast('유효한 출처를 선택해주세요.', 'error');
        return;
    }
    
    // 유효하지 않은 출처가 있으면 자동 동기화
    if (validSourceIds.length !== selectedSourceIds.length) {
        selectedSourceIds = validSourceIds;
        updateSelectedSourcesDisplay();
        console.log('🔄 뉴스 추출 시 유효하지 않은 출처 ID 자동 제거됨');
    }
    
    try {
        if (elements.extractNewsBtn) {
            elements.extractNewsBtn.disabled = true;
            elements.extractNewsBtn.innerHTML = '<div class="spinner"></div> 추출 중...';
        }
        
        const requestData = {
            keyword, 
            count,
            sources: validSourceIds  // 검증된 출처들만 전송
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
                // 키워드가 있는 경우와 없는 경우 구분
                if (keyword && keyword.trim() !== '') {
                    showToast(`"${keyword}" 키워드와 관련된 뉴스를 찾을 수 없습니다.`, 'warning');
                } else {
                    showToast('선택한 출처에서 뉴스를 찾을 수 없습니다.', 'warning');
                }
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
    // 뉴스 추출 탭으로 전환
    switchTab('news-extraction');
    
    hideAllSections();
    if (elements.newsSelectionSection) {
        elements.newsSelectionSection.style.display = 'block';
    }
    
    // 🚨 중요: 뉴스 선택 섹션 표시 시 상태 초기화 확인
    console.log(`🔄 뉴스 선택 섹션 표시: ${selectedNewsUrls.length}개 선택됨 (초기화 완료됨)`);
    
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
            ${extractedNews.length > 20 ? `
                <div class="news-limit-notice">
                    <i class="fas fa-info-circle"></i>
                    <span>💡 20개 이상 선택 시 자동으로 처음 20개만 처리됩니다.</span>
                </div>
            ` : ''}
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
                <div class="news-item-actions">
                    <button class="btn-action btn-preview" onclick="previewNewsContent('${article.url}', '${article.title.replace(/'/g, '\\\'')}')" title="뉴스 미리보기" data-action="preview">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-action btn-external" onclick="window.open('${article.url}', '_blank')" title="원본 보기" data-action="external">
                        <i class="fas fa-external-link-alt"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    
    // 선택 상태 복원
    restoreNewsSelection();
    
    // 클릭 이벤트 추가
    elements.newsList.querySelectorAll('.news-item').forEach(item => {
        item.addEventListener('click', function(e) {
            // 액션 버튼 클릭 시 선택 토글 방지
            if (e.target.closest('.news-item-actions')) {
                e.stopPropagation();
                return;
            }
            
            const url = this.dataset.url;
            toggleNewsSelectionByUrl(url);
        });
        
        // 액션 버튼들의 클릭 이벤트 방지
        item.querySelectorAll('.btn-action').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
            });
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
    // 🚨 자동 복원 방지: 사용자가 직접 선택한 뉴스만 복원
    // 뉴스 추출 후에는 모든 선택 상태가 초기화되어야 함
    
    // 사용자가 명시적으로 선택한 뉴스만 복원 (현재는 안전을 위해 비활성화)
    // elements.newsList.querySelectorAll('.news-item').forEach(item => {
    //     const url = item.dataset.url;
    //     if (selectedNewsUrls.includes(url)) {
    //         item.classList.add('selected');
    //         item.querySelector('.news-checkbox').classList.add('checked');
    //     }
    // });
    
    console.log('🔄 선택 상태 복원 함수 호출됨 (자동 복원 비활성화됨)');
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
        // 🚨 20개 제한 체크 (안정성 우선)
        if (selectedNewsUrls.length >= 20) {
            showToast('⚠️ 최대 20개의 뉴스만 선택할 수 있습니다.', 'warning');
            return;
        }
        
        // 선택
        selectedNewsUrls.push(article.url);
        newsItem.classList.add('selected');
        checkbox.classList.add('checked');
    }
    
    updateSelectedCount();
}

function updateSelectedCount() {
    updateGenerateButtonState();
    updateTabBadge('content-generation', selectedNewsUrls.length);
    updateSelectedNewsSummary();
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
    
    // 🚨 중요: 선택한 뉴스 확정 버튼 상태 관리
    const confirmSelectedNewsBtn = document.getElementById('confirmSelectedNewsBtn');
    if (confirmSelectedNewsBtn) {
        confirmSelectedNewsBtn.disabled = !hasSelected;
        confirmSelectedNewsBtn.innerHTML = hasSelected ? 
            `<i class="fas fa-check"></i> 선택한 뉴스 확정 (${count}개)` : 
            '<i class="fas fa-check"></i> 선택한 뉴스 확정';
    }
    
    // 콘텐츠 생성 탭의 버튼들 상태 업데이트
    const generateSelectedBtn2 = document.getElementById('generateSelectedBtn2');
    if (generateSelectedBtn2) {
        generateSelectedBtn2.disabled = !hasSelected;
        
        // 선택된 콘텐츠 타입에 따라 버튼 텍스트 업데이트
        const selectedType = getSelectedContentType();
        const typeNames = {
            'standard': 'X(Twitter) Normal Form',
            'threads': 'Threads',
            'x': 'X(Twitter) Short Form',
            'enhanced_blog': 'Blog'
        };
        
        const typeName = typeNames[selectedType] || '콘텐츠';
        
        generateSelectedBtn2.innerHTML = hasSelected ? 
            `<i class="fas fa-magic"></i> ${typeName} 생성 (${count}개)` : 
            `<i class="fas fa-magic"></i> ${typeName} 생성`;
    }
    
    // 파일 유형 선택 토글 표시 업데이트
    updateFormatSelectionVisibility();
}

function selectAllNews() {
    // 🚨 모든 뉴스 선택 (백엔드에서 자동으로 100개로 제한됨)
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

async function handleGenerateSelectedEnhancedBlogNews() {
    const selectedFormats = getSelectedFormats();
    console.log('선택된 형식:', selectedFormats);
    await generateSelectedNews('enhanced_blog', selectedFormats);
}

// 새로운 통합 핸들러 함수
async function handleGenerateSelectedNewsWithType() {
    const selectedContentType = getSelectedContentType();
    console.log('선택된 콘텐츠 타입:', selectedContentType);
    
    if (selectedContentType === 'enhanced_blog') {
        const selectedFormats = getSelectedFormats();
        console.log('선택된 형식:', selectedFormats);
        await generateSelectedNews('enhanced_blog', selectedFormats);
    } else {
        await generateSelectedNews(selectedContentType);
    }
}

// 콘텐츠 타입 변경 핸들러
function handleContentTypeChange() {
    const selectedType = getSelectedContentType();
    const wordpressFormatOptions = document.getElementById('wordpressFormatOptions');
    
    if (wordpressFormatOptions) {
        if (selectedType === 'enhanced_blog') {
            // Blog 선택 시 바로 블로그 콘텐츠 파일 형식 옵션 표시
            wordpressFormatOptions.style.display = 'block';
        } else {
            wordpressFormatOptions.style.display = 'none';
        }
    }
    
    // 버튼 텍스트 업데이트
    updateGenerateButtonText();
    
    // 가이드라인 버튼 표시/숨김 및 텍스트 업데이트
    updateGuidelineButton();
}

// 선택된 콘텐츠 타입 가져오기
function getSelectedContentType() {
    const selectedRadio = document.querySelector('input[name="contentType"]:checked');
    return selectedRadio ? selectedRadio.value : 'standard';
}

// 생성 버튼 텍스트 업데이트
function updateGenerateButtonText() {
    const selectedType = getSelectedContentType();
    const generateBtn = document.getElementById('generateSelectedBtn2');
    
    if (generateBtn) {
        const typeNames = {
            'standard': 'X(Twitter) Normal Form',
            'threads': 'Threads',
            'x': 'X(Twitter) Short Form',
            'enhanced_blog': 'Blog'
        };
        
        const typeName = typeNames[selectedType] || '콘텐츠';
        generateBtn.innerHTML = `<i class="fas fa-magic"></i> ${typeName} 생성`;
    }
}

// 선택한 뉴스 확정 및 콘텐츠 생성 탭으로 이동
function handleConfirmSelectedNews() {
    if (selectedNewsUrls.length === 0) {
        showToast('선택된 뉴스가 없습니다.', 'warning');
        return;
    }
    
    // 콘텐츠 생성 탭으로 전환
    switchTab('content-generation');
    showToast(`${selectedNewsUrls.length}개의 뉴스가 선택되었습니다.`, 'success');
}

async function generateSelectedNews(contentType = 'standard', selectedFormats = null) {
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
        
        // 🆕 새로운 배치 생성 시작 - 기존 결과 초기화
        sessionContent = []; // 기존 세션 콘텐츠 모두 초기화
        updateGeneratedContentBadge(); // 배지 0으로 업데이트
        console.log('🧹 새로운 배치 생성 시작 - 기존 콘텐츠 결과 초기화 완료');
        
        // 콘텐츠 타입에 따른 진행률 표시
        const progressTitle = document.getElementById('progressTitle');
        const progressSubtitle = document.getElementById('progressSubtitle');
        
        if (progressTitle) {
            if (contentType === 'blog') {
                progressTitle.textContent = '블로그 콘텐츠 일괄 생성 중...';
            } else if (contentType === 'enhanced_blog') {
                progressTitle.textContent = 'Blog 콘텐츠 일괄 생성 중...';
            } else {
                progressTitle.textContent = '일괄 콘텐츠 생성 중...';
            }
        }
        
        if (progressSubtitle) {
            progressSubtitle.textContent = `${selectedNewsUrls.length}개 뉴스 처리 중 (병렬 처리로 최적화)`;
        }
        
        // 더 정확한 시간 예상 (병렬 처리 고려) - 타임아웃 2배 증가
        let estimatedTimePerBatch = 30; // 기본값
        let timeoutDuration = 480000; // 8분 기본 타임아웃 (2배 증가)
        
        if (contentType === 'enhanced_blog') {
            estimatedTimePerBatch = 60; // Blog는 더 오래 걸림
            timeoutDuration = 1200000; // 20분 타임아웃 (2배 증가)
        }
        
        const totalItems = selectedNewsUrls.length;
        const batchSize = Math.min(8, totalItems); // 최대 8개 병렬 처리 (성능 최적화)
        const estimatedBatches = Math.ceil(totalItems / batchSize);
        const estimatedTime = estimatedBatches * estimatedTimePerBatch * 1000; // ms로 변환
        
        startProgressSimulation(estimatedTime);
        
        // 진행률 업데이트를 위한 시작 시간 기록
        const startTime = Date.now();
        
        // 🚀 개선된 fetch 요청 (타임아웃 포함)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeoutDuration);
        
        try {
            // 워드프레스 형식 정보 추가
            let requestBody = {
                urls: selectedNewsUrls,
                api_provider: apiSettings.provider,
                api_key: apiSettings.key,
                content_type: contentType
            };
            
            // Blog인 경우
            if (contentType === 'enhanced_blog' && selectedFormats) {
                requestBody.selected_formats = selectedFormats;
                
                // 워드프레스가 선택된 경우 형식 정보 추가
                if (selectedFormats.includes('wordpress')) {
                    const wordpressFormat = document.querySelector('input[name="wordpressFormat"]:checked')?.value || 'text';
                    requestBody.wordpress_type = wordpressFormat;
                }
            }
            
            const response = await fetch(`${API_BASE_URL}/api/batch-generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                const errorText = await response.text();
                let errorMessage = `서버 오류 (${response.status})`;
                
                try {
                    const errorData = JSON.parse(errorText);
                    errorMessage = errorData.error || errorMessage;
                } catch (e) {
                    errorMessage = errorText || errorMessage;
                }
                
                throw new Error(errorMessage);
            }
            
            const result = await response.json();
            
            if (result.success && result.data && result.data.results) {
                // 실제 처리 시간 계산
                const processingTime = (Date.now() - startTime) / 1000;
                
                // 진행률 완료
                completeProgress();
                currentBatchData = result.data;
                
                // 성공한 결과만 세션 콘텐츠에 추가
                const successfulResults = result.data.results.filter(item => item.success);
                successfulResults.forEach(item => {
                    sessionContent.push({
                        id: `content_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                        content: item.content,
                        title: item.title || 'Generated Content',
                        created_at: new Date().toISOString(),
                        source_url: item.url || 'Unknown',
                        content_type: contentType,
                        processing_time: processingTime
                    });
                });
                
                // 배지 업데이트
                updateGeneratedContentBadge();
                
                // 성능 통계 표시
                const successCount = successfulResults.length;
                const totalCount = result.data.total_count || result.data.results.length;
                const avgTimePerItem = (processingTime / totalCount).toFixed(1);
                
                setTimeout(() => {
                    // 생성된 콘텐츠 탭으로 자동 전환
                    switchTab('generated-content');
                    
                                    const contentTypeName = contentType === 'enhanced_blog' ? 'Blog ' : '';
                    const performanceInfo = `(평균 ${avgTimePerItem}초/개, 총 ${processingTime.toFixed(1)}초)`;
                    
                    // 🎯 병렬처리 통계 표시
                    let parallelInfo = '';
                    if (result.data.parallel_stats) {
                        const stats = result.data.parallel_stats;
                        parallelInfo = ` | 병렬처리: ${stats.max_workers}개 스레드, 효율성: ${stats.parallel_efficiency}, 속도 향상: ${stats.speedup_factor}`;
                    }
                    
                    showToast(
                        `🚀 병렬 일괄 ${contentTypeName}콘텐츠 생성 완료! 성공: ${successCount}/${totalCount} ${performanceInfo}${parallelInfo}`, 
                        'success'
                    );
                }, 500);
            } else {
                throw new Error(result.error || '서버에서 올바른 응답을 받지 못했습니다.');
            }
            
        } catch (fetchError) {
            clearTimeout(timeoutId);
            
            if (fetchError.name === 'AbortError') {
                const timeoutMinutes = Math.floor(timeoutDuration / 60000);
                throw new Error(`요청 시간이 초과되었습니다 (${timeoutMinutes}분). 선택한 뉴스 개수를 줄이거나 다시 시도해주세요.`);
            } else if (fetchError.message.includes('Failed to fetch')) {
                throw new Error('네트워크 연결에 문제가 있습니다. 인터넷 연결을 확인하고 다시 시도해주세요.');
            } else {
                throw fetchError;
            }
        }
        
    } catch (error) {
        console.error('일괄 생성 오류:', error);
        stopProgressSimulation();
        
        // 🚀 개선된 에러 메시지
        let userFriendlyMessage = error.message;
        
        if (error.message.includes('timeout') || error.message.includes('초과')) {
            userFriendlyMessage = `⏱️ 처리 시간 초과: 선택한 뉴스가 너무 많거나 서버가 바쁩니다. 뉴스 개수를 줄이고 다시 시도해주세요.`;
        } else if (error.message.includes('Maximum 100 URLs allowed') || error.message.includes('100 URLs')) {
            userFriendlyMessage = `⚠️ 뉴스 개수 제한: 최대 100개의 뉴스만 선택할 수 있습니다. 타임아웃 방지를 위한 제한입니다.`;
        } else if (error.message.includes('INVALID_API_PROVIDER') || error.message.includes('API provider must be')) {
            userFriendlyMessage = `🔑 API 키 미설정: 우측 상단 'API 키 설정' 버튼을 클릭하여 Anthropic 또는 OpenAI API 키를 설정해주세요.`;
        } else if (error.message.includes('network') || error.message.includes('연결')) {
            userFriendlyMessage = `🌐 네트워크 오류: 인터넷 연결을 확인하고 다시 시도해주세요.`;
        } else if (error.message.includes('API')) {
            userFriendlyMessage = `🔑 API 오류: API 키를 확인하고 다시 시도해주세요.`;
        } else if (error.message.includes('500')) {
            userFriendlyMessage = `🔧 서버 오류: 서버에 일시적인 문제가 있습니다. 잠시 후 다시 시도해주세요.`;
        } else if (error.message.includes('400')) {
            userFriendlyMessage = `⚠️ 요청 오류: API 키 설정을 확인하고 다시 시도해주세요.`;
        }
        
        showErrorSectionWithRetry(userFriendlyMessage, () => generateSelectedNews(contentType));
    }
}

// 🚀 재시도 기능이 있는 에러 섹션 표시
function showErrorSectionWithRetry(message, retryCallback) {
    // 콘텐츠 생성 탭으로 전환
    switchTab('content-generation');
    
    hideAllSections();
    if (elements.errorSection) {
        elements.errorSection.style.display = 'block';
    }
    if (elements.errorMessage) {
        elements.errorMessage.textContent = message;
    }
    
    // 재시도 버튼 이벤트 설정
    const retryBtn = document.getElementById('retryBtn');
    if (retryBtn && retryCallback) {
        retryBtn.onclick = () => {
            console.log('🔄 재시도 버튼 클릭됨');
            retryCallback();
        };
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
                // 첫 번째 성공한 콘텐츠를 currentData로 설정
                const firstSuccessContent = result.data.results.find(item => item.success);
                if (firstSuccessContent) {
                    currentData = firstSuccessContent;
                }
                setTimeout(() => {
                    showResultSection();
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
        }
    } catch (error) {
        console.error('일괄 작업 상태 확인 오류:', error);
        showErrorSection('일괄 작업 상태를 확인하는 중 오류가 발생했습니다.');
    }
}

// 복잡한 서버 로드 기능 제거됨 - 현재 세션만 관리

function showSessionContent() {
    console.log('📋 세션 콘텐츠 표시');
    hideAllSections();
    const contentSection = document.getElementById('generatedContentListSection');
    if (contentSection) {
        contentSection.style.display = 'block';
    }
    displaySessionContent();
}

function displaySessionContent() {
    const contentListElement = document.getElementById('generatedContentList');
    if (!contentListElement) {
        console.error('❌ generatedContentList 요소 없음');
        return;
    }
    
    if (sessionContent.length === 0) {
        contentListElement.innerHTML = `
            <div class="empty-content-message">
                <i class="fas fa-file-alt"></i>
                <h3>아직 생성된 콘텐츠가 없습니다</h3>
                <p>뉴스를 추출하고 콘텐츠를 생성해보세요.</p>
            </div>
        `;
        return;
    }
    
    // 최신 순으로 정렬
    const sortedContent = [...sessionContent].sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
    );
    
    contentListElement.innerHTML = sortedContent.map((item, index) => {
        // 콘텐츠 미리보기 (첫 280자, 더 나은 처리)
        const contentPreview = item.content ? 
            item.content.substring(0, 280)
                .replace(/[#*`]/g, '')
                .replace(/\n+/g, ' ')
                .replace(/\s+/g, ' ')
                .trim() + '...' : 
            '콘텐츠 로딩 중...';
        
        // 키워드 추출 (마크다운에서 해시태그 찾기) - 최대 6개
        const keywords = item.content ? 
            [...new Set(item.content.match(/#[가-힣a-zA-Z0-9_]+/g) || [])].slice(0, 6) : [];
        
        return `
            <div class="content-item" data-index="${index}" data-id="${item.id}">
                <div class="content-item-header">
                    <div class="content-item-main">
                        <div class="content-item-title">${item.title}</div>
                        <div class="content-preview-text">
                            ${contentPreview}
                        </div>
                        ${keywords.length > 0 ? `
                            <div class="content-item-keywords">
                                ${keywords.map(keyword => 
                                    `<span class="keyword-tag">${keyword}</span>`
                                ).join('')}
                            </div>
                        ` : ''}
                    </div>
                    <div class="content-item-actions">
                        <button class="content-action-btn preview-btn" onclick="showSimplePreview(${index})" title="미리보기">
                            <i class="fas fa-eye"></i>
                            <span>미리보기</span>
                        </button>
                        <button class="content-action-btn copy-btn" onclick="copyContent('${item.id}')" title="복사">
                            <i class="fas fa-copy"></i>
                            <span>복사</span>
                        </button>
                        <button class="content-action-btn download-btn" onclick="downloadContent('${item.id}')" title="다운로드">
                            <i class="fas fa-download"></i>
                            <span>다운로드</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// 콘텐츠 미리보기 모달 함수들
async function showContentPreviewModal(item, index) {
    console.log('🔍 콘텐츠 미리보기 모달 열기:', item);
    
    const modal = document.getElementById('contentPreviewModalSection');
    if (!modal) {
        console.error('❌ 콘텐츠 미리보기 모달을 찾을 수 없음');
        // HTML에 모달이 있는지 확인
        const allModals = document.querySelectorAll('[id*="modal"]');
        console.log('🔍 찾은 모달들:', Array.from(allModals).map(m => m.id));
        return;
    }
    
    console.log('✅ 모달 요소 찾음:', modal);
    
    // 모달 제목 설정
    const modalTitle = document.getElementById('contentPreviewModalTitle');
    if (modalTitle) {
        modalTitle.innerHTML = '<i class="fas fa-eye"></i> 콘텐츠 미리보기';
    }
    
    // 파일 정보 설정
    const filenameElement = document.getElementById('previewFilename');
    const sizeElement = document.getElementById('previewSize');
    const dateElement = document.getElementById('previewDate');
    
    if (filenameElement) {
        filenameElement.textContent = item.filename || '알 수 없음';
    }
    
    if (sizeElement) {
        const fileSize = item.size ? `${(item.size / 1024).toFixed(1)}KB` : '알 수 없음';
        sizeElement.textContent = fileSize;
    }
    
    if (dateElement) {
        const createdDate = item.created_at ? new Date(item.created_at).toLocaleString('ko-KR') : '알 수 없음';
        dateElement.textContent = createdDate;
    }
    
    // 로딩 상태 표시
    showPreviewLoading();
    
    // 모달 표시
    console.log('🎭 모달 표시 중...');
    modal.style.display = 'block';
    console.log('✅ 모달 display 설정 완료:', modal.style.display);
    
    // 콘텐츠 로드
    console.log('📄 콘텐츠 로드 시작...');
    await loadContentPreviewInModal(item, index);
    
    // 이벤트 리스너 설정
    setupContentPreviewModalEvents(item, index);
    console.log('🎉 모달 설정 완료!');
}

function hideContentPreviewModal() {
    console.log('🚪 모달 닫기 시도...');
    const modal = document.getElementById('contentPreviewModalSection');
    if (modal) {
        modal.style.display = 'none';
        console.log('✅ 모달 숨김 완료');
    } else {
        console.log('❌ 모달 요소를 찾을 수 없음');
    }
    
    // 콘텐츠 초기화
    const previewBody = document.getElementById('previewContentBody');
    if (previewBody) {
        previewBody.innerHTML = '';
        previewBody.style.display = 'none';
    }
    
    // 로딩/에러 상태 초기화
    const loadingElement = document.getElementById('previewLoading');
    const errorElement = document.getElementById('previewError');
    if (loadingElement) loadingElement.style.display = 'none';
    if (errorElement) errorElement.style.display = 'none';
    
    console.log('🧹 모달 정리 완료');
}

function showPreviewLoading() {
    const loadingElement = document.getElementById('previewLoading');
    const contentElement = document.getElementById('previewContentBody');
    const errorElement = document.getElementById('previewError');
    
    if (loadingElement) loadingElement.style.display = 'flex';
    if (contentElement) contentElement.style.display = 'none';
    if (errorElement) errorElement.style.display = 'none';
}

function showPreviewError() {
    const loadingElement = document.getElementById('previewLoading');
    const contentElement = document.getElementById('previewContentBody');
    const errorElement = document.getElementById('previewError');
    
    if (loadingElement) loadingElement.style.display = 'none';
    if (contentElement) contentElement.style.display = 'none';
    if (errorElement) errorElement.style.display = 'flex';
}

function showPreviewContent() {
    const loadingElement = document.getElementById('previewLoading');
    const contentElement = document.getElementById('previewContentBody');
    const errorElement = document.getElementById('previewError');
    
    if (loadingElement) loadingElement.style.display = 'none';
    if (contentElement) contentElement.style.display = 'block';
    if (errorElement) errorElement.style.display = 'none';
}

async function loadContentPreviewInModal(item, index) {
    console.log('📄 모달에서 콘텐츠 로드:', item);
    
    try {
        let content = item.content;
        
        // 콘텐츠가 캐시되지 않았다면 API에서 가져오기
        if (!content) {
            const response = await fetch(`${API_BASE_URL}${item.url}`);
            const result = await response.json();
            
            if (result.success && result.data.content) {
                content = result.data.content;
                item.content = content; // 캐시에 저장
            } else {
                throw new Error('Invalid response format');
            }
        }
        
                 // 콘텐츠 렌더링
         const previewBody = document.getElementById('previewContentBody');
         if (previewBody) {
             // 마크다운 렌더링 (marked.js가 로드되어 있다면)
             if (typeof marked !== 'undefined') {
                 previewBody.innerHTML = marked.parse(content);
             } else {
                 // 마크다운 라이브러리가 없으면 간단한 마크다운 처리
                 previewBody.innerHTML = parseSimpleMarkdown(content);
             }
         }
        
        showPreviewContent();
        
    } catch (error) {
        console.error('❌ 콘텐츠 로드 실패:', error);
        showPreviewError();
    }
}

function setupContentPreviewModalEvents(item, index) {
    console.log('🔧 모달 이벤트 설정 중...');
    
    // 모달 닫기 이벤트
    const closeButtons = [
        document.getElementById('closeContentPreviewModalBtn'),
        document.getElementById('closePreviewModalBtn')
    ];
    
    closeButtons.forEach((btn, i) => {
        if (btn) {
            console.log(`✅ 닫기 버튼 ${i+1} 이벤트 설정`);
            btn.onclick = hideContentPreviewModal;
        } else {
            console.log(`❌ 닫기 버튼 ${i+1} 없음`);
        }
    });
    
    // 모달 오버레이 클릭 시 닫기
    const overlay = document.getElementById('contentPreviewModalOverlay');
    if (overlay) {
        console.log('✅ 오버레이 클릭 이벤트 설정');
        overlay.onclick = (e) => {
            if (e.target === overlay) {
                hideContentPreviewModal();
            }
        };
    } else {
        console.log('❌ 오버레이 요소 없음');
    }
    
    // 복사 버튼 이벤트
    const copyBtn = document.getElementById('copyPreviewContentBtn');
    if (copyBtn) {
        console.log('✅ 복사 버튼 이벤트 설정');
        copyBtn.onclick = async () => {
            try {
                let content = item.content;
                
                if (!content) {
                    const response = await fetch(`${API_BASE_URL}${item.url}`);
                    const result = await response.json();
                    
                    if (result.success && result.data.content) {
                        content = result.data.content;
                        item.content = content;
                    } else {
                        throw new Error('Invalid response format');
                    }
                }
                
                await navigator.clipboard.writeText(content);
                showToast('클립보드에 복사되었습니다.', 'success');
                
            } catch (error) {
                console.error('❌ 복사 실패:', error);
                showToast('복사 중 오류가 발생했습니다.', 'error');
            }
        };
    } else {
        console.log('❌ 복사 버튼 없음');
    }
    
    // 다운로드 버튼 이벤트
    const downloadBtn = document.getElementById('downloadPreviewContentBtn');
    if (downloadBtn) {
        console.log('✅ 다운로드 버튼 이벤트 설정');
        downloadBtn.onclick = () => {
            downloadGeneratedContent(index);
        };
    } else {
        console.log('❌ 다운로드 버튼 없음');
    }
    
    // ESC 키로 모달 닫기 (중복 방지)
    if (!window.contentPreviewEscListener) {
        console.log('✅ ESC 키 이벤트 설정');
        window.contentPreviewEscListener = function(e) {
            if (e.key === 'Escape') {
                const modal = document.getElementById('contentPreviewModalSection');
                if (modal && modal.style.display === 'block') {
                    hideContentPreviewModal();
                }
            }
        };
        document.addEventListener('keydown', window.contentPreviewEscListener);
    }
}

// 간단한 마크다운 파서 (marked.js가 없을 때 사용)
function parseSimpleMarkdown(content) {
    if (!content) return '';
    
    // HTML 특수 문자 이스케이프
    let html = content
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    
    // 헤더 처리 (# ## ###)
    html = html.replace(/^### (.*$)/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gm, '<h1>$1</h1>');
    
    // 굵은 글씨 처리 (**text** 또는 __text__)
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__(.*?)__/g, '<strong>$1</strong>');
    
    // 기울임 처리 (*text* 또는 _text_)
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    html = html.replace(/_(.*?)_/g, '<em>$1</em>');
    
    // 인라인 코드 처리 (`code`)
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // 코드 블록 처리 (``` 또는 단순 들여쓰기)
    html = html.replace(/```([^`]+)```/g, '<pre><code>$1</code></pre>');
    
    // 링크 처리 [text](url)
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    
    // 줄바꿈 처리 (두 개의 개행을 문단으로)
    const paragraphs = html.split(/\n\s*\n/);
    html = paragraphs.map(p => {
        p = p.trim();
        if (p === '') return '';
        
        // 헤더가 아닌 경우에만 p 태그로 감싸기
        if (!p.match(/^<h[1-6]>/) && !p.match(/^<pre>/) && !p.match(/^<ul>/) && !p.match(/^<ol>/)) {
            // 단순한 줄바꿈을 br 태그로 변환
            p = p.replace(/\n/g, '<br>');
            return `<p>${p}</p>`;
        }
        
        return p;
    }).join('\n');
    
    // 목록 처리 (- 또는 * 또는 +)
    html = html.replace(/^[\-\*\+] (.*)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    // 번호 목록 처리 (1. 2. 3.)
    html = html.replace(/^\d+\. (.*)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ol>$1</ol>');
    
    // 인용 처리 (> text)
    html = html.replace(/^> (.*)$/gm, '<blockquote>$1</blockquote>');
    
    // 수평선 처리 (---)
    html = html.replace(/^---$/gm, '<hr>');
    
    return html;
}

// 주석 처리된 코드와 테스트 함수들 정리 완료

async function copyGeneratedContent(index) {
    const item = generatedContentData[index];
    if (!item) return;
    
    try {
        let content = item.content;
        
        // 콘텐츠가 캐시되지 않았다면 API에서 가져오기
        if (!content) {
            const response = await fetch(`${API_BASE_URL}${item.url}`);
            const result = await response.json();
            
            if (result.success && result.data.content) {
                content = result.data.content;
                item.content = content; // 캐시에 저장
            } else {
                throw new Error('Invalid response format');
            }
        }
        
        await navigator.clipboard.writeText(content);
        showToast('클립보드에 복사되었습니다.', 'success');
    } catch (error) {
        console.error('복사 오류:', error);
        showToast('복사 중 오류가 발생했습니다.', 'error');
    }
}

async function downloadGeneratedContent(index) {
    const item = generatedContentData[index];
    if (!item) return;
    
    try {
        let content = item.content;
        
        // 콘텐츠가 캐시되지 않았다면 API에서 가져오기
        if (!content) {
            const response = await fetch(`${API_BASE_URL}${item.url}`);
            const result = await response.json();
            
            if (result.success && result.data.content) {
                content = result.data.content;
                item.content = content; // 캐시에 저장
            } else {
                throw new Error('Invalid response format');
            }
        }
        
        const blob = new Blob([content], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = item.filename || `content-${index + 1}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showToast('다운로드가 시작되었습니다.', 'success');
    } catch (error) {
        console.error('다운로드 오류:', error);
        showToast('다운로드 중 오류가 발생했습니다.', 'error');
    }
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



function resetAllFeatures() {
    // 🎯 모든 상태 및 세션 초기화
    currentJobId = null;
    currentData = null;
    currentBatchJobId = null;
    currentBatchData = null;
    extractedNews = [];
    selectedNewsUrls = [];
    sessionContent = []; // 세션 콘텐츠 초기화
    
    // 모든 섹션 숨기기 (이미 메인 뉴스 추출 섹션 표시됨)
    hideAllSections();
    
    // URL 입력 필드 초기화
    const urlInputs = document.querySelectorAll('input[name="urlInput[]"]');
    urlInputs.forEach(input => input.value = '');
    
    // 추가 URL 입력 필드 제거
    const additionalRows = document.querySelectorAll('.url-input-row:not(:first-child)');
    additionalRows.forEach(row => row.remove());
    
    // 뉴스 추출 입력 필드 초기화
    if (elements.newsCount) elements.newsCount.value = '10';
    
    // 메인 뉴스 추출 섹션 확실히 표시
    showNewsExtractorSection();
    
    // 모든 배지 초기화
    updateTabBadge('news-extraction', 0);
    updateTabBadge('content-generation', 0);
    updateTabBadge('generated-content', 0);
    
    // 첫 번째 탭으로 전환
    switchTab('news-extraction');
    
    // 저장된 사용자 설정 초기화
    clearUserPreferences();
    
    showToast('모든 기능이 초기화되었습니다. 새로운 세션을 시작합니다.', 'info');
}

function resetGeneratedContent() {
    // 🎯 생성된 콘텐츠만 초기화 (뉴스 추출 탭 기능과 동일)
    console.log('🔄 생성된 콘텐츠 초기화 시작');
    
    // 생성된 콘텐츠 관련 상태 초기화
    currentJobId = null;
    currentData = null;
    currentBatchJobId = null;
    currentBatchData = null;
    sessionContent = []; // 세션 콘텐츠 초기화
    
    // 생성된 콘텐츠 배지 초기화
    updateTabBadge('generated-content', 0);
    
    // 생성된 콘텐츠 목록 초기화
    updateGeneratedContentBadge();
    
    // 뉴스 추출 탭으로 이동 (뉴스 추출 탭 초기화 기능과 동일)
    switchTab('news-extraction');
    
    // 뉴스 추출 섹션 표시
    showNewsExtractorSection();
    
    console.log('✅ 생성된 콘텐츠 초기화 완료 - 뉴스 추출 탭으로 이동');
    showToast('생성된 콘텐츠가 초기화되었습니다. 뉴스 추출 탭으로 이동합니다.', 'info');
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
    const newsSelectionSection = document.getElementById('newsSelectionSection');
    const generatedContentListSection = document.getElementById('generatedContentListSection');
    const apiSettingsSection = document.getElementById('apiSettingsModalSection');
    
    if (apiSettingsSection && apiSettingsSection.style.display !== 'none') {
        hideApiSettingsModal();
    // urlInputSection 제거됨
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
        // 🚨 자동 복원 방지: selectedNewsUrls 저장 제거
        // selectedNewsUrls: selectedNewsUrls,
        newsSort: document.getElementById('newsSortSelect')?.value || 'newest',
        lastKeyword: '', // 키워드 입력 창이 제거되어 빈 문자열로 고정
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
        
        // 키워드 입력 창이 제거되어 해당 코드 삭제
        
        if (preferences.lastCount) {
            const countInput = document.getElementById('newsCount');
            if (countInput) {
                countInput.value = preferences.lastCount;
            }
        }
        
        // 🚨 자동 복원 방지: 선택된 뉴스 URL은 사용자가 직접 선택해야 함
        // 뉴스 추출 후에는 항상 빈 상태에서 시작해야 함
        // if (preferences.selectedNewsUrls && Array.isArray(preferences.selectedNewsUrls)) {
        //     selectedNewsUrls = preferences.selectedNewsUrls;
        // }
        
        console.log('🔄 사용자 설정 로드 완료 (뉴스 선택 자동 복원 비활성화됨)');
        
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
        // 계층적 구조 정보 로드
        const structuredResponse = await fetch(`${API_BASE_URL}/api/sources/structured`);
        const structuredResult = await structuredResponse.json();
        
        if (structuredResult.success) {
            // 전역 변수에 저장
            availableSources = structuredResult.data.extractable_sources;
            parentSources = structuredResult.data.parent_sources;
            standaloneSources = structuredResult.data.standalone_sources;
            
            // 🚀 선택된 출처 ID 유효성 검증 및 동기화
            const validSelectedIds = selectedSourceIds.filter(id => 
                availableSources.some(source => source.id === id)
            );
            
            // 유효하지 않은 ID가 있으면 활성화된 출처로 초기화
            if (validSelectedIds.length === 0 || validSelectedIds.length !== selectedSourceIds.length) {
                selectedSourceIds = availableSources
                    .filter(source => source.active)
                    .map(source => source.id);
                
                if (validSelectedIds.length !== selectedSourceIds.length) {
                    console.log('🔄 유효하지 않은 출처 ID 감지, 자동 동기화 완료');
                }
            } else {
                selectedSourceIds = validSelectedIds;
            }
            
            updateSelectedSourcesDisplay();
            console.log(`${availableSources.length}개의 추출 가능한 출처를 로드했습니다.`);
            console.log(`부모 출처: ${parentSources.length}개, 독립 출처: ${standaloneSources.length}개`);
        } else {
            throw new Error(structuredResult.error);
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
                description: 'Yahoo Finance 최신 뉴스',
                parent_id: 'yahoo_finance_main',
                parent_name: 'Yahoo Finance'
            },
            {
                id: 'yahoo_finance_crypto',
                name: 'Crypto',
                full_url: 'https://finance.yahoo.com/topic/crypto/',
                active: true,
                description: 'Yahoo Finance 암호화폐 뉴스',
                parent_id: 'yahoo_finance_main',
                parent_name: 'Yahoo Finance'
            },
            {
                id: 'yahoo_finance_tech',
                name: 'Tech',
                full_url: 'https://finance.yahoo.com/topic/tech/',
                active: true,
                description: 'Yahoo Finance 기술 뉴스',
                parent_id: 'yahoo_finance_main',
                parent_name: 'Yahoo Finance'
            }
        ];
        
        parentSources = [
            {
                id: 'yahoo_finance_main',
                name: 'Yahoo Finance',
                url: 'https://finance.yahoo.com/',
                is_parent: true,
                active: true,
                description: 'Yahoo Finance 메인 사이트',
                subcategories: availableSources
            }
        ];
        
        standaloneSources = [];
        selectedSourceIds = ['yahoo_finance_latest'];
        updateSelectedSourcesDisplay();
    }
}

function updateSelectedSourcesDisplay() {
    if (!elements.selectedSources) return;
    
    // 🚀 선택된 출처 ID 유효성 재검증
    const validSelectedIds = selectedSourceIds.filter(id => 
        availableSources.some(source => source.id === id)
    );
    
    if (validSelectedIds.length !== selectedSourceIds.length) {
        selectedSourceIds = validSelectedIds;
        console.log('🔄 유효하지 않은 출처 ID 자동 제거됨');
    }
    
    if (selectedSourceIds.length === 0) {
        elements.selectedSources.innerHTML = '<span class="loading">출처를 선택해주세요</span>';
        return;
    }
    
    const selectedSources = availableSources.filter(source => 
        selectedSourceIds.includes(source.id)
    );
    
    // 부모 출처별로 그룹화
    const parentGroups = {};
    selectedSources.forEach(source => {
        const parentName = source.parent_name || source.name;
        if (!parentGroups[parentName]) {
            parentGroups[parentName] = [];
        }
        parentGroups[parentName].push(source);
    });
    
    // 계층적 구조로 표시
    const displayHtml = Object.entries(parentGroups).map(([parentName, sources]) => {
        if (sources.length === 1 && !sources[0].parent_name) {
            // 단독 출처인 경우
            return `
                <span class="source-tag">
                    ${sources[0].name}
                    <span class="remove" onclick="removeSelectedSource('${sources[0].id}')">×</span>
                </span>
            `;
        } else {
            // 부모-서브카테고리 구조인 경우
            const subcategories = sources.map(source => `
                <span class="subcategory-tag">
                    ${source.name}
                    <span class="remove" onclick="removeSelectedSource('${source.id}')">×</span>
                </span>
            `).join('');
            
            return `
                <div class="parent-source-group">
                    <span class="parent-source-name">@${parentName}</span>
                    <div class="subcategories">${subcategories}</div>
                </div>
            `;
        }
    }).join('');
    
    elements.selectedSources.innerHTML = displayHtml;
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
                                <option value="naver_news" ${subcategory.parser_type === 'naver_news' ? 'selected' : ''}>Naver News</option>
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
            
            // 🚀 출처 데이터 완전 동기화
            await loadAvailableSources();
            displaySourcesList();
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
    
    // 부모 출처 여부 확인
    const isParent = elements.sourceIsParentCheckbox?.checked === true;
    
    // 폼 데이터 수집
    const formData = {
        name: elements.sourceNameInput?.value.trim(),
        url: elements.sourceUrlInput?.value.trim(),
        description: elements.sourceDescriptionInput?.value.trim(),
        active: elements.sourceActiveCheckbox?.checked !== false,
        is_parent: isParent
    };
    
    // 부모 출처가 아닌 경우 파서 타입 추가
    if (!isParent) {
        formData.parser_type = elements.sourceParserTypeSelect?.value || 'yahoo_finance';
    }
    
    // 부모 출처인 경우 서브카테고리 데이터 추가
    if (isParent) {
        const subcategories = getSubcategoriesData();
        if (subcategories.length === 0) {
            showToast('부모 출처는 최소 하나의 서브카테고리가 필요합니다.', 'error');
            return;
        }
        formData.subcategories = subcategories;
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
    
    // 서브카테고리 유효성 검증
    if (isParent && formData.subcategories) {
        for (const subcategory of formData.subcategories) {
            if (!subcategory.name) {
                showToast('모든 서브카테고리에 이름을 입력해주세요.', 'error');
                return;
            }
            if (!subcategory.url) {
                showToast('모든 서브카테고리에 URL 경로를 입력해주세요.', 'error');
                return;
            }
        }
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
        // 독립 출처의 경우 임시로 선택된 것으로 처리 (확정은 confirmSourceSelection에서)
        tempSelectedSubcategories = [currentSelectedParentSource.id];
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
        selectedSourceIds = [...tempSelectedSubcategories];
    } else {
        selectedSourceIds = [currentSelectedParentSource.id];
    }
    
    // 모달 닫기 및 메인 화면 업데이트
    hideSourceSelectionModal();
    updateSelectedSourcesDisplay();
    saveUserPreferences();
    
    showToast(`${selectedSourceIds.length}개 출처가 선택되었습니다.`, 'success');
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
                        <option value="naver_news">Naver News</option>
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

// ============================================================================
// 부모 출처 관리 함수들
// ============================================================================

let currentEditingParentSource = null;
let currentEditingSubcategory = null;
let currentParentSourceForSubcategories = null;

function showParentSourceManagementModal() {
    hideAllSections();
    if (elements.sourceManagementSection) {
        elements.sourceManagementSection.style.display = 'block';
        displayParentSourcesList();
    }
}

function hideParentSourceManagementModal() {
    if (elements.sourceManagementSection) {
        elements.sourceManagementSection.style.display = 'none';
    }
    hideSubcategoryManagementModal();
    showNewsExtractorSection();
}

function displayParentSourcesList() {
    const parentSourcesList = document.getElementById('parentSourcesList');
    if (!parentSourcesList) return;
    
    if (!parentSources || parentSources.length === 0) {
        parentSourcesList.innerHTML = `
            <div class="no-sources">
                <i class="fas fa-sitemap"></i>
                <h4>등록된 부모 출처가 없습니다</h4>
                <p>새 부모 출처를 추가하여 체계적인 뉴스 관리를 시작해보세요.</p>
            </div>
        `;
        return;
    }
    
    parentSourcesList.innerHTML = '';
    
    parentSources.forEach(source => {
        const subcategoryCount = source.subcategories ? source.subcategories.length : 0;
        const activeSubcategoryCount = source.subcategories ? 
            source.subcategories.filter(sub => sub.active).length : 0;
        
        const sourceElement = document.createElement('div');
        sourceElement.className = `source-item ${source.active ? 'active' : 'inactive'}`;
        
        sourceElement.innerHTML = `
            <div class="source-header">
                <div class="source-info">
                    <div class="source-name">
                        <i class="fas fa-sitemap"></i>
                        ${source.name}
                        <span class="parent-badge">부모 출처</span>
                    </div>
                    <div class="source-meta">
                        <div class="source-url">${source.url}</div>
                        <span class="source-status ${source.active ? 'active' : 'inactive'}">
                            ${source.active ? '활성' : '비활성'}
                        </span>
                        <span class="subcategory-count">
                            <i class="fas fa-tags"></i>
                            ${activeSubcategoryCount}/${subcategoryCount} 카테고리 활성
                        </span>
                    </div>
                    ${source.description ? `<div class="source-description">${source.description}</div>` : ''}
                </div>
                <div class="source-actions">
                    <button type="button" class="btn btn-info" onclick="showSubcategoryManagementModal('${source.id}')">
                        <i class="fas fa-tags"></i>
                        카테고리 관리
                    </button>
                    <button type="button" class="btn btn-primary" onclick="editParentSource('${source.id}')">
                        <i class="fas fa-edit"></i>
                        수정
                    </button>
                    <button type="button" class="btn btn-danger" onclick="deleteParentSource('${source.id}')">
                        <i class="fas fa-trash"></i>
                        삭제
                    </button>
                </div>
            </div>
        `;
        
        parentSourcesList.appendChild(sourceElement);
    });
}

// ============================================================================
// 부모 출처 추가/수정 모달 함수들
// ============================================================================

function showAddParentSourceModal() {
    currentEditingParentSource = null;
    
    const modalTitle = document.getElementById('parentSourceModalTitle');
    if (modalTitle) {
        modalTitle.innerHTML = '<i class="fas fa-plus"></i> 새 부모 출처 추가';
    }
    
    // 폼 초기화
    const form = document.getElementById('parentSourceForm');
    if (form) form.reset();
    
    const activeCheckbox = document.getElementById('parentSourceActiveCheckbox');
    if (activeCheckbox) activeCheckbox.checked = true;
    
    showParentSourceModal();
}

function editParentSource(sourceId) {
    const source = parentSources.find(s => s.id === sourceId);
    if (!source) {
        showToast('부모 출처를 찾을 수 없습니다.', 'error');
        return;
    }
    
    currentEditingParentSource = source;
    
    const modalTitle = document.getElementById('parentSourceModalTitle');
    if (modalTitle) {
        modalTitle.innerHTML = '<i class="fas fa-edit"></i> 부모 출처 수정';
    }
    
    // 폼 초기화
    const form = document.getElementById('parentSourceForm');
    if (form) form.reset();
    
    // 기본 정보 채우기
    const nameInput = document.getElementById('parentSourceNameInput');
    if (nameInput) nameInput.value = source.name || '';
    
    const urlInput = document.getElementById('parentSourceUrlInput');
    if (urlInput) urlInput.value = source.url || '';
    
    const descriptionInput = document.getElementById('parentSourceDescriptionInput');
    if (descriptionInput) descriptionInput.value = source.description || '';
    
    const activeCheckbox = document.getElementById('parentSourceActiveCheckbox');
    if (activeCheckbox) activeCheckbox.checked = source.active !== false;
    
    showParentSourceModal();
}

function showParentSourceModal() {
    const modalSection = document.getElementById('parentSourceModalSection');
    if (modalSection) {
        modalSection.style.display = 'block';
    }
}

function hideParentSourceModal() {
    const modalSection = document.getElementById('parentSourceModalSection');
    if (modalSection) {
        modalSection.style.display = 'none';
    }
}

async function saveParentSource() {
    const nameInput = document.getElementById('parentSourceNameInput');
    const urlInput = document.getElementById('parentSourceUrlInput');
    const descriptionInput = document.getElementById('parentSourceDescriptionInput');
    const activeCheckbox = document.getElementById('parentSourceActiveCheckbox');
    
    if (!nameInput || !urlInput) return;
    
    const formData = {
        name: nameInput.value.trim(),
        url: urlInput.value.trim(),
        description: descriptionInput ? descriptionInput.value.trim() : '',
        active: activeCheckbox ? activeCheckbox.checked : true,
        is_parent: true // 항상 부모 출처
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
        
        if (currentEditingParentSource) {
            // 수정
            response = await fetch(`${API_BASE_URL}/api/sources/${currentEditingParentSource.id}`, {
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
            const action = currentEditingParentSource ? '수정' : '추가';
            showToast(`부모 출처가 성공적으로 ${action}되었습니다.`, 'success');
            
            // 데이터 새로고침 및 UI 업데이트
            await loadAvailableSources();
            displayParentSourcesList();
            hideParentSourceModal();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('부모 출처 저장 오류:', error);
        showToast('부모 출처 저장 중 오류가 발생했습니다.', 'error');
    }
}

async function deleteParentSource(sourceId) {
    const source = parentSources.find(s => s.id === sourceId);
    if (!source) return;
    
    const subcategoryCount = source.subcategories ? source.subcategories.length : 0;
    let confirmMessage = `'${source.name}' 부모 출처를 삭제하시겠습니까?`;
    
    if (subcategoryCount > 0) {
        confirmMessage += `\n\n⚠️ 이 출처에는 ${subcategoryCount}개의 서브카테고리가 있습니다.\n부모 출처를 삭제하면 모든 서브카테고리도 함께 삭제됩니다.`;
    }
    
    if (!confirm(confirmMessage)) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/sources/${sourceId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('부모 출처가 성공적으로 삭제되었습니다.', 'success');
            
            // 🚀 출처 데이터 완전 동기화
            await loadAvailableSources();
            displayParentSourcesList();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('부모 출처 삭제 오류:', error);
        showToast('부모 출처 삭제 중 오류가 발생했습니다.', 'error');
    }
}

// ============================================================================
// 서브카테고리 관리 함수들
// ============================================================================

function showSubcategoryManagementModal(parentSourceId) {
    const parentSource = parentSources.find(s => s.id === parentSourceId);
    if (!parentSource) {
        showToast('부모 출처를 찾을 수 없습니다.', 'error');
        return;
    }
    
    currentParentSourceForSubcategories = parentSource;
    
    // 부모 출처 정보 표시
    const parentSourceInfo = document.getElementById('currentParentSourceInfo');
    if (parentSourceInfo) {
        parentSourceInfo.innerHTML = `
            <div class="parent-source-card">
                <div class="parent-source-header">
                    <h4><i class="fas fa-sitemap"></i> ${parentSource.name}</h4>
                    <span class="source-status ${parentSource.active ? 'active' : 'inactive'}">
                        ${parentSource.active ? '활성' : '비활성'}
                    </span>
                </div>
                <div class="parent-source-url">${parentSource.url}</div>
                ${parentSource.description ? `<div class="parent-source-description">${parentSource.description}</div>` : ''}
            </div>
        `;
    }
    
    // 서브카테고리 관리 모달 표시
    const modalSection = document.getElementById('subcategoryManagementSection');
    if (modalSection) {
        modalSection.style.display = 'block';
    }
    
    displaySubcategoriesList();
}

function hideSubcategoryManagementModal() {
    const modalSection = document.getElementById('subcategoryManagementSection');
    if (modalSection) {
        modalSection.style.display = 'none';
    }
}

function displaySubcategoriesList() {
    const subcategoriesList = document.getElementById('subcategoriesList');
    if (!subcategoriesList || !currentParentSourceForSubcategories) return;
    
    const subcategories = currentParentSourceForSubcategories.subcategories || [];
    
    if (subcategories.length === 0) {
        subcategoriesList.innerHTML = `
            <div class="no-sources">
                <i class="fas fa-tags"></i>
                <h4>등록된 서브카테고리가 없습니다</h4>
                <p>'새 서브카테고리 추가' 버튼을 클릭하여 카테고리를 추가해보세요.</p>
            </div>
        `;
        return;
    }
    
    subcategoriesList.innerHTML = '';
    
    subcategories.forEach(subcategory => {
        const subcategoryElement = document.createElement('div');
        subcategoryElement.className = `source-item ${subcategory.active ? 'active' : 'inactive'}`;
        
        subcategoryElement.innerHTML = `
            <div class="source-header">
                <div class="source-info">
                    <div class="source-name">
                        <i class="fas fa-tag"></i>
                        ${subcategory.name}
                        <span class="subcategory-badge">서브카테고리</span>
                    </div>
                    <div class="source-meta">
                                                 <div class="source-url">${currentParentSourceForSubcategories.url.replace(/\/$/, '')}${subcategory.url}</div>
                        <span class="source-parser">${subcategory.parser_type || 'universal'}</span>
                        <span class="source-status ${subcategory.active ? 'active' : 'inactive'}">
                            ${subcategory.active ? '활성' : '비활성'}
                        </span>
                    </div>
                    ${subcategory.description ? `<div class="source-description">${subcategory.description}</div>` : ''}
                </div>
                <div class="source-actions">
                    <button type="button" class="btn btn-primary" onclick="editSubcategory('${subcategory.id}')">
                        <i class="fas fa-edit"></i>
                        수정
                    </button>
                    <button type="button" class="btn btn-danger" onclick="deleteSubcategory('${subcategory.id}')">
                        <i class="fas fa-trash"></i>
                        삭제
                    </button>
                </div>
            </div>
        `;
        
        subcategoriesList.appendChild(subcategoryElement);
    });
}

// ============================================================================
// 서브카테고리 추가/수정 모달 함수들
// ============================================================================

function showAddSubcategoryModal() {
    if (!currentParentSourceForSubcategories) {
        showToast('부모 출처가 선택되지 않았습니다.', 'error');
        return;
    }
    
    currentEditingSubcategory = null;
    
    const modalTitle = document.getElementById('subcategoryModalTitle');
    if (modalTitle) {
        modalTitle.innerHTML = `<i class="fas fa-plus"></i> 새 서브카테고리 추가 - ${currentParentSourceForSubcategories.name}`;
    }
    
    // 폼 초기화
    const form = document.getElementById('subcategoryForm');
    if (form) form.reset();
    
    const activeCheckbox = document.getElementById('subcategoryActiveCheckbox');
    if (activeCheckbox) activeCheckbox.checked = true;
    
    showSubcategoryModal();
}

function editSubcategory(subcategoryId) {
    if (!currentParentSourceForSubcategories) return;
    
    const subcategory = currentParentSourceForSubcategories.subcategories.find(sub => sub.id === subcategoryId);
    if (!subcategory) {
        showToast('서브카테고리를 찾을 수 없습니다.', 'error');
        return;
    }
    
    currentEditingSubcategory = subcategory;
    
    const modalTitle = document.getElementById('subcategoryModalTitle');
    if (modalTitle) {
        modalTitle.innerHTML = `<i class="fas fa-edit"></i> 서브카테고리 수정 - ${subcategory.name}`;
    }
    
    // 폼 초기화
    const form = document.getElementById('subcategoryForm');
    if (form) form.reset();
    
    // 기본 정보 채우기
    const nameInput = document.getElementById('subcategoryNameInput');
    if (nameInput) nameInput.value = subcategory.name || '';
    
    const urlInput = document.getElementById('subcategoryUrlInput');
    if (urlInput) urlInput.value = subcategory.url || '';
    
    const parserTypeSelect = document.getElementById('subcategoryParserTypeSelect');
    if (parserTypeSelect) parserTypeSelect.value = subcategory.parser_type || 'universal';
    
    const descriptionInput = document.getElementById('subcategoryDescriptionInput');
    if (descriptionInput) descriptionInput.value = subcategory.description || '';
    
    const activeCheckbox = document.getElementById('subcategoryActiveCheckbox');
    if (activeCheckbox) activeCheckbox.checked = subcategory.active !== false;
    
    showSubcategoryModal();
}

function showSubcategoryModal() {
    const modalSection = document.getElementById('subcategoryModalSection');
    if (modalSection) {
        modalSection.style.display = 'block';
    }
}

function hideSubcategoryModal() {
    const modalSection = document.getElementById('subcategoryModalSection');
    if (modalSection) {
        modalSection.style.display = 'none';
    }
}

async function saveSubcategory() {
    if (!currentParentSourceForSubcategories) {
        showToast('부모 출처가 선택되지 않았습니다.', 'error');
        return;
    }
    
    const nameInput = document.getElementById('subcategoryNameInput');
    const urlInput = document.getElementById('subcategoryUrlInput');
    const parserTypeSelect = document.getElementById('subcategoryParserTypeSelect');
    const descriptionInput = document.getElementById('subcategoryDescriptionInput');
    const activeCheckbox = document.getElementById('subcategoryActiveCheckbox');
    
    if (!nameInput || !urlInput) return;
    
    const subcategoryData = {
        name: nameInput.value.trim(),
        url: urlInput.value.trim(),
        parser_type: parserTypeSelect ? parserTypeSelect.value : 'universal',
        description: descriptionInput ? descriptionInput.value.trim() : '',
        active: activeCheckbox ? activeCheckbox.checked : true
    };
    
    // 유효성 검증
    if (!subcategoryData.name) {
        showToast('카테고리명을 입력해주세요.', 'error');
        return;
    }
    
    if (!subcategoryData.url) {
        showToast('URL 경로를 입력해주세요.', 'error');
        return;
    }
    
    try {
        // 기존 서브카테고리들 가져오기
        const existingSubcategories = currentParentSourceForSubcategories.subcategories || [];
        let updatedSubcategories;
        
        if (currentEditingSubcategory) {
            // 수정: 기존 서브카테고리 업데이트
            updatedSubcategories = existingSubcategories.map(sub => 
                sub.id === currentEditingSubcategory.id ? { ...sub, ...subcategoryData } : sub
            );
        } else {
            // 추가: 새 서브카테고리 추가 (고유 ID 생성)
            const newSubcategoryWithId = {
                ...subcategoryData,
                id: `sub_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
            };
            updatedSubcategories = [...existingSubcategories, newSubcategoryWithId];
        }
        
        // 부모 출처 업데이트
        const parentFormData = {
            name: currentParentSourceForSubcategories.name,
            url: currentParentSourceForSubcategories.url,
            description: currentParentSourceForSubcategories.description,
            active: currentParentSourceForSubcategories.active,
            is_parent: true,
            subcategories: updatedSubcategories
        };
        
        const response = await fetch(`${API_BASE_URL}/api/sources/${currentParentSourceForSubcategories.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(parentFormData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            const action = currentEditingSubcategory ? '수정' : '추가';
            showToast(`서브카테고리가 성공적으로 ${action}되었습니다.`, 'success');
            
            // 데이터 새로고침 및 UI 업데이트
            await loadAvailableSources();
            
            // 현재 부모 출처 정보 업데이트
            currentParentSourceForSubcategories = parentSources.find(s => s.id === currentParentSourceForSubcategories.id);
            
            displaySubcategoriesList();
            hideSubcategoryModal();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('서브카테고리 저장 오류:', error);
        showToast('서브카테고리 저장 중 오류가 발생했습니다.', 'error');
    }
}

async function deleteSubcategory(subcategoryId) {
    if (!currentParentSourceForSubcategories) return;
    
    const subcategory = currentParentSourceForSubcategories.subcategories.find(sub => sub.id === subcategoryId);
    if (!subcategory) return;
    
    if (!confirm(`'${subcategory.name}' 서브카테고리를 삭제하시겠습니까?`)) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/sources/${subcategoryId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('서브카테고리가 성공적으로 삭제되었습니다.', 'success');
            
            // 🚀 출처 데이터 완전 동기화
            await loadAvailableSources();
            
            // 현재 부모 출처 정보 업데이트
            currentParentSourceForSubcategories = parentSources.find(s => s.id === currentParentSourceForSubcategories.id);
            
            displaySubcategoriesList();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('서브카테고리 삭제 오류:', error);
        showToast('서브카테고리 삭제 중 오류가 발생했습니다.', 'error');
    }
}

// 🚨 강제 콘텐츠 로드 함수 (복잡한 로직 우회)
// 🎯 현재 세션 콘텐츠 표시 (과거 누적 데이터 없이)
function showCurrentSessionContent() {
    console.log('📋 현재 세션 콘텐츠 표시', { count: currentSessionContent.length });
    
    // 섹션 표시
    hideAllSections();
    const contentSection = document.getElementById('generatedContentListSection');
    if (contentSection) {
        contentSection.style.display = 'block';
    }
    
    // 콘텐츠 표시
    displayCurrentSessionContent();
}

// 현재 세션 콘텐츠 렌더링
function displayCurrentSessionContent() {
    const contentListElement = document.getElementById('generatedContentList');
    if (!contentListElement) {
        console.error('❌ generatedContentList 요소를 찾을 수 없음');
        return;
    }
    
    if (currentSessionContent.length === 0) {
        contentListElement.innerHTML = `
            <div class="empty-content-message">
                <i class="fas fa-file-alt"></i>
                <h3>아직 생성된 콘텐츠가 없습니다</h3>
                <p>뉴스를 추출하고 콘텐츠를 생성해보세요.</p>
            </div>
        `;
        return;
    }
    
    // 최신 순으로 정렬
    const sortedContent = [...currentSessionContent].sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
    );
    
    contentListElement.innerHTML = sortedContent.map((item, index) => {
        // 콘텐츠 미리보기 텍스트 생성 (더 긴 텍스트로 개선)
        let contentPreview = '';
        if (item.content) {
            // 마크다운 기호 제거 및 텍스트 정리
            contentPreview = item.content
                .replace(/[#*`]/g, '')
                .replace(/\n+/g, ' ')
                .replace(/\s+/g, ' ')
                .trim()
                .substring(0, 280) + '...';
        } else {
            contentPreview = '콘텐츠 미리보기를 불러오는 중...';
        }
        
        // 해시태그 추출 (마크다운에서 #태그 찾기)
        const keywords = item.content ? 
            [...new Set(item.content.match(/#[가-힣a-zA-Z0-9_]+/g) || [])].slice(0, 5) : [];
        
        return `
            <div class="content-item">
                <div class="content-item-preview">
                    <p class="content-preview-text">${contentPreview}</p>
                    
                    ${keywords.length > 0 ? `
                        <div class="content-item-keywords">
                            ${keywords.map(keyword => `<span class="keyword-tag">${keyword}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
                
                <div class="content-item-actions">
                    <button class="content-action-btn preview-btn" onclick="showSimplePreview(${index})">
                        <i class="fas fa-eye"></i>
                        <span>미리보기</span>
                    </button>
                    <button class="content-action-btn copy-btn" onclick="copySessionContent(${index})">
                        <i class="fas fa-copy"></i>
                        <span>복사</span>
                    </button>
                    <button class="content-action-btn download-btn" onclick="downloadSessionContent(${index})">
                        <i class="fas fa-download"></i>
                        <span>다운로드</span>
                    </button>
                </div>
            </div>
        `;
    }).join('');
    
    console.log(`✅ 현재 세션 콘텐츠 ${currentSessionContent.length}개 렌더링 완료`);
}

// 세션 콘텐츠 미리보기 토글
// 세션 콘텐츠 토글 함수 삭제됨 - 팝업 모달 방식으로 변경

// 세션 콘텐츠 복사
async function copySessionContent(index) {
    const item = currentSessionContent[index];
    if (!item || !item.content) {
        showToast('복사할 콘텐츠가 없습니다.', 'error');
        return;
    }
    
    try {
        await navigator.clipboard.writeText(item.content);
        showToast('클립보드에 복사되었습니다!', 'success');
    } catch (error) {
        console.error('복사 에러:', error);
        showToast('복사 중 오류가 발생했습니다.', 'error');
    }
}

// 세션 콘텐츠 다운로드
async function downloadSessionContent(index) {
    const item = currentSessionContent[index];
    if (!item || !item.content) {
        showToast('다운로드할 콘텐츠가 없습니다.', 'error');
        return;
    }
    
    try {
        const filename = item.filename || `content_${index + 1}.md`;
        const blob = new Blob([item.content], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
        showToast('다운로드가 완료되었습니다!', 'success');
    } catch (error) {
        console.error('다운로드 에러:', error);
        showToast('다운로드 중 오류가 발생했습니다.', 'error');
    }
}

async function loadGeneratedContentListForced() {
    console.log('🚀 강제 콘텐츠 로드 시작');
    
    try {
        // 직접 API 호출
        const response = await fetch(`${API_BASE_URL}/api/generated-content`);
        const result = await response.json();
        
        console.log('📊 강제 로드 결과:', result);
        
        if (result.success && result.data && result.data.files) {
            const files = result.data.files;
            console.log(`✅ ${files.length}개 파일 로드됨`);
            
            // 직접 HTML 생성
            const contentListElement = document.getElementById('generatedContentList');
            if (contentListElement) {
                if (files.length === 0) {
                    contentListElement.innerHTML = `
                        <div class="empty-content-message">
                            <i class="fas fa-file-alt"></i>
                            <h3>생성된 콘텐츠가 없습니다</h3>
                            <p>뉴스 추출 후 콘텐츠를 생성해보세요.</p>
                        </div>
                    `;
                } else {
                    // 파일을 최신 순으로 정렬
                    files.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
                    
                    // Blog 파일들 그룹핑
                    const { groups, regularFiles } = groupEnhancedBlogFiles(files);
                    
                    // 모든 파일들 (그룹 + 일반 파일) 통합하여 최신 순 정렬
                    const allItems = [
                        ...groups.map(group => ({ ...group, isGroup: true })),
                        ...regularFiles.map(file => ({ ...file, isGroup: false }))
                    ].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
                    
                    contentListElement.innerHTML = allItems.map((item, index) => {
                        if (item.isGroup) {
                            // Blog 그룹 처리
                            const group = item;
                            let contentPreview = '';
                            if (group.content) {
                                contentPreview = group.content
                                    .replace(/[#*`]/g, '')
                                    .replace(/\n+/g, ' ')
                                    .replace(/\s+/g, ' ')
                                    .trim()
                                    .substring(0, 280) + '...';
                            } else {
                                contentPreview = '콘텐츠 미리보기를 불러오는 중...';
                            }
                            
                            const keywords = group.content ? 
                                [...new Set(group.content.match(/#[가-힣a-zA-Z0-9_]+/g) || [])].slice(0, 5) : [];
                                
                            const firstFile = group.files[0];
                            
                            return `
                                <div class="content-item enhanced-blog-group">
                                    <div class="content-item-header">
                                        <span class="enhanced-blog-badge">
                                            <i class="fas fa-star"></i>
                                            Blog
                                        </span>
                                        <span class="file-count">${group.files.length}개 파일</span>
                                    </div>
                                    
                                    ${createFileTypeSelector(group.baseName, group.files)}
                                    
                                    <div class="content-item-preview">
                                        <p class="content-preview-text">${contentPreview}</p>
                                        
                                        ${keywords.length > 0 ? `
                                            <div class="content-item-keywords">
                                                ${keywords.map(keyword => `<span class="keyword-tag">${keyword}</span>`).join('')}
                                            </div>
                                        ` : ''}
                                    </div>
                                    
                                    <div class="content-item-actions">
                                        <button class="content-action-btn preview-btn" onclick="toggleEnhancedBlogPreview('${group.baseName}')">
                                            <i class="fas fa-eye"></i>
                                            <span>미리보기</span>
                                        </button>
                                        <button class="content-action-btn copy-btn" onclick="copyEnhancedBlogContent('${group.baseName}')">
                                            <i class="fas fa-copy"></i>
                                            <span>복사</span>
                                        </button>
                                        <button class="content-action-btn download-btn" onclick="downloadEnhancedBlogContent('${group.baseName}')">
                                            <i class="fas fa-download"></i>
                                            <span>다운로드</span>
                                        </button>
                                    </div>
                                    
                                    <div class="content-preview" id="preview-${group.baseName}" style="display: none;">
                                        <div class="preview-loading">
                                            <i class="fas fa-spinner fa-spin"></i>
                                            <span>콘텐츠 로딩 중...</span>
                                        </div>
                                    </div>
                                </div>
                            `;
                        } else {
                            // 일반 파일 처리
                            let contentPreview = '';
                            if (item.content) {
                                contentPreview = item.content
                                    .replace(/[#*`]/g, '')
                                    .replace(/\n+/g, ' ')
                                    .replace(/\s+/g, ' ')
                                    .trim()
                                    .substring(0, 280) + '...';
                            } else {
                                contentPreview = '콘텐츠 미리보기를 불러오는 중...';
                            }
                            
                            const keywords = item.content ? 
                                [...new Set(item.content.match(/#[가-힣a-zA-Z0-9_]+/g) || [])].slice(0, 5) : [];
                            
                            return `
                                <div class="content-item">
                                    <div class="content-item-preview">
                                        <p class="content-preview-text">${contentPreview}</p>
                                        
                                        ${keywords.length > 0 ? `
                                            <div class="content-item-keywords">
                                                ${keywords.map(keyword => `<span class="keyword-tag">${keyword}</span>`).join('')}
                                            </div>
                                        ` : ''}
                                    </div>
                                    
                                    <div class="content-item-actions">
                                        <button class="content-action-btn preview-btn" onclick="toggleContentPreview('${item.filename}')">
                                            <i class="fas fa-eye"></i>
                                            <span>미리보기</span>
                                        </button>
                                        <button class="content-action-btn copy-btn" onclick="copyContentForced('${item.filename}')">
                                            <i class="fas fa-copy"></i>
                                            <span>복사</span>
                                        </button>
                                        <button class="content-action-btn download-btn" onclick="downloadContentForced('${item.filename}')">
                                            <i class="fas fa-download"></i>
                                            <span>다운로드</span>
                                        </button>
                                    </div>
                                    
                                    <div class="content-preview" id="preview-${item.filename}" style="display: none;">
                                        <div class="preview-loading">
                                            <i class="fas fa-spinner fa-spin"></i>
                                            <span>콘텐츠 로딩 중...</span>
                                        </div>
                                    </div>
                                </div>
                            `;
                        }
                    }).join('');
                }
                console.log('✅ 강제 렌더링 완료');
            } else {
                console.error('❌ generatedContentList 요소를 찾을 수 없음');
            }
            
            // 배지 업데이트
            updateTabBadge('generated-content', files.length);
            
        } else {
            console.error('❌ API 응답 실패:', result);
        }
    } catch (error) {
        console.error('🚨 강제 로드 에러:', error);
    }
}

// 파일명에서 제목 추출하는 헬퍼 함수
function extractTitleFromFilename(filename) {
    // finance_yahoo_com_20250713_221822.md 형태에서 의미있는 제목 추출
    const baseTitle = filename.replace(/\.md$/, '');
    const parts = baseTitle.split('_');
    
    if (parts.length >= 4) {
        const domain = parts.slice(0, 3).join('_');
        const dateTime = parts.slice(3).join('_');
        
        // 도메인 기반 제목 생성
        if (domain === 'finance_yahoo_com') {
            return `Yahoo Finance 뉴스 (${dateTime})`;
        }
    }
    
    // 기본 제목 생성
    return baseTitle.replace(/_/g, ' ').replace(/^\w/, c => c.toUpperCase());
}

// 시간 차이 계산 헬퍼 함수
function getTimeAgo(date) {
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) {
        return '방금 전';
    } else if (diffInSeconds < 3600) {
        return `${Math.floor(diffInSeconds / 60)}분 전`;
    } else if (diffInSeconds < 86400) {
        return `${Math.floor(diffInSeconds / 3600)}시간 전`;
    } else {
        return `${Math.floor(diffInSeconds / 86400)}일 전`;
    }
}

// 뉴스 미리보기 기능
function previewNewsContent(url, title) {
    console.log('📄 뉴스 미리보기:', url, title);
    
    // 간단한 미리보기 모달 생성
    const modal = document.createElement('div');
    modal.className = 'news-preview-modal';
    modal.innerHTML = `
        <div class="modal-overlay">
            <div class="modal-content">
                <div class="modal-header">
                    <h3><i class="fas fa-eye"></i> 뉴스 미리보기</h3>
                    <button class="btn btn-icon" onclick="closeNewsPreview()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="news-preview-info">
                        <h4>${title}</h4>
                        <p class="news-url">${url}</p>
                    </div>
                    <div class="news-preview-actions">
                        <button class="btn btn-primary" onclick="window.open('${url}', '_blank'); closeNewsPreview();">
                            <i class="fas fa-external-link-alt"></i>
                            원본 보기
                        </button>
                        <button class="btn btn-secondary" onclick="closeNewsPreview()">
                            <i class="fas fa-times"></i>
                            닫기
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // 모달 닫기 이벤트
    modal.addEventListener('click', function(e) {
        if (e.target === modal.querySelector('.modal-overlay')) {
            closeNewsPreview();
        }
    });
    
    // ESC 키로 닫기
    const escListener = function(e) {
        if (e.key === 'Escape') {
            closeNewsPreview();
            document.removeEventListener('keydown', escListener);
        }
    };
    document.addEventListener('keydown', escListener);
    
    showToast('뉴스 미리보기를 표시합니다.', 'info');
}

function closeNewsPreview() {
    const modal = document.querySelector('.news-preview-modal');
    if (modal) {
        document.body.removeChild(modal);
    }
}

// 콘텐츠 미리보기 토글 함수
// 토글 함수 삭제됨 - 팝업 모달 방식으로 변경

// 간단한 복사/다운로드 함수
async function copyContentForced(filename) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/generated-content/${filename}`);
        const result = await response.json();
        if (result.success) {
            await navigator.clipboard.writeText(result.data.content);
            showToast('클립보드에 복사되었습니다!', 'success');
        }
    } catch (error) {
        console.error('복사 에러:', error);
        showToast('복사 중 오류가 발생했습니다.', 'error');
    }
}

async function downloadContentForced(filename) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/generated-content/${filename}`);
        const result = await response.json();
        if (result.success) {
            const blob = new Blob([result.data.content], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
            showToast('다운로드가 완료되었습니다!', 'success');
        }
    } catch (error) {
        console.error('다운로드 에러:', error);
        showToast('다운로드 중 오류가 발생했습니다.', 'error');
    }
}



// ============================================================================
// 간단한 세션 콘텐츠 관리 시스템
// ============================================================================

// ============================================================================
// 🚀 새로운 간단한 미리보기 시스템 (제로 베이스)
// ============================================================================

function showSimplePreview(index) {
    console.log('🚀 새로운 미리보기 시작:', index);
    
    // 1. 데이터 검증
    if (!sessionContent || sessionContent.length === 0) {
        console.error('❌ sessionContent가 비어있음');
        alert('표시할 콘텐츠가 없습니다.');
        return;
    }
    
    if (index < 0 || index >= sessionContent.length) {
        console.error('❌ 잘못된 인덱스:', index, '전체 길이:', sessionContent.length);
        alert('콘텐츠를 찾을 수 없습니다.');
        return;
    }
    
    const content = sessionContent[index];
    console.log('📄 미리보기 데이터:', {
        title: content.title,
        content_length: content.content ? content.content.length : 0,
        content_type: content.content_type
    });
    
    // 2. 기존 모달 제거 (중복 방지)
    const existingModal = document.getElementById('simple-preview-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 3. 마크다운을 HTML로 변환
    let htmlContent;
    if (content.content) {
        if (typeof marked !== 'undefined') {
            try {
                htmlContent = marked.parse(content.content);
                console.log('✅ marked.js로 마크다운 변환 완료');
            } catch (error) {
                console.warn('⚠️ marked.js 변환 실패, 기본 처리 사용:', error);
                htmlContent = content.content.replace(/\n/g, '<br>');
            }
        } else {
            // marked.js가 없으면 기본 마크다운 처리
            htmlContent = content.content
                .replace(/^# (.*$)/gim, '<h1>$1</h1>')
                .replace(/^## (.*$)/gim, '<h2>$1</h2>')
                .replace(/^### (.*$)/gim, '<h3>$1</h3>')
                .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
                .replace(/\*(.*)\*/gim, '<em>$1</em>')
                .replace(/\n/g, '<br>');
            console.log('✅ 기본 마크다운 처리 완료');
        }
    } else {
        htmlContent = '<p>콘텐츠가 없습니다.</p>';
    }
    
    // 4. 모달 HTML 생성
    const modalHTML = `
        <div id="simple-preview-modal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            box-sizing: border-box;
        ">
            <div style="
                background: var(--bg-primary);
                border: 1px solid var(--border-color);
                border-radius: 16px;
                max-width: 800px;
                max-height: 90vh;
                width: 100%;
                overflow: hidden;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
                display: flex;
                flex-direction: column;
            ">
                <!-- 헤더 -->
                <div style="
                    padding: 15px 20px;
                    border-bottom: 1px solid #e5e7eb;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background: var(--bg-secondary);
                ">
                    <h3 style="margin: 0; color: var(--text-primary); font-size: 16px; font-weight: 500;">
                        📄 콘텐츠 미리보기
                    </h3>
                    <button onclick="closeSimplePreview()" style="
                        background: none;
                        border: none;
                        font-size: 20px;
                        cursor: pointer;
                        color: var(--text-secondary);
                        padding: 4px;
                        border-radius: 4px;
                        transition: all 0.2s;
                    " onmouseover="this.style.background='var(--bg-hover)'" onmouseout="this.style.background='none'">
                        ×
                    </button>
                </div>
                
                <!-- 콘텐츠 -->
                <div style="
                    padding: 24px;
                    overflow-y: auto;
                    flex: 1;
                    line-height: 1.6;
                    color: var(--text-primary);
                    font-size: 15px;
                ">
                    ${htmlContent}
                </div>
                
                <!-- 하단 버튼 -->
                <div style="
                    padding: 16px 24px;
                    border-top: 1px solid var(--border-color);
                    background: var(--bg-secondary);
                    display: flex;
                    justify-content: flex-end;
                    gap: 12px;
                ">
                    <button onclick="copySimpleContent(${index})" style="
                        background: linear-gradient(135deg, #10b981, #059669);
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 8px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: 500;
                        transition: all 0.2s;
                        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
                        display: flex;
                        align-items: center;
                        gap: 6px;
                    " onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 8px rgba(16, 185, 129, 0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 4px rgba(16, 185, 129, 0.3)'">
                        📋 복사
                    </button>
                    <button onclick="closeSimplePreview()" style="
                        background: var(--bg-hover);
                        color: var(--text-secondary);
                        border: 1px solid var(--border-color);
                        padding: 10px 20px;
                        border-radius: 8px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: 500;
                        transition: all 0.2s;
                        display: flex;
                        align-items: center;
                        gap: 6px;
                    " onmouseover="this.style.background='var(--bg-secondary)'" onmouseout="this.style.background='var(--bg-hover)'">
                        닫기
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // 5. 모달을 body에 추가
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // 6. 오버레이 클릭으로 닫기
    const modal = document.getElementById('simple-preview-modal');
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeSimplePreview();
        }
    });
    
    // 7. ESC 키로 닫기
    const escHandler = function(e) {
        if (e.key === 'Escape') {
            closeSimplePreview();
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
    
    console.log('✅ 새로운 미리보기 모달 표시 완료');
}

function closeSimplePreview() {
    const modal = document.getElementById('simple-preview-modal');
    if (modal) {
        modal.remove();
        console.log('✅ 미리보기 모달 닫기 완료');
    }
}

function copySimpleContent(index) {
    if (index >= 0 && index < sessionContent.length) {
        const content = sessionContent[index];
        if (content.content) {
            navigator.clipboard.writeText(content.content).then(() => {
                alert('클립보드에 복사되었습니다!');
            }).catch(() => {
                alert('복사에 실패했습니다.');
            });
        }
    }
}

// 기존 복잡한 함수는 유지 (호환성을 위해)
function previewSessionContent(index) {
    // 새로운 함수로 리다이렉트
    showSimplePreview(index);
}

// 콘텐츠 미리보기 (ID로 찾기)
function previewContent(contentId) {
    const content = sessionContent.find(item => item.id === contentId);
    if (!content) {
        showToast('콘텐츠를 찾을 수 없습니다.', 'error');
        return;
    }
    
    // 간단한 모달로 미리보기 표시
    const modal = document.createElement('div');
    modal.className = 'content-preview-modal';
    modal.innerHTML = `
        <div class="modal-overlay" onclick="closePreviewModal()"></div>
        <div class="modal-content">
            <div class="modal-header">
                <h3>${content.title}</h3>
                <button onclick="closePreviewModal()" class="btn-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="content-preview">
                    ${typeof marked !== 'undefined' ? marked.parse(content.content) : `<pre>${content.content}</pre>`}
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.style.display = 'flex';
}

function closePreviewModal() {
    const modal = document.querySelector('.content-preview-modal');
    if (modal) {
        modal.remove();
    }
}

// 콘텐츠 복사
async function copyContent(contentId) {
    const content = sessionContent.find(item => item.id === contentId);
    if (!content) {
        showToast('콘텐츠를 찾을 수 없습니다.', 'error');
        return;
    }
    
    try {
        await navigator.clipboard.writeText(content.content);
        showToast('콘텐츠가 클립보드에 복사되었습니다!', 'success');
    } catch (error) {
        showToast('복사에 실패했습니다.', 'error');
    }
}

// 콘텐츠 다운로드
function downloadContent(contentId) {
    const content = sessionContent.find(item => item.id === contentId);
    if (!content) {
        showToast('콘텐츠를 찾을 수 없습니다.', 'error');
        return;
    }
    
    const filename = `${content.title.replace(/[^a-zA-Z0-9가-힣]/g, '_')}_${new Date().toISOString().slice(0, 19).replace(/[:-]/g, '')}.md`;
    const blob = new Blob([content.content], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('파일이 다운로드되었습니다!', 'success');
}

// 시간 표시 유틸리티
function getTimeAgo(date) {
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return '방금 전';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}분 전`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}시간 전`;
    return date.toLocaleDateString('ko-KR');
}

// 파일 유형 선택 토글 관리 (더 이상 사용되지 않음)
function updateFormatSelectionVisibility() {
    // 이 함수는 더 이상 필요하지 않지만, 호출하는 곳이 있을 수 있으므로 빈 함수로 유지
}

// 선택된 파일 형식 가져오기 (워드프레스만 지원)
function getSelectedFormats() {
    // Blog 선택 시 항상 워드프레스만 반환
    return ['wordpress'];
}

// Blog 생성 처리 (수정)
async function handleGenerateSelectedEnhancedBlogNews() {
    const selectedFormats = getSelectedFormats();
    console.log('선택된 형식:', selectedFormats);
    await generateSelectedNews('enhanced_blog', selectedFormats);
}

// Blog 파일인지 확인
function isEnhancedBlogFile(filename) {
    return filename && filename.includes('_enhanced_blog');
}

// 🔧 실제 파일명 찾기 (새로운 패턴과 기존 패턴 모두 지원)
async function findActualFilename(groupBaseName, selectedType) {
    try {
        // 생성된 콘텐츠 목록 가져오기
        const response = await fetch(`${API_BASE_URL}/api/generated-content`);
        const result = await response.json();
        
        if (!result.success || !result.data) {
            return null;
        }
        
        // 그룹에 속하는 모든 파일 찾기
        const groupFiles = result.data.filter(file => {
            if (!isEnhancedBlogFile(file.filename)) return false;
            
            // 파일명에서 그룹명 추출
            let fileBaseName = file.filename.replace(/\.(md|html)$/, '').replace(/_(naver|tistory|wordpress)$/, '');
            fileBaseName = fileBaseName.replace(/_\d{6}_\d{3}_enhanced_blog$/, '_enhanced_blog');
            
            return fileBaseName === groupBaseName;
        });
        
        // 선택된 타입에 맞는 파일 찾기
        const targetFile = groupFiles.find(file => {
            if (selectedType === 'md') return file.filename.endsWith('.md');
            if (selectedType === 'naver') return file.filename.endsWith('_naver.html');
            if (selectedType === 'tistory') return file.filename.endsWith('_tistory.html');
            if (selectedType === 'wordpress') return file.filename.endsWith('_wordpress.html');
            return false;
        });
        
        return targetFile ? targetFile.filename : null;
    } catch (error) {
        console.error('파일명 찾기 실패:', error);
        return null;
    }
}

// Blog 파일들을 그룹핑 (새로운 파일명 패턴 지원)
function groupEnhancedBlogFiles(files) {
    const groups = {};
    const regularFiles = [];
    
    files.forEach(file => {
        if (isEnhancedBlogFile(file.filename)) {
            // enhanced_blog 파일의 기본명 추출 (확장자와 플랫폼명 제거)
            let baseName = file.filename.replace(/\.(md|html)$/, '').replace(/_(naver|tistory|wordpress)$/, '');
            
            // 🔧 새로운 파일명 패턴 처리: 마이크로초와 인덱스 제거하여 그룹화
            // 예: n_news_naver_com_20250715_233738_368046_000_enhanced_blog
            //     -> n_news_naver_com_20250715_233738_enhanced_blog
            baseName = baseName.replace(/_\d{6}_\d{3}_enhanced_blog$/, '_enhanced_blog');
            
            // 기존 파일명 패턴도 동일하게 처리
            // 예: finance_yahoo_com_20250715_183840_enhanced_blog (변경 없음)
            
            if (!groups[baseName]) {
                groups[baseName] = {
                    baseName,
                    files: [],
                    content: file.content || '',
                    created_at: file.created_at
                };
            }
            
            // 파일 유형 결정
            let fileType = 'md';
            if (file.filename.endsWith('_naver.html')) fileType = 'naver';
            else if (file.filename.endsWith('_tistory.html')) fileType = 'tistory';
            else if (file.filename.endsWith('_wordpress.html')) fileType = 'wordpress';
            
            groups[baseName].files.push({
                ...file,
                fileType
            });
            
            // 그룹의 최신 시간으로 업데이트 (가장 최근 파일 기준)
            if (new Date(file.created_at) > new Date(groups[baseName].created_at)) {
                groups[baseName].created_at = file.created_at;
                // 콘텐츠도 최신 파일 기준으로 업데이트 (md 파일 우선)
                if (fileType === 'md' || !groups[baseName].content) {
                    groups[baseName].content = file.content || '';
                }
            }
        } else {
            regularFiles.push(file);
        }
    });
    
    return { groups: Object.values(groups), regularFiles };
}

// Blog 파일 유형 선택기 HTML 생성
function createFileTypeSelector(groupBaseName, files) {
    const availableTypes = files.map(f => f.fileType);
    
    return `
        <div class="file-type-selector" id="selector-${groupBaseName}">
            <div class="file-type-options">
                ${availableTypes.map(type => {
                    const typeInfo = {
                        md: { icon: 'fab fa-x-twitter', label: 'X (트위터)' },
                        naver: { icon: 'fas fa-globe', label: '네이버 블로그' },
                        tistory: { icon: 'fas fa-blog', label: '티스토리' },
                        wordpress: { icon: 'fab fa-wordpress', label: '워드프레스' }
                    };
                    
                    const info = typeInfo[type] || { icon: 'fas fa-file', label: type };
                    const isFirst = type === availableTypes[0];
                    
                    return `
                        <button class="file-type-btn ${isFirst ? 'active' : ''}" 
                                onclick="switchFileType('${groupBaseName}', '${type}')"
                                data-type="${type}">
                            <i class="${info.icon}"></i>
                            <span>${info.label}</span>
                        </button>
                    `;
                }).join('')}
            </div>
        </div>
    `;
}

// 파일 유형 전환 함수
function switchFileType(groupBaseName, selectedType) {
    const selector = document.getElementById(`selector-${groupBaseName}`);
    const previewContainer = document.getElementById(`preview-${groupBaseName}`);
    
    if (!selector || !previewContainer) return;
    
    // 버튼 상태 업데이트
    selector.querySelectorAll('.file-type-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.type === selectedType);
    });
    
    // 해당 파일의 콘텐츠로 미리보기 업데이트
    updateEnhancedBlogPreview(groupBaseName, selectedType);
}

// Blog 미리보기 토글
function toggleEnhancedBlogPreview(groupBaseName) {
    const previewDiv = document.getElementById(`preview-${groupBaseName}`);
    if (!previewDiv) return;
    
    if (previewDiv.style.display === 'none') {
        // 현재 선택된 파일 유형 가져오기
        const selector = document.getElementById(`selector-${groupBaseName}`);
        const activeBtn = selector ? selector.querySelector('.file-type-btn.active') : null;
        const selectedType = activeBtn ? activeBtn.dataset.type : 'md';
        
        updateEnhancedBlogPreview(groupBaseName, selectedType);
        previewDiv.style.display = 'block';
    } else {
        previewDiv.style.display = 'none';
    }
}

// Blog 미리보기 업데이트 (새로운 파일명 패턴 지원)
async function updateEnhancedBlogPreview(groupBaseName, selectedType) {
    const previewDiv = document.getElementById(`preview-${groupBaseName}`);
    if (!previewDiv) return;
    
    try {
        // 🔧 실제 파일명 찾기 (새로운 패턴과 기존 패턴 모두 지원)
        const actualFilename = await findActualFilename(groupBaseName, selectedType);
        if (!actualFilename) {
            throw new Error('파일을 찾을 수 없습니다.');
        }
        
        // 파일 내용 가져오기
        const response = await fetch(`${API_BASE_URL}/api/generated-content/${actualFilename}`);
        const result = await response.json();
        
        if (result.success && result.data) {
            let content = result.data.content;
            
            if (selectedType === 'md') {
                // 마크다운 형식으로 표시
                previewDiv.innerHTML = `
                    <div class="content-preview-header">
                        <h4><i class="fab fa-markdown"></i> Markdown 미리보기</h4>
                    </div>
                    <div class="content-preview-body">
                        <pre class="markdown-preview">${content}</pre>
                    </div>
                `;
            } else {
                // HTML 형식으로 표시
                const platformNames = {
                    naver: '네이버 블로그',
                    tistory: '티스토리', 
                    wordpress: '워드프레스'
                };
                
                previewDiv.innerHTML = `
                    <div class="content-preview-header">
                        <h4><i class="fas fa-globe"></i> ${platformNames[selectedType]} 미리보기</h4>
                    </div>
                    <div class="content-preview-body">
                        <div class="html-preview">${content}</div>
                    </div>
                `;
            }
        } else {
            previewDiv.innerHTML = `
                <div class="preview-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>미리보기를 불러올 수 없습니다.</span>
                </div>
            `;
        }
    } catch (error) {
        console.error('미리보기 로드 실패:', error);
        previewDiv.innerHTML = `
            <div class="preview-error">
                <i class="fas fa-exclamation-triangle"></i>
                <span>미리보기 로드 중 오류가 발생했습니다.</span>
            </div>
        `;
    }
}

// Blog 콘텐츠 복사 (새로운 파일명 패턴 지원)
async function copyEnhancedBlogContent(groupBaseName) {
    try {
        // 현재 선택된 파일 유형 가져오기
        const selector = document.getElementById(`selector-${groupBaseName}`);
        const activeBtn = selector ? selector.querySelector('.file-type-btn.active') : null;
        const selectedType = activeBtn ? activeBtn.dataset.type : 'md';
        
        // 🔧 실제 파일명 찾기 (새로운 패턴과 기존 패턴 모두 지원)
        const actualFilename = await findActualFilename(groupBaseName, selectedType);
        if (!actualFilename) {
            showToast('파일을 찾을 수 없습니다.', 'error');
            return;
        }
        
        // 파일 내용 가져오기
        const response = await fetch(`${API_BASE_URL}/api/generated-content/${actualFilename}`);
        const result = await response.json();
        
        if (result.success && result.data) {
            await navigator.clipboard.writeText(result.data.content);
            
            const platformNames = {
                md: 'X (트위터)',
                naver: '네이버 블로그',
                tistory: '티스토리',
                wordpress: '워드프레스'
            };
            
            showToast(`${platformNames[selectedType]} 콘텐츠가 클립보드에 복사되었습니다.`, 'success');
        } else {
            showToast('콘텐츠 복사에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('복사 실패:', error);
        showToast('콘텐츠 복사 중 오류가 발생했습니다.', 'error');
    }
}

// Blog 콘텐츠 다운로드 (새로운 파일명 패턴 지원)
async function downloadEnhancedBlogContent(groupBaseName) {
    try {
        // 현재 선택된 파일 유형 가져오기
        const selector = document.getElementById(`selector-${groupBaseName}`);
        const activeBtn = selector ? selector.querySelector('.file-type-btn.active') : null;
        const selectedType = activeBtn ? activeBtn.dataset.type : 'md';
        
        // 🔧 실제 파일명 찾기 (새로운 패턴과 기존 패턴 모두 지원)
        const actualFilename = await findActualFilename(groupBaseName, selectedType);
        if (!actualFilename) {
            showToast('파일을 찾을 수 없습니다.', 'error');
            return;
        }
        
        // 파일 다운로드
        const link = document.createElement('a');
        link.href = `${API_BASE_URL}/api/download/${actualFilename}`;
        link.download = actualFilename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showToast('파일 다운로드가 시작되었습니다.', 'success');
    } catch (error) {
        console.error('다운로드 실패:', error);
        showToast('파일 다운로드 중 오류가 발생했습니다.', 'error');
    }
}



// ============================================================================
// 가이드라인 관련 기능
// ============================================================================

// 가이드라인 버튼 업데이트
function updateGuidelineButton() {
    const guidelineBtn = document.getElementById('showGuidelineBtn');
    const guidelineBtnText = document.getElementById('guidelineButtonText');
    const selectedType = getSelectedContentType();
    
    if (guidelineBtn && guidelineBtnText) {
        // 가이드라인 버튼 표시
        guidelineBtn.style.display = 'inline-block';
        
        // 콘텐츠 타입별 버튼 텍스트 설정
        const guidelineNames = {
            'x': 'X(Twitter) Short Form 가이드라인',
            'standard': 'X(Twitter) Normal Form 가이드라인',
            'threads': 'Threads 가이드라인',
            'enhanced_blog': 'Blog 가이드라인'
        };
        
        guidelineBtnText.textContent = guidelineNames[selectedType] || '가이드라인 보기';
    }
}

// 가이드라인 보기 버튼 클릭 핸들러
function showGuideline() {
    const selectedType = getSelectedContentType();
    const modal = document.getElementById('guidelineModal');
    const modalTitle = document.getElementById('guidelineModalTitle');
    const guidelineContent = document.getElementById('guidelineContent');
    
    if (!modal || !modalTitle || !guidelineContent) return;
    
    // 파일명 매핑
    const guidelineFiles = {
        'x': 'x-twitter-short-form.md',
        'standard': 'x-twitter-normal-form.md',
        'threads': 'threads.md',
        'enhanced_blog': 'blog.md'
    };
    
    const guidelineTitles = {
        'x': 'X(Twitter) Short Form 콘텐츠 생성 가이드라인',
        'standard': 'X(Twitter) Normal Form 콘텐츠 생성 가이드라인',
        'threads': 'Threads 콘텐츠 생성 가이드라인',
        'enhanced_blog': 'Blog 콘텐츠 생성 가이드라인'
    };
    
    const filename = guidelineFiles[selectedType];
    const title = guidelineTitles[selectedType];
    
    if (!filename) {
        showToast('가이드라인을 찾을 수 없습니다.', 'error');
        return;
    }
    
    // 제목 설정
    modalTitle.innerHTML = `<i class="fas fa-book"></i> ${title}`;
    
    // 로딩 표시
    guidelineContent.innerHTML = '<div class="loading-message"><i class="fas fa-spinner fa-spin"></i> 가이드라인 로드 중...</div>';
    
    // 모달 표시
    modal.style.display = 'flex';
    
    // 가이드라인 파일 로드
    fetch(`./guidelines/${filename}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('가이드라인 파일을 찾을 수 없습니다.');
            }
            return response.text();
        })
        .then(markdown => {
            // Markdown을 HTML로 변환 (marked.js 사용)
            if (typeof marked !== 'undefined') {
                const html = marked.parse(markdown);
                guidelineContent.innerHTML = html;
            } else {
                // marked.js가 없으면 그대로 표시
                guidelineContent.innerHTML = `<pre>${markdown}</pre>`;
            }
        })
        .catch(error => {
            console.error('가이드라인 로드 실패:', error);
            guidelineContent.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>가이드라인을 불러올 수 없습니다.</p>
                    <small>${error.message}</small>
                </div>
            `;
        });
}

// 가이드라인 모달 닫기
function closeGuidelineModal() {
    const modal = document.getElementById('guidelineModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// ESC 키로 모달 닫기
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeGuidelineModal();
    }
});

// 모달 외부 클릭으로 닫기
document.addEventListener('click', function(event) {
    const modal = document.getElementById('guidelineModal');
    if (event.target === modal) {
        closeGuidelineModal();
    }
});

// 가이드라인 버튼 이벤트 리스너 설정
document.addEventListener('DOMContentLoaded', function() {
    const guidelineBtn = document.getElementById('showGuidelineBtn');
    if (guidelineBtn) {
        guidelineBtn.addEventListener('click', showGuideline);
    }
    
    // 초기 상태에서 가이드라인 버튼 업데이트
    updateGuidelineButton();
});

// ========== Authentication Functions ==========

// UI 업데이트 함수
window.updateAuthUI = function(isAuthenticated) {
    const authButton = document.getElementById('authButton');
    const userMenu = document.getElementById('userMenu');
    
    if (isAuthenticated && authManager.user) {
        authButton.style.display = 'none';
        userMenu.style.display = 'flex';
        
        const displayName = document.getElementById('userDisplayName');
        displayName.textContent = authManager.user.username || authManager.user.email.split('@')[0];
    } else {
        authButton.style.display = 'flex';
        userMenu.style.display = 'none';
    }
};

// 모달 관련 함수들
function showAuthModal() {
    document.getElementById('authModal').style.display = 'block';
}

function closeAuthModal() {
    document.getElementById('authModal').style.display = 'none';
    document.getElementById('loginError').textContent = '';
    document.getElementById('registerError').textContent = '';
}

function showApiKeysModal() {
    document.getElementById('apiKeysModal').style.display = 'block';
    document.getElementById('userDropdown').style.display = 'none';
    loadApiKeys();
}

function closeApiKeysModal() {
    document.getElementById('apiKeysModal').style.display = 'none';
}

function showProfileModal() {
    document.getElementById('profileModal').style.display = 'block';
    document.getElementById('userDropdown').style.display = 'none';
    loadProfile();
}

function closeProfileModal() {
    document.getElementById('profileModal').style.display = 'none';
}

// 탭 전환
document.querySelectorAll('.auth-tab-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const tab = this.getAttribute('data-tab');
        
        // 탭 버튼 활성화
        document.querySelectorAll('.auth-tab-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        // 탭 콘텐츠 전환
        document.querySelectorAll('.auth-tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tab + 'Tab').classList.add('active');
    });
});

// 로그인 처리
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const errorDiv = document.getElementById('loginError');
    
    errorDiv.textContent = '';
    
    const result = await authManager.login(email, password);
    
    if (result.success) {
        closeAuthModal();
        showToast('로그인되었습니다!', 'success');
        
        // API 키 입력 필드 제거 또는 숨기기
        document.querySelectorAll('.api-key-input').forEach(input => {
            input.style.display = 'none';
        });
    } else {
        errorDiv.textContent = result.error || '로그인에 실패했습니다.';
    }
}

// 회원가입 처리
async function handleRegister(event) {
    event.preventDefault();
    
    const email = document.getElementById('registerEmail').value;
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;
    const errorDiv = document.getElementById('registerError');
    
    errorDiv.textContent = '';
    
    const result = await authManager.register(email, password, username);
    
    if (result.success) {
        closeAuthModal();
        showToast('회원가입이 완료되었습니다!', 'success');
        
        // API 키 설정 안내
        setTimeout(() => {
            if (confirm('API 키를 지금 설정하시겠습니까?')) {
                showApiKeysModal();
            }
        }, 1000);
    } else {
        errorDiv.textContent = result.error || '회원가입에 실패했습니다.';
    }
}

// API 키 저장
async function saveApiKey(provider) {
    const input = document.getElementById(provider + 'Key');
    const apiKey = input.value.trim();
    const messageDiv = document.getElementById('apiKeyMessage');
    
    if (!apiKey) {
        messageDiv.textContent = 'API 키를 입력해주세요.';
        messageDiv.className = 'message error';
        return;
    }
    
    const result = await authManager.saveApiKey(provider, apiKey);
    
    if (result.success) {
        messageDiv.textContent = result.message;
        messageDiv.className = 'message success';
        input.value = '';
        
        // 3초 후 메시지 제거
        setTimeout(() => {
            messageDiv.textContent = '';
        }, 3000);
    } else {
        messageDiv.textContent = result.error || 'API 키 저장에 실패했습니다.';
        messageDiv.className = 'message error';
    }
}

// API 키 테스트
async function testApiKey(provider) {
    const messageDiv = document.getElementById('apiKeyMessage');
    
    messageDiv.textContent = '테스트 중...';
    messageDiv.className = 'message';
    
    const result = await authManager.testApiKey(provider);
    
    if (result.success) {
        messageDiv.textContent = result.message;
        messageDiv.className = 'message success';
    } else {
        messageDiv.textContent = result.error || 'API 키 테스트에 실패했습니다.';
        messageDiv.className = 'message error';
    }
    
    // 3초 후 메시지 제거
    setTimeout(() => {
        messageDiv.textContent = '';
    }, 3000);
}

// API 키 목록 로드
async function loadApiKeys() {
    const result = await authManager.getApiKeys();
    
    if (result.success && result.api_keys) {
        result.api_keys.forEach(key => {
            const input = document.getElementById(key.provider + 'Key');
            if (input) {
                input.placeholder = key.masked_key || 'API 키가 저장되어 있습니다';
            }
        });
    }
}

// 프로필 로드
async function loadProfile() {
    const result = await authManager.getProfile();
    
    if (result.success && result.user) {
        document.getElementById('profileEmail').value = result.user.email;
        document.getElementById('profileUsername').value = result.user.username || '';
    }
}

// 프로필 업데이트
async function handleUpdateProfile(event) {
    event.preventDefault();
    
    const username = document.getElementById('profileUsername').value;
    const messageDiv = document.getElementById('profileMessage');
    
    const result = await authManager.updateProfile({ username });
    
    if (result.success) {
        messageDiv.textContent = result.message;
        messageDiv.className = 'message success';
        
        // UI 업데이트
        const displayName = document.getElementById('userDisplayName');
        displayName.textContent = result.user.username || result.user.email.split('@')[0];
        
        setTimeout(() => {
            messageDiv.textContent = '';
        }, 3000);
    } else {
        messageDiv.textContent = result.error || '프로필 업데이트에 실패했습니다.';
        messageDiv.className = 'message error';
    }
}

// 사용자 메뉴 토글
document.getElementById('userMenuButton')?.addEventListener('click', function() {
    const dropdown = document.getElementById('userDropdown');
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
});

// 클릭 외부 영역 클릭 시 드롭다운 닫기
document.addEventListener('click', function(event) {
    if (!event.target.closest('.user-menu')) {
        document.getElementById('userDropdown').style.display = 'none';
    }
});

// 모달 외부 클릭 시 닫기
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
};

// 페이지 로드 시 인증 상태 확인
document.addEventListener('DOMContentLoaded', function() {
    updateAuthUI(authManager.isAuthenticated());
});

// 기존 콘텐츠 생성 함수 수정 (로그인 사용자용)
const originalGenerateContent = window.generateContent;
window.generateContent = async function() {
    // 로그인한 경우 v2 API 사용
    if (authManager.isAuthenticated()) {
        const selectedUrl = document.getElementById('selectedUrl').value;
        const selectedContentType = document.querySelector('input[name="contentType"]:checked').value;
        const selectedProvider = document.querySelector('input[name="apiProvider"]:checked').value;
        
        if (!selectedUrl) {
            showToast('URL을 선택해주세요.', 'error');
            return;
        }
        
        try {
            showLoading(true, '콘텐츠 생성 중...');
            
            const response = await authManager.makeAuthRequest(
                `${window.CONFIG.API_URL}/api/v2/generate`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        url: selectedUrl,
                        content_type: selectedContentType,
                        api_provider: selectedProvider
                    })
                }
            );
            
            const result = await response.json();
            
            if (result.success) {
                showToast('콘텐츠가 생성되었습니다!', 'success');
                addGeneratedContent(result.data);
            } else {
                showToast(result.error || '콘텐츠 생성에 실패했습니다.', 'error');
            }
        } catch (error) {
            console.error('Generate content error:', error);
            showToast(error.message || '콘텐츠 생성 중 오류가 발생했습니다.', 'error');
        } finally {
            showLoading(false);
        }
    } else {
        // 로그인하지 않은 경우 기존 방식 사용
        originalGenerateContent();
    }
};