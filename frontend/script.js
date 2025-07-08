// Global variables
let currentJobId = null;
let currentData = null;
let currentBatchJobId = null;
let currentBatchData = null;

// URL inputs management
let urlInputCount = 1;
const maxUrlInputs = 3;

// API Configuration
const API_BASE_URL = window.ENV?.API_BASE_URL || 'http://localhost:8080';

// DOM elements
const urlForm = document.getElementById('urlForm');
const urlInputsContainer = document.getElementById('urlInputsContainer');
const batchSection = document.getElementById('batchSection');
const batchUrls = document.getElementById('batchUrls');
const processBatchBtn = document.getElementById('processBatchBtn');
const cancelBatchBtn = document.getElementById('cancelBatchBtn');

// API settings elements
const apiSettingsBtn = document.getElementById('apiSettingsBtn');
const apiStatus = document.getElementById('apiStatus');
const apiSettingsSection = document.getElementById('apiSettingsSection');
const apiProviderSelect = document.getElementById('apiProviderSelect');
const apiKeyInput = document.getElementById('apiKeyInput');
const toggleApiKeyBtn = document.getElementById('toggleApiKeyBtn');
const validateApiKeyBtn = document.getElementById('validateApiKeyBtn');
const saveApiKeyBtn = document.getElementById('saveApiKeyBtn');
const deleteApiKeyBtn = document.getElementById('deleteApiKeyBtn');
const cancelApiSettingsBtn = document.getElementById('cancelApiSettingsBtn');
const apiValidationResult = document.getElementById('apiValidationResult');
const progressSection = document.getElementById('progressSection');
const progressTitle = document.getElementById('progressTitle');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const resultSection = document.getElementById('resultSection');
// const resultTitle = document.getElementById('resultTitle'); // Removed
// const resultTime = document.getElementById('resultTime'); // Removed
// const resultApi = document.getElementById('resultApi'); // Removed
const markdownPreview = document.getElementById('markdownPreview');
// const markdownCode = document.getElementById('markdownCode'); // Removed
const downloadBtn = document.getElementById('downloadBtn');
const copyBtn = document.getElementById('copyBtn');
const resetBtn = document.getElementById('resetBtn');
const batchResultSection = document.getElementById('batchResultSection');
const batchSummary = document.getElementById('batchSummary');
const batchResults = document.getElementById('batchResults');
const downloadAllBtn = document.getElementById('downloadAllBtn');
const resetBatchBtn = document.getElementById('resetBatchBtn');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');
const retryBtn = document.getElementById('retryBtn');
const toastContainer = document.getElementById('toastContainer');

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    initEventListeners();
    loadApiSettings();
    
    // Initialize URL input buttons
    updateUrlInputButtons();
    
    // Check if marked.js is loaded
    if (typeof marked === 'undefined') {
        showToast('마크다운 라이브러리를 로드할 수 없습니다.', 'error');
    }
    
    // Mobile optimizations
    initMobileOptimizations();
});

// Mobile optimizations
function initMobileOptimizations() {
    // Prevent zoom on input focus for iOS
    if (window.navigator.userAgent.match(/iPhone|iPad|iPod/i)) {
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                if (this.style.fontSize !== '16px') {
                    this.style.fontSize = '16px';
                }
            });
        });
    }
    
    // Add touch event optimization
    const touchableElements = document.querySelectorAll('.btn, .tab-btn, .add-url-btn, .remove-url-btn');
    touchableElements.forEach(element => {
        element.style.touchAction = 'manipulation';
        element.style.userSelect = 'none';
        element.style.webkitUserSelect = 'none';
        element.style.msUserSelect = 'none';
    });
    
    // Handle virtual keyboard on mobile
    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', function() {
            // Adjust UI when virtual keyboard appears/disappears
            const body = document.body;
            if (window.visualViewport.height < window.innerHeight) {
                body.style.paddingBottom = `${window.innerHeight - window.visualViewport.height}px`;
            } else {
                body.style.paddingBottom = '0px';
            }
        });
    }
    
    // Prevent overscroll bounce on iOS
    document.addEventListener('touchmove', function(e) {
        if (e.target.tagName !== 'TEXTAREA' && e.target.tagName !== 'INPUT') {
            e.preventDefault();
        }
    }, { passive: false });
    
    // 터치 피드백 최소화
    touchableElements.forEach(element => {
        element.addEventListener('touchstart', function(e) {
            this.style.opacity = '0.8';
        });
        
        element.addEventListener('touchend', function(e) {
            this.style.opacity = '';
        });
        
        element.addEventListener('touchcancel', function(e) {
            this.style.opacity = '';
        });
    });
}

// Apply mobile optimizations to new elements
function applyMobileOptimizationsToNewElements(container) {
    const newTouchableElements = container.querySelectorAll('.btn, .tab-btn, .add-url-btn, .remove-url-btn');
    newTouchableElements.forEach(element => {
        element.style.touchAction = 'manipulation';
        element.style.userSelect = 'none';
        element.style.webkitUserSelect = 'none';
        element.style.msUserSelect = 'none';
        
        // 터치 피드백 최소화
        element.addEventListener('touchstart', function(e) {
            this.style.opacity = '0.8';
        });
        
        element.addEventListener('touchend', function(e) {
            this.style.opacity = '';
        });
        
        element.addEventListener('touchcancel', function(e) {
            this.style.opacity = '';
        });
    });
    
    // Apply iOS font size fix to new inputs
    if (window.navigator.userAgent.match(/iPhone|iPad|iPod/i)) {
        const newInputs = container.querySelectorAll('input, textarea, select');
        newInputs.forEach(input => {
            input.addEventListener('focus', function() {
                if (this.style.fontSize !== '16px') {
                    this.style.fontSize = '16px';
                }
            });
        });
    }
}

// Event listeners
function initEventListeners() {
    // Form submission
    urlForm.addEventListener('submit', handleFormSubmit);
    
    // API settings
    apiSettingsBtn.addEventListener('click', showApiSettingsSection);
    cancelApiSettingsBtn.addEventListener('click', hideApiSettingsSection);
    toggleApiKeyBtn.addEventListener('click', toggleApiKeyVisibility);
    validateApiKeyBtn.addEventListener('click', validateApiKey);
    saveApiKeyBtn.addEventListener('click', saveApiKey);
    deleteApiKeyBtn.addEventListener('click', deleteApiKey);
    apiProviderSelect.addEventListener('change', onApiProviderChange);
    apiKeyInput.addEventListener('input', onApiKeyInput);
    
    // URL input click-to-select-all functionality
    initUrlInputSelectAll();
    
    // Batch handling (기존 배치 UI용)
    processBatchBtn.addEventListener('click', handleBatchProcess);
    cancelBatchBtn.addEventListener('click', hideBatchSection);
    
    // Result actions
    downloadBtn.addEventListener('click', downloadFile);
    copyBtn.addEventListener('click', copyToClipboard);
    resetBtn.addEventListener('click', resetForm);
    downloadAllBtn.addEventListener('click', downloadAllFiles);
    resetBatchBtn.addEventListener('click', resetForm);
    retryBtn.addEventListener('click', retryGeneration);
}

// URL 입력창 전체선택 기능 초기화
function initUrlInputSelectAll() {
    // 이벤트 위임을 사용하여 동적으로 생성되는 URL 입력창에도 적용
    urlInputsContainer.addEventListener('click', function(e) {
        if (e.target.matches('input[type="url"]')) {
            // 첫 클릭 시에만 전체선택
            if (!e.target.hasAttribute('data-clicked')) {
                e.target.select();
                e.target.setAttribute('data-clicked', 'true');
                
                // 포커스가 벗어나면 data-clicked 속성 제거
                e.target.addEventListener('blur', function() {
                    this.removeAttribute('data-clicked');
                }, { once: true });
            }
        }
    });
}

// URL inputs management functions
function addUrlInput(currentIndex) {
    if (urlInputCount >= maxUrlInputs) {
        showToast('최대 3개의 URL까지 입력할 수 있습니다.', 'warning');
        return;
    }
    
    const newIndex = urlInputCount;
    urlInputCount++;
    
    const newRow = document.createElement('div');
    newRow.className = 'url-input-row';
    newRow.setAttribute('data-index', newIndex);
    
    newRow.innerHTML = `
        <div class="form-group">
            <div class="input-with-buttons">
                <input 
                    type="url" 
                    id="urlInput-${newIndex}" 
                    name="urlInput[]"
                    placeholder="https://news.example.com/article"
                    required
                >
                ${urlInputCount < maxUrlInputs ? 
                    `<button type="button" class="btn btn-icon add-url-btn" onclick="addUrlInput(${newIndex})">
                        <i class="fas fa-plus"></i>
                    </button>` : ''
                }
                <button type="button" class="btn btn-icon remove-url-btn" onclick="removeUrlInput(${newIndex})">
                    <i class="fas fa-minus"></i>
                </button>
            </div>
        </div>
    `;
    
    urlInputsContainer.appendChild(newRow);
    
    // Remove add button from previous row
    const prevRow = document.querySelector(`[data-index="${currentIndex}"]`);
    if (prevRow) {
        const prevAddBtn = prevRow.querySelector('.add-url-btn');
        if (prevAddBtn) {
            prevAddBtn.remove();
        }
    }
    
    // Focus on new input
    document.getElementById(`urlInput-${newIndex}`).focus();
    
    // Update button states
    updateUrlInputButtons();
    
    // Apply mobile optimizations to new buttons
    applyMobileOptimizationsToNewElements(newRow);
}

function removeUrlInput(index) {
    if (urlInputCount <= 1) {
        showToast('최소 1개의 URL 입력창이 필요합니다.', 'warning');
        return;
    }
    
    const row = document.querySelector(`[data-index="${index}"]`);
    if (row) {
        row.remove();
        urlInputCount--;
        
        // Find the last row and add the add button if needed
        const lastRow = Array.from(urlInputsContainer.children).pop();
        if (lastRow && urlInputCount < maxUrlInputs) {
            const buttonContainer = lastRow.querySelector('.input-with-buttons');
            const removeBtn = buttonContainer.querySelector('.remove-url-btn');
            
            if (!buttonContainer.querySelector('.add-url-btn')) {
                const addBtn = document.createElement('button');
                addBtn.type = 'button';
                addBtn.className = 'btn btn-icon add-url-btn';
                addBtn.innerHTML = '<i class="fas fa-plus"></i>';
                addBtn.onclick = () => addUrlInput(parseInt(lastRow.getAttribute('data-index')));
                
                buttonContainer.insertBefore(addBtn, removeBtn);
                
                // Apply mobile optimizations to new button
                applyMobileOptimizationsToNewElements(buttonContainer);
            }
        }
        
        updateUrlInputButtons();
    }
}

function updateUrlInputButtons() {
    const rows = urlInputsContainer.querySelectorAll('.url-input-row');
    rows.forEach((row, index) => {
        const removeBtn = row.querySelector('.remove-url-btn');
        if (removeBtn) {
            removeBtn.style.display = rows.length > 1 ? 'inline-flex' : 'none';
        }
    });
}

function getAllUrls() {
    const urls = [];
    const inputs = urlInputsContainer.querySelectorAll('input[type="url"]');
    inputs.forEach(input => {
        const url = input.value.trim();
        if (url) {
            urls.push(url);
        }
    });
    return urls;
}

// Form submission handler
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const urls = getAllUrls();
    const apiSettings = getApiSettings();
    
    if (urls.length === 0) {
        showToast('URL을 입력해주세요.', 'error');
        return;
    }
    
    // Validate URLs
    const invalidUrls = urls.filter(url => !isValidUrl(url));
    if (invalidUrls.length > 0) {
        showToast(`잘못된 URL이 있습니다: ${invalidUrls.join(', ')}`, 'error');
        return;
    }
    
    if (!apiSettings) {
        showToast('API 키를 설정해주세요.', 'error');
        showApiSettingsSection();
        return;
    }
    
    try {
        hideAllSections();
        showProgressSection();
        
        if (urls.length === 1) {
            // Single URL processing
            const requestData = {
                url: urls[0],
                api_provider: apiSettings.provider,
                api_key: apiSettings.key,
                save_intermediate: false
            };
            
            const response = await fetch(`${API_BASE_URL}/api/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                currentJobId = data.job_id;
                currentData = data.data;
                showResultSection();
                showToast('콘텐츠가 성공적으로 생성되었습니다!', 'success');
            } else {
                showErrorSection(data.error);
                showToast('콘텐츠 생성에 실패했습니다.', 'error');
            }
        } else {
            // Multiple URLs processing (batch)
            progressTitle.textContent = `배치 처리 중... (${urls.length}개 URL)`;
            
            const requestData = {
                urls: urls,
                api_provider: apiSettings.provider,
                api_key: apiSettings.key,
                save_intermediate: false
            };
            
            const response = await fetch(`${API_BASE_URL}/api/batch-generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                currentBatchJobId = data.job_id;
                currentBatchData = data.data;
                showBatchResultSection();
                showToast('배치 처리가 성공적으로 완료되었습니다!', 'success');
            } else {
                showErrorSection(data.error);
                showToast('배치 처리에 실패했습니다.', 'error');
            }
        }
        
    } catch (error) {
        console.error('Error:', error);
        showErrorSection('서버와의 통신에 실패했습니다.');
        showToast('서버 연결에 실패했습니다.', 'error');
    }
}

// Batch processing (기존 배치 UI용)
function hideBatchSection() {
    batchSection.style.display = 'none';
    batchUrls.value = '';
}

async function handleBatchProcess() {
    const urls = batchUrls.value.trim().split('\n').filter(url => url.trim());
    const apiSettings = getApiSettings();
    
    if (urls.length === 0) {
        showToast('URL을 입력해주세요.', 'error');
        return;
    }
    
    if (!apiSettings) {
        showToast('API 키를 설정해주세요.', 'error');
        showApiSettingsSection();
        return;
    }
    
    // Validate URLs
    const invalidUrls = urls.filter(url => !isValidUrl(url.trim()));
    if (invalidUrls.length > 0) {
        showToast(`잘못된 URL이 있습니다: ${invalidUrls.join(', ')}`, 'error');
        return;
    }
    
    try {
        hideAllSections();
        showProgressSection();
        progressTitle.textContent = `배치 처리 중... (${urls.length}개 URL)`;
        
        const requestData = {
            urls: urls.map(url => url.trim()),
            api_provider: apiSettings.provider,
            api_key: apiSettings.key,
            save_intermediate: false
        };
        
        const response = await fetch(`${API_BASE_URL}/api/batch`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentBatchJobId = data.job_id;
            currentBatchData = data.data;
            showBatchResultSection();
            showToast('배치 처리가 완료되었습니다!', 'success');
        } else {
            showErrorSection(data.error);
            showToast('배치 처리에 실패했습니다.', 'error');
        }
        
    } catch (error) {
        console.error('Batch Error:', error);
        showErrorSection('배치 처리 중 오류가 발생했습니다.');
        showToast('배치 처리에 실패했습니다.', 'error');
    }
}

// Section visibility management
function hideAllSections() {
    const sections = [
        'progressSection', 'resultSection', 'batchResultSection', 'errorSection', 'apiSettingsSection'
    ];
    sections.forEach(sectionId => {
        document.getElementById(sectionId).style.display = 'none';
    });
}

function showProgressSection() {
    progressSection.style.display = 'block';
    progressTitle.textContent = '처리 중...';
    updateProgress(0);
    
    // Simulate progress
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 20;
        if (progress >= 90) {
            progress = 90;
            clearInterval(interval);
        }
        updateProgress(progress);
    }, 500);
}

function updateProgress(percentage) {
    progressFill.style.width = percentage + '%';
    progressText.textContent = Math.round(percentage) + '%';
}

function showResultSection() {
    hideAllSections();
    resultSection.style.display = 'block';
    
    // Render markdown preview directly
    if (typeof marked !== 'undefined') {
        markdownPreview.innerHTML = marked.parse(currentData.content);
    } else {
        markdownPreview.innerHTML = '<p>마크다운 미리보기를 로드할 수 없습니다.</p>';
    }
}

function showBatchResultSection() {
    hideAllSections();
    batchResultSection.style.display = 'block';
    
    // Populate batch summary
    const summary = currentBatchData.summary;
    batchSummary.innerHTML = `
        <h3>배치 처리 결과</h3>
        <p><strong>총 처리:</strong> ${summary.total}개</p>
        <p><strong>성공:</strong> ${summary.successful}개</p>
        <p><strong>실패:</strong> ${summary.failed}개</p>
    `;
    
    // Populate batch results
    batchResults.innerHTML = '';
    currentBatchData.results.forEach((result, index) => {
        const item = document.createElement('div');
        item.className = `batch-item ${result.success ? 'success' : 'error'}`;
        
        if (result.success) {
            item.innerHTML = `
                <h4>${result.title}</h4>
                <p><strong>URL:</strong> ${result.url}</p>
                <p><strong>처리 시간:</strong> ${new Date(result.timestamp).toLocaleString('ko-KR')}</p>
                <div class="batch-actions">
                    <button class="btn btn-success" onclick="downloadBatchItem(${index})">
                        <i class="fas fa-download"></i> 다운로드
                    </button>
                    <button class="btn btn-info" onclick="previewBatchItem(${index})">
                        <i class="fas fa-eye"></i> 미리보기
                    </button>
                    <button class="btn btn-copy" onclick="copyBatchItem(${index})">
                        <i class="fas fa-copy"></i> 복사
                    </button>
                </div>
            `;
        } else {
            item.innerHTML = `
                <h4>처리 실패</h4>
                <p><strong>URL:</strong> ${result.url}</p>
                <p><strong>오류:</strong> ${result.error}</p>
            `;
        }
        
        batchResults.appendChild(item);
    });
}

function showErrorSection(message) {
    hideAllSections();
    errorSection.style.display = 'block';
    
    // 에러 타입에 따라 다른 스타일과 아이콘 적용
    let errorIcon = '⚠️';
    let errorTitle = '오류 발생';
    let errorClass = 'error-default';
    
    if (message.includes('차단')) {
        errorIcon = '🚫';
        errorTitle = '접근 차단';
        errorClass = 'error-blocked';
    } else if (message.includes('찾을 수 없습니다')) {
        errorIcon = '🔍';
        errorTitle = '페이지 없음';
        errorClass = 'error-notfound';
    } else if (message.includes('시간 초과')) {
        errorIcon = '⏱️';
        errorTitle = '시간 초과';
        errorClass = 'error-timeout';
    } else if (message.includes('네트워크')) {
        errorIcon = '🌐';
        errorTitle = '네트워크 오류';
        errorClass = 'error-network';
    } else if (message.includes('서버')) {
        errorIcon = '🔧';
        errorTitle = '서버 오류';
        errorClass = 'error-server';
    }
    
    // 에러 메시지를 더 구조적으로 표시
    errorMessage.innerHTML = `
        <div class="error-content ${errorClass}">
            <div class="error-header">
                <span class="error-icon">${errorIcon}</span>
                <span class="error-title">${errorTitle}</span>
            </div>
            <div class="error-message">${message}</div>
        </div>
    `;
}

// Tab switching - removed (no longer needed)

// File operations
async function downloadFile() {
    if (!currentJobId) {
        showToast('다운로드할 파일이 없습니다.', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/download/${currentJobId}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${currentData.title}_${currentData.timestamp}.md`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            showToast('파일이 다운로드되었습니다.', 'success');
        } else {
            showToast('파일 다운로드에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('Download error:', error);
        showToast('파일 다운로드에 실패했습니다.', 'error');
    }
}

async function copyToClipboard() {
    if (!currentData) {
        showToast('복사할 내용이 없습니다.', 'error');
        return;
    }
    
    try {
        await navigator.clipboard.writeText(currentData.content);
        showToast('클립보드에 복사되었습니다.', 'success');
    } catch (error) {
        console.error('Copy error:', error);
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = currentData.content;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('클립보드에 복사되었습니다.', 'success');
    }
}

// Batch file operations
async function downloadBatchItem(index) {
    const item = currentBatchData.results[index];
    if (!item.success) return;
    
    const blob = new Blob([item.content], { type: 'text/markdown' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${item.title}_${item.timestamp}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    showToast('파일이 다운로드되었습니다.', 'success');
}

async function copyBatchItem(index) {
    const item = currentBatchData.results[index];
    if (!item.success) return;
    
    try {
        await navigator.clipboard.writeText(item.content);
        showToast('클립보드에 복사되었습니다.', 'success');
    } catch (error) {
        console.error('Copy error:', error);
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = item.content;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('클립보드에 복사되었습니다.', 'success');
    }
}

function previewBatchItem(index) {
    const item = currentBatchData.results[index];
    if (!item.success) return;
    
    // Create a modal or new window for preview
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    `;
    
    const content = document.createElement('div');
    content.style.cssText = `
        background: white;
        border-radius: 10px;
        padding: 30px;
        max-width: 80%;
        max-height: 80%;
        overflow-y: auto;
        position: relative;
    `;
    
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '&times;';
    closeBtn.style.cssText = `
        position: absolute;
        top: 10px;
        right: 15px;
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #666;
    `;
    
    const title = document.createElement('h2');
    title.textContent = item.title;
    title.style.marginBottom = '20px';
    
    const preview = document.createElement('div');
    if (typeof marked !== 'undefined') {
        preview.innerHTML = marked.parse(item.content);
    } else {
        preview.innerHTML = `<pre>${item.content}</pre>`;
    }
    
    content.appendChild(closeBtn);
    content.appendChild(title);
    content.appendChild(preview);
    modal.appendChild(content);
    document.body.appendChild(modal);
    
    // Close modal events
    closeBtn.addEventListener('click', () => document.body.removeChild(modal));
    modal.addEventListener('click', (e) => {
        if (e.target === modal) document.body.removeChild(modal);
    });
}

async function downloadAllFiles() {
    if (!currentBatchData) {
        showToast('다운로드할 파일이 없습니다.', 'error');
        return;
    }
    
    const successfulResults = currentBatchData.results.filter(r => r.success);
    
    if (successfulResults.length === 0) {
        showToast('다운로드할 파일이 없습니다.', 'error');
        return;
    }
    
    // Download each file
    for (const result of successfulResults) {
        const blob = new Blob([result.content], { type: 'text/markdown' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${result.title}_${result.timestamp}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        // Small delay between downloads
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    showToast(`${successfulResults.length}개 파일이 다운로드되었습니다.`, 'success');
}

// Reset and retry
function resetForm() {
    // Reset URL input container to initial state
    urlInputsContainer.innerHTML = `
        <div class="url-input-row" data-index="0">
            <div class="form-group">
                <div class="input-with-buttons">
                    <input 
                        type="url" 
                        id="urlInput-0" 
                        name="urlInput[]"
                        placeholder="https://news.example.com/article"
                        required
                    >
                    <button type="button" class="btn btn-icon add-url-btn" onclick="addUrlInput(0)">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Reset counters
    urlInputCount = 1;
    
    // Hide batch section
    hideBatchSection();
    
    // Reset global variables
    currentJobId = null;
    currentData = null;
    currentBatchJobId = null;
    currentBatchData = null;
    
    // Hide all sections
    hideAllSections();
    
    // Focus on URL input
    document.getElementById('urlInput-0').focus();
    
    // Update button states
    updateUrlInputButtons();
}

function retryGeneration() {
    hideAllSections();
    handleFormSubmit({ preventDefault: () => {} });
}

// Utility functions
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
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showToast('예상치 못한 오류가 발생했습니다.', 'error');
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    showToast('네트워크 오류가 발생했습니다.', 'error');
});

// API Settings Functions
function loadApiSettings() {
    const settings = getApiSettings();
    if (settings) {
        updateApiStatus(settings.provider, true);
        apiProviderSelect.value = settings.provider;
        apiKeyInput.value = settings.key;
    } else {
        updateApiStatus(null, false);
    }
}

function getApiSettings() {
    const settings = localStorage.getItem('nongbuxx_api_settings');
    return settings ? JSON.parse(settings) : null;
}

function saveApiSettings(provider, key) {
    const settings = {
        provider: provider,
        key: key,
        timestamp: Date.now()
    };
    localStorage.setItem('nongbuxx_api_settings', JSON.stringify(settings));
}

function deleteApiSettings() {
    localStorage.removeItem('nongbuxx_api_settings');
}

function updateApiStatus(provider, isConfigured) {
    const statusElement = apiStatus.querySelector('.status-text');
    if (isConfigured) {
        statusElement.textContent = 'AI활성';
        apiStatus.className = 'api-status-simple configured';
    } else {
        statusElement.textContent = 'AI비활성';
        apiStatus.className = 'api-status-simple not-configured';
    }
}

function showApiSettingsSection() {
    hideAllSections();
    apiSettingsSection.style.display = 'block';
    
    // Reset form
    const settings = getApiSettings();
    if (settings) {
        apiProviderSelect.value = settings.provider;
        apiKeyInput.value = settings.key;
    } else {
        apiProviderSelect.value = 'anthropic';
        apiKeyInput.value = '';
    }
    
    // Reset validation result
    apiValidationResult.className = 'api-validation-result';
    apiValidationResult.textContent = '';
    
    // Reset buttons
    saveApiKeyBtn.disabled = true;
    
    apiKeyInput.focus();
}

function hideApiSettingsSection() {
    apiSettingsSection.style.display = 'none';
}

function toggleApiKeyVisibility() {
    const isPassword = apiKeyInput.type === 'password';
    apiKeyInput.type = isPassword ? 'text' : 'password';
    
    const icon = toggleApiKeyBtn.querySelector('i');
    icon.className = isPassword ? 'fas fa-eye-slash' : 'fas fa-eye';
}

function onApiProviderChange() {
    // Reset validation when provider changes
    apiValidationResult.className = 'api-validation-result';
    apiValidationResult.textContent = '';
    saveApiKeyBtn.disabled = true;
    
    // Clear API key when provider changes
    apiKeyInput.value = '';
    
    // Update placeholder
    const placeholder = apiProviderSelect.value === 'anthropic' ? 'sk-ant-...' : 'sk-...';
    apiKeyInput.placeholder = placeholder;
    
    // Focus on API key input for user convenience
    apiKeyInput.focus();
}

function onApiKeyInput() {
    // Reset validation when key changes
    apiValidationResult.className = 'api-validation-result';
    apiValidationResult.textContent = '';
    saveApiKeyBtn.disabled = true;
}

async function validateApiKey() {
    const provider = apiProviderSelect.value;
    const key = apiKeyInput.value.trim();
    
    if (!key) {
        showToast('API 키를 입력해주세요.', 'error');
        return;
    }
    
    // Show loading state
    apiValidationResult.className = 'api-validation-result loading';
    apiValidationResult.innerHTML = '<div class="spinner"></div>API 키 유효성 확인 중...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/validate-api-key`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                api_provider: provider,
                api_key: key
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            apiValidationResult.className = 'api-validation-result success';
            apiValidationResult.textContent = `✓ API 키가 유효합니다 (${data.provider === 'anthropic' ? 'Anthropic Claude' : 'OpenAI GPT-4'})`;
            saveApiKeyBtn.disabled = false;
            showToast('API 키가 유효합니다!', 'success');
        } else {
            apiValidationResult.className = 'api-validation-result error';
            apiValidationResult.textContent = `✗ ${data.error}`;
            saveApiKeyBtn.disabled = true;
            showToast('API 키 유효성 확인에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('API validation error:', error);
        apiValidationResult.className = 'api-validation-result error';
        apiValidationResult.textContent = '✗ 서버 연결에 실패했습니다.';
        saveApiKeyBtn.disabled = true;
        showToast('서버 연결에 실패했습니다.', 'error');
    }
}

function saveApiKey() {
    const provider = apiProviderSelect.value;
    const key = apiKeyInput.value.trim();
    
    if (!key) {
        showToast('API 키를 입력해주세요.', 'error');
        return;
    }
    
    saveApiSettings(provider, key);
    updateApiStatus(provider, true);
    hideApiSettingsSection();
    showToast('API 키가 저장되었습니다!', 'success');
}

function deleteApiKey() {
    if (confirm('저장된 API 키를 삭제하시겠습니까?')) {
        deleteApiSettings();
        updateApiStatus(null, false);
        hideApiSettingsSection();
        
        // Clear form
        apiKeyInput.value = '';
        apiValidationResult.className = 'api-validation-result';
        apiValidationResult.textContent = '';
        
        showToast('API 키가 삭제되었습니다.', 'success');
    }
}

// Service worker registration (optional, for offline support)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(error) {
                console.log('ServiceWorker registration failed');
            });
    });
} 