// Global variables
let currentJobId = null;
let currentData = null;
let currentBatchJobId = null;
let currentBatchData = null;

// DOM elements
const urlForm = document.getElementById('urlForm');
const urlInput = document.getElementById('urlInput');
const apiProvider = document.getElementById('apiProvider');
const customFilename = document.getElementById('customFilename');
const batchBtn = document.getElementById('batchBtn');
const batchSection = document.getElementById('batchSection');
const batchUrls = document.getElementById('batchUrls');
const processBatchBtn = document.getElementById('processBatchBtn');
const cancelBatchBtn = document.getElementById('cancelBatchBtn');
const progressSection = document.getElementById('progressSection');
const progressTitle = document.getElementById('progressTitle');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const resultSection = document.getElementById('resultSection');
const resultTitle = document.getElementById('resultTitle');
const resultTime = document.getElementById('resultTime');
const resultApi = document.getElementById('resultApi');
const markdownPreview = document.getElementById('markdownPreview');
const markdownCode = document.getElementById('markdownCode');
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
    
    // Check if marked.js is loaded
    if (typeof marked === 'undefined') {
        showToast('마크다운 라이브러리를 로드할 수 없습니다.', 'error');
    }
});

// Event listeners
function initEventListeners() {
    // Form submission
    urlForm.addEventListener('submit', handleFormSubmit);
    
    // Batch handling
    batchBtn.addEventListener('click', showBatchSection);
    processBatchBtn.addEventListener('click', handleBatchProcess);
    cancelBatchBtn.addEventListener('click', hideBatchSection);
    
    // Result actions
    downloadBtn.addEventListener('click', downloadFile);
    copyBtn.addEventListener('click', copyToClipboard);
    resetBtn.addEventListener('click', resetForm);
    downloadAllBtn.addEventListener('click', downloadAllFiles);
    resetBatchBtn.addEventListener('click', resetForm);
    retryBtn.addEventListener('click', retryGeneration);
    
    // Tab switching
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            switchTab(this.dataset.tab);
        });
    });
}

// Form submission handler
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const url = urlInput.value.trim();
    const api = apiProvider.value;
    const filename = customFilename.value.trim();
    
    if (!url) {
        showToast('URL을 입력해주세요.', 'error');
        return;
    }
    
    if (!isValidUrl(url)) {
        showToast('올바른 URL을 입력해주세요.', 'error');
        return;
    }
    
    try {
        hideAllSections();
        showProgressSection();
        
        const requestData = {
            url: url,
            api_provider: api,
            save_intermediate: false
        };
        
        if (filename) {
            requestData.filename = filename;
        }
        
        const response = await fetch('/api/generate', {
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
        
    } catch (error) {
        console.error('Error:', error);
        showErrorSection('서버와의 통신에 실패했습니다.');
        showToast('서버 연결에 실패했습니다.', 'error');
    }
}

// Batch processing
function showBatchSection() {
    batchSection.style.display = 'block';
    batchBtn.style.display = 'none';
    batchUrls.focus();
}

function hideBatchSection() {
    batchSection.style.display = 'none';
    batchBtn.style.display = 'inline-flex';
    batchUrls.value = '';
}

async function handleBatchProcess() {
    const urls = batchUrls.value.trim().split('\n').filter(url => url.trim());
    const api = apiProvider.value;
    
    if (urls.length === 0) {
        showToast('URL을 입력해주세요.', 'error');
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
            api_provider: api,
            save_intermediate: false
        };
        
        const response = await fetch('/api/batch', {
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
        'progressSection', 'resultSection', 'batchResultSection', 'errorSection'
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
    
    // Populate result data
    resultTitle.textContent = currentData.title;
    resultTime.textContent = new Date(currentData.timestamp).toLocaleString('ko-KR');
    resultApi.textContent = currentData.api_provider === 'anthropic' ? 'Anthropic Claude' : 'OpenAI GPT-4';
    
    // Populate content
    markdownCode.textContent = currentData.content;
    
    // Render markdown preview
    if (typeof marked !== 'undefined') {
        markdownPreview.innerHTML = marked.parse(currentData.content);
    } else {
        markdownPreview.innerHTML = '<p>마크다운 미리보기를 로드할 수 없습니다.</p>';
    }
    
    // Show preview tab by default
    switchTab('preview');
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
    errorMessage.textContent = message;
}

// Tab switching
function switchTab(tabName) {
    // Update tab buttons
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });
    
    // Update tab content
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
        if (content.id === tabName + 'Tab') {
            content.classList.add('active');
        }
    });
}

// File operations
async function downloadFile() {
    if (!currentJobId) {
        showToast('다운로드할 파일이 없습니다.', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/api/download/${currentJobId}`);
        
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
    // Reset form
    urlForm.reset();
    hideBatchSection();
    
    // Reset global variables
    currentJobId = null;
    currentData = null;
    currentBatchJobId = null;
    currentBatchData = null;
    
    // Hide all sections
    hideAllSections();
    
    // Focus on URL input
    urlInput.focus();
}

function retryGeneration() {
    hideAllSections();
    if (batchSection.style.display === 'block') {
        handleBatchProcess();
    } else {
        handleFormSubmit({ preventDefault: () => {} });
    }
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