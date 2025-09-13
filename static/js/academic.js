// Sentino AI Academic Research Platform JavaScript

class AcademicResearchApp {
    constructor() {
        this.currentQuery = '';
        this.currentPapers = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadTrendingTopics();
    }

    bindEvents() {
        // Search form submission
        const searchForm = document.getElementById('academicSearchForm');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.performSearch();
            });
        }

        // Modal close events
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target.id);
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    async performSearch() {
        const query = document.getElementById('searchQuery').value.trim();
        const maxResults = document.getElementById('maxResults').value;
        const sortBy = document.getElementById('sortBy').value;
        const includeScihub = document.getElementById('includeScihub').checked;

        if (!query) {
            this.showError('Please enter a search query');
            return;
        }

        // Add loading animation to search button
        const searchButton = document.querySelector('.search-btn');
        const originalText = searchButton.innerHTML;
        searchButton.innerHTML = `
            <div class="loading-spinner"></div>
            <span class="loading-text">Searching...</span>
        `;
        searchButton.disabled = true;

        this.currentQuery = query;
        this.showLoading(true);

        try {
            const response = await fetch('/api/academic-search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    max_results: parseInt(maxResults),
                    sort_by: sortBy,
                    include_scihub: includeScihub
                })
            });

            const data = await response.json();

            if (data.success) {
                this.currentPapers = data.papers;
                this.displayResults(data);
                this.showResearchSuggestionsButton();
            } else {
                this.showError(data.error || 'Search failed');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Network error occurred');
        } finally {
            this.showLoading(false);
            // Restore search button
            searchButton.innerHTML = originalText;
            searchButton.disabled = false;
        }
    }

    displayResults(data) {
        // Show results section
        document.getElementById('resultsSection').style.display = 'block';
        document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });

        // Store search results for draft generator
        window.currentSearchResults = data.papers || [];

        // Display AI analysis
        const analysisContent = document.getElementById('analysisContent');
        if (data.analysis) {
            analysisContent.innerHTML = this.formatAnalysis(data.analysis);
        } else {
            analysisContent.innerHTML = '<p class="text-muted">No analysis available</p>';
        }

        // Display stats
        this.displayStats(data.scihub_stats);

        // Display papers
        this.displayPapers(data.papers);

        // Show advanced analysis tools
        document.getElementById('analysisTools').style.display = 'block';
    }

    displayStats(stats) {
        document.getElementById('totalPapers').textContent = stats.total_papers || 0;
        document.getElementById('scihubAvailable').textContent = stats.available_on_scihub || 0;
        document.getElementById('availabilityRate').textContent = 
            Math.round((stats.availability_rate || 0) * 100) + '%';
    }

    displayPapers(papers) {
        const papersList = document.getElementById('papersList');
        
        if (!papers || papers.length === 0) {
            papersList.innerHTML = '<p class="text-muted">No papers found for your query.</p>';
            return;
        }

        // Clear existing papers
        papersList.innerHTML = '';
        
        // Add papers with staggered animation
        papers.forEach((paper, index) => {
            const paperElement = document.createElement('div');
            paperElement.innerHTML = this.createPaperCard(paper);
            const paperCard = paperElement.firstElementChild;
            
            // Set CSS custom property for animation delay
            paperCard.style.setProperty('--paper-index', index);
            paperCard.style.opacity = '0';
            paperCard.style.transform = 'translateY(30px)';
            
            papersList.appendChild(paperCard);
            
            // Trigger animation with delay
            setTimeout(() => {
                paperCard.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                paperCard.style.opacity = '1';
                paperCard.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    createPaperCard(paper) {
        // Enhanced Sci-Hub status with direct links
        const scihubContent = paper.scihub_available ? 
            `<div class="scihub-section scihub-available">
                <div class="scihub-status">
                    <i class="fas fa-check-circle"></i>
                    <span>Available on Sci-Hub</span>
                </div>
                <div class="scihub-links">
                    <a href="${paper.scihub_pdf_url}" target="_blank" class="scihub-direct-link">
                        <i class="fas fa-external-link-alt"></i> Open in Sci-Hub
                    </a>
                    ${paper.doi ? `<a href="https://sci-hub.se/${paper.doi}" target="_blank" class="scihub-page-link">
                        <i class="fas fa-globe"></i> Sci-Hub Page
                    </a>` : ''}
                    <button class="scihub-download-btn" onclick="app.downloadFromScihub('${paper.scihub_pdf_url}', '${this.escapeHtml(paper.title)}.pdf')">
                        <i class="fas fa-download"></i> Download PDF
                    </button>
                </div>
            </div>` :
            `<div class="scihub-section scihub-unavailable">
                <div class="scihub-status">
                    <i class="fas fa-times-circle"></i>
                    <span>Not available on Sci-Hub</span>
                </div>
                <div class="scihub-alternative">
                    <a href="https://sci-hub.se/${encodeURIComponent(paper.title)}" target="_blank" class="scihub-search-link">
                        <i class="fas fa-search"></i> Search on Sci-Hub
                    </a>
                    ${paper.doi ? `<a href="https://sci-hub.se/${paper.doi}" target="_blank" class="scihub-search-link">
                        <i class="fas fa-external-link-alt"></i> Try DOI on Sci-Hub
                    </a>` : ''}
                </div>
            </div>`;

        const categories = paper.categories && paper.categories.length > 0 ? 
            paper.categories.map(cat => `<span class="category-tag">${cat}</span>`).join('') : '';

        return `
            <div class="paper-item">
                <div class="paper-header">
                    <div class="paper-info">
                        <h4 class="paper-title">
                            <a href="${paper.url}" target="_blank">${paper.title}</a>
                        </h4>
                        <div class="paper-meta">
                            <span class="paper-authors">${paper.authors}</span>
                            <span class="paper-date">${paper.published}</span>
                            <span class="paper-source">${paper.source}</span>
                        </div>
                        ${categories ? `<div class="paper-categories">${categories}</div>` : ''}
                    </div>
                    ${scihubContent}
                </div>
                
                <p class="paper-summary">${this.truncateText(paper.summary, 300)}</p>
                
                <div class="paper-actions">
                    <a href="${paper.url}" target="_blank" class="btn-outline">
                        <i class="fas fa-external-link-alt"></i> View Original
                    </a>
                    <button class="btn-primary" onclick="app.analyzePaper('${this.escapeHtml(paper.title)}', '${this.escapeHtml(paper.summary)}', '${this.escapeHtml(paper.authors)}', '${paper.published_year || ''}', ${JSON.stringify(paper.categories || [])})">
                        <i class="fas fa-microscope"></i> AI Analysis
                    </button>
                </div>
            </div>
        `;
    }

    async analyzePaper(title, abstract, authors, year = '', categories = []) {
        this.showModal('paperAnalysisModal');
        
        document.getElementById('modalPaperTitle').textContent = title;
        document.getElementById('modalAnalysisContent').innerHTML = '<div class="loading">Conducting comprehensive analysis...</div>';

        try {
            const response = await fetch('/api/paper-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title,
                    abstract: abstract,
                    authors: authors,
                    year: year,
                    categories: categories
                })
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById('modalAnalysisContent').innerHTML = this.formatAnalysis(data.analysis);
            } else {
                document.getElementById('modalAnalysisContent').innerHTML = 
                    '<p class="error">Failed to analyze paper</p>';
            }
        } catch (error) {
            console.error('Analysis error:', error);
            document.getElementById('modalAnalysisContent').innerHTML = 
                '<p class="error">Network error occurred</p>';
        }
    }

    async generateLiteratureReview() {
        if (!this.currentPapers || this.currentPapers.length === 0) {
            this.showError('No papers available for literature review');
            return;
        }

        this.showModal('literatureReviewModal');
        const reviewType = document.getElementById('reviewType').value;
        const citationFormat = document.getElementById('citationFormat').value;
        
        document.getElementById('reviewContent').innerHTML = '<div class="loading">Generating comprehensive literature review...</div>';

        try {
            const response = await fetch('/api/literature-review', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    papers: this.currentPapers,
                    query: this.currentQuery,
                    review_type: reviewType,
                    citation_format: citationFormat
                })
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById('reviewContent').innerHTML = this.formatAnalysis(data.literature_review);
                this.currentReview = data.literature_review;
            } else {
                document.getElementById('reviewContent').innerHTML = 
                    '<p class="error">Failed to generate literature review</p>';
            }
        } catch (error) {
            console.error('Literature review error:', error);
            document.getElementById('reviewContent').innerHTML = 
                '<p class="error">Network error occurred</p>';
        }
    }

    showMethodologyAnalysis() {
        this.showModal('methodologyModal');
        document.getElementById('methodologyResearchQuestion').value = this.currentQuery || '';
        document.getElementById('methodologyContent').style.display = 'none';
        document.getElementById('methodologyActions').style.display = 'none';
    }

    async generateMethodologyAnalysis() {
        const researchQuestion = document.getElementById('methodologyResearchQuestion').value.trim();
        const researchType = document.getElementById('researchType').value;
        const citationFormat = document.getElementById('methodologyCitationFormat').value;

        if (!researchQuestion) {
            this.showError('Please enter a research question');
            return;
        }

        document.getElementById('methodologyContent').style.display = 'block';
        document.getElementById('methodologyContent').innerHTML = '<div class="loading">Analyzing methodological approaches...</div>';

        try {
            const response = await fetch('/api/methodology-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    research_question: researchQuestion,
                    papers: this.currentPapers || [],
                    research_type: researchType,
                    citation_format: citationFormat
                })
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById('methodologyContent').innerHTML = this.formatAnalysis(data.methodology_analysis);
                document.getElementById('methodologyActions').style.display = 'block';
                this.currentMethodology = data.methodology_analysis;
            } else {
                document.getElementById('methodologyContent').innerHTML = 
                    '<p class="error">Failed to generate methodology analysis</p>';
            }
        } catch (error) {
            console.error('Methodology analysis error:', error);
            document.getElementById('methodologyContent').innerHTML = 
                '<p class="error">Network error occurred</p>';
        }
    }

    async showResearchFramework() {
        if (!this.currentQuery) {
            this.showError('No active search query for framework generation');
            return;
        }

        this.showModal('researchFrameworkModal');
        document.getElementById('frameworkContent').innerHTML = '<div class="loading">Generating research framework...</div>';

        // Use the enhanced research suggestions endpoint for framework
        try {
            const response = await fetch('/api/research-suggestions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: this.currentQuery
                })
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById('frameworkContent').innerHTML = this.formatAnalysis(data.suggestions);
                this.currentFramework = data.suggestions;
            } else {
                document.getElementById('frameworkContent').innerHTML = 
                    '<p class="error">Failed to generate research framework</p>';
            }
        } catch (error) {
            console.error('Research framework error:', error);
            document.getElementById('frameworkContent').innerHTML = 
                '<p class="error">Network error occurred</p>';
        }
    }

    exportReview() {
        if (!this.currentReview) {
            this.showError('No literature review to export');
            return;
        }
        
        // Create a simple text file for now - could be enhanced to generate Word doc
        const blob = new Blob([this.currentReview], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `literature_review_${this.currentQuery.replace(/\s+/g, '_')}.txt`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    copyReview() {
        if (!this.currentReview) {
            this.showError('No literature review to copy');
            return;
        }
        
        navigator.clipboard.writeText(this.currentReview).then(() => {
            // Could show a success message
            alert('Literature review copied to clipboard!');
        }).catch(() => {
            this.showError('Failed to copy to clipboard');
        });
    }

    exportMethodology() {
        if (!this.currentMethodology) {
            this.showError('No methodology analysis to export');
            return;
        }
        
        const blob = new Blob([this.currentMethodology], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `methodology_analysis_${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    async showResearchSuggestions() {
        if (!this.currentQuery) {
            this.showError('No active search query');
            return;
        }

        this.showModal('suggestionsModal');
        document.getElementById('suggestionsContent').innerHTML = '<div class="loading">Generating suggestions...</div>';

        try {
            const response = await fetch('/api/research-suggestions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: this.currentQuery
                })
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById('suggestionsContent').innerHTML = this.formatAnalysis(data.suggestions);
            } else {
                document.getElementById('suggestionsContent').innerHTML = 
                    '<p class="error">Failed to generate suggestions</p>';
            }
        } catch (error) {
            console.error('Suggestions error:', error);
            document.getElementById('suggestionsContent').innerHTML = 
                '<p class="error">Network error occurred</p>';
        }
    }

    showResearchSuggestionsButton() {
        // Add suggestions button to analysis panel if it doesn't exist
        const analysisPanel = document.getElementById('analysisPanel');
        if (!analysisPanel.querySelector('.suggestions-btn')) {
            const button = document.createElement('button');
            button.className = 'btn-outline suggestions-btn';
            button.innerHTML = '<i class="fas fa-lightbulb"></i> Get Research Suggestions';
            button.onclick = () => this.showResearchSuggestions();
            analysisPanel.appendChild(button);
        }
    }

    async downloadFromScihub(pdfUrl, filename) {
        try {
            const response = await fetch('/api/scihub/download-paper', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    pdf_url: pdfUrl,
                    filename: filename
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                this.showError('Failed to download paper');
            }
        } catch (error) {
            console.error('Download error:', error);
            this.showError('Network error occurred');
        }
    }

    async loadTrendingTopics() {
        // This could be called periodically or on demand
        try {
            const response = await fetch('/api/trending-topics');
            const data = await response.json();
            
            if (data.success) {
                this.trendingData = data.trending;
            }
        } catch (error) {
            console.error('Error loading trending topics:', error);
        }
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            modal.classList.add('show');
            
            // Add entrance animation
            const modalContent = modal.querySelector('.modal-content');
            if (modalContent) {
                modalContent.style.transform = 'scale(0.7) translateY(-50px)';
                modalContent.style.opacity = '0';
                
                setTimeout(() => {
                    modalContent.style.transition = 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
                    modalContent.style.transform = 'scale(1) translateY(0)';
                    modalContent.style.opacity = '1';
                }, 10);
            }
            
            // Prevent body scroll
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            const modalContent = modal.querySelector('.modal-content');
            
            if (modalContent) {
                modalContent.style.transition = 'all 0.2s ease-in-out';
                modalContent.style.transform = 'scale(0.9) translateY(-20px)';
                modalContent.style.opacity = '0';
                
                setTimeout(() => {
                    modal.classList.remove('show');
                    modal.style.display = 'none';
                    document.body.style.overflow = 'auto';
                }, 200);
            } else {
                modal.classList.remove('show');
                modal.style.display = 'none';
                document.body.style.overflow = 'auto';
            }
        }
    }

    closeAllModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => modal.classList.remove('show'));
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) {
            overlay.classList.add('show');
        } else {
            overlay.classList.remove('show');
        }
    }

    showError(message) {
        // Simple error display - could be enhanced with a toast notification
        alert('Error: ' + message);
    }

    downloadFromScihub(pdfUrl, filename) {
        if (!pdfUrl) {
            this.showError('No Sci-Hub PDF URL available');
            return;
        }

        try {
            // Create a temporary link element for download
            const link = document.createElement('a');
            link.href = pdfUrl;
            link.target = '_blank';
            link.download = filename || 'paper.pdf';
            
            // Add visual feedback
            const downloadBtn = event.target;
            const originalText = downloadBtn.innerHTML;
            downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';
            downloadBtn.disabled = true;
            
            // Trigger download
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // Restore button after delay
            setTimeout(() => {
                downloadBtn.innerHTML = originalText;
                downloadBtn.disabled = false;
            }, 2000);
            
        } catch (error) {
            console.error('Download error:', error);
            this.showError('Failed to download paper');
        }
    }

    formatAnalysis(text) {
        if (!text) return '<div class="markdown-content"><p class="text-muted">No analysis available</p></div>';
        
        // Enhanced markdown-like formatting to HTML
        let formatted = text
            // Headers
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')
            // Bold and italic
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Lists - handle bullet points and numbered lists
            .replace(/^\* (.*$)/gm, '<li>$1</li>')
            .replace(/^- (.*$)/gm, '<li>$1</li>')
            .replace(/^\d+\. (.*$)/gm, '<li>$1</li>')
            // Code blocks
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            // Links
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
            // Horizontal rules
            .replace(/^---$/gm, '<hr>')
            // Blockquotes
            .replace(/^> (.*$)/gm, '<blockquote>$1</blockquote>')
            // Line breaks and paragraphs
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>')
            .replace(/<p><\/p>/g, '');
        
        // Wrap consecutive list items in ul tags
        formatted = formatted.replace(/(<li>.*?<\/li>(\s*<br>\s*<li>.*?<\/li>)*)/g, function(match) {
            return '<ul>' + match.replace(/<br>\s*/g, '') + '</ul>';
        });
        
        // Clean up nested ul tags
        formatted = formatted.replace(/<\/ul>\s*<ul>/g, '');
        
        // Wrap in markdown-content container
        return `<div class="markdown-content">${formatted}</div>`;
    }

    truncateText(text, maxLength) {
        if (!text || text.length <= maxLength) return text;
        return text.substr(0, maxLength) + '...';
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML.replace(/'/g, '&#39;');
    }
}

// Global functions for onclick handlers
function showTrendingTopics() {
    app.showModal('trendingModal');
    
    const content = document.getElementById('trendingContent');
    if (app.trendingData) {
        content.innerHTML = app.trendingData.map(category => `
            <div class="trending-category">
                <h4>${category.category}</h4>
                <ul>
                    ${category.papers.map(paper => `
                        <li><a href="${paper.url}" target="_blank">${paper.title}</a></li>
                    `).join('')}
                </ul>
            </div>
        `).join('');
    } else {
        content.innerHTML = '<div class="loading">Loading trending topics...</div>';
        app.loadTrendingTopics().then(() => {
            if (app.trendingData) {
                showTrendingTopics(); // Recursive call to update content
            }
        });
    }
}

async function showSciHubStatus() {
    app.showModal('scihubStatusModal');
    
    const content = document.getElementById('statusContent');
    content.innerHTML = '<div class="loading">Checking mirror status...</div>';
    
    try {
        const response = await fetch('/api/scihub/mirror-status');
        const data = await response.json();
        
        if (data.success) {
            content.innerHTML = `
                <div class="status-info">
                    <p><strong>Active Mirror:</strong> ${data.active_mirror || 'None'}</p>
                    <h4>Mirror Status:</h4>
                    <ul>
                        ${data.mirrors.map(mirror => `
                            <li class="${mirror.status === 'active' ? 'status-active' : 'status-inactive'}">
                                ${mirror.url} - ${mirror.status}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        } else {
            content.innerHTML = '<p class="error">Failed to check mirror status</p>';
        }
    } catch (error) {
        console.error('Status check error:', error);
        content.innerHTML = '<p class="error">Network error occurred</p>';
    }
}

function closeModal(modalId) {
    app.closeModal(modalId);
}

function generateLiteratureReview() {
    app.generateLiteratureReview();
}

function showMethodologyAnalysis() {
    app.showMethodologyAnalysis();
}

function generateMethodologyAnalysis() {
    app.generateMethodologyAnalysis();
}

function showResearchFramework() {
    app.showResearchFramework();
}

function exportReview() {
    app.exportReview();
}

function copyReview() {
    app.copyReview();
}

function exportMethodology() {
    app.exportMethodology();
}

function updateReviewType() {
    // Regenerate review with new type if content exists
    if (app.currentPapers && app.currentPapers.length > 0) {
        app.generateLiteratureReview();
    }
}

function updateCitationFormat() {
    // Regenerate review with new citation format if content exists
    if (app.currentPapers && app.currentPapers.length > 0) {
        app.generateLiteratureReview();
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new AcademicResearchApp();
});

// =============================================================================
// DRAFT GENERATOR FUNCTIONS
// =============================================================================

function showDraftGenerator() {
    showModal('draftGeneratorModal');
    
    // Reset form to initial state
    showDraftForm();
}

function showModal(modalId) {
    app.showModal(modalId);
}

function showDraftForm() {
    document.getElementById('draftForm').style.display = 'flex';
    document.getElementById('draftResult').style.display = 'none';
    document.getElementById('draftLoading').style.display = 'none';
}

function generateAcademicDraft() {
    // Get form values
    const researchTitle = document.getElementById('researchTitle').value.trim();
    const researchQuestion = document.getElementById('researchQuestion').value.trim();
    const researchField = document.getElementById('researchField').value.trim();
    const researchType = document.getElementById('researchType').value;
    const citationFormat = document.getElementById('draftCitationFormat').value;
    
    // DEBUG: Console log all form values
    console.log('=== DRAFT FORM DEBUG ===');
    console.log('Research Title raw:', document.getElementById('researchTitle').value);
    console.log('Research Title trimmed:', researchTitle);
    console.log('Research Title length:', researchTitle.length);
    console.log('Research Title empty check:', !researchTitle);
    console.log('Research Question raw:', document.getElementById('researchQuestion').value);
    console.log('Research Question trimmed:', researchQuestion);
    console.log('Research Question length:', researchQuestion.length);
    console.log('Research Question empty check:', !researchQuestion);
    console.log('Form elements exist:');
    console.log('- researchTitle element:', document.getElementById('researchTitle'));
    console.log('- researchQuestion element:', document.getElementById('researchQuestion'));
    console.log('========================');
    
    // Get selected sections
    const includeSections = {
        introduction: document.getElementById('includeIntroduction').checked,
        literature_review: document.getElementById('includeLiteratureReview').checked,
        methodology: document.getElementById('includeMethodology').checked,
        conclusion: document.getElementById('includeConclusion').checked,
        future_works: document.getElementById('includeFutureWorks').checked
    };
    
    // Validation
    if (!researchTitle || !researchQuestion) {
        console.error('VALIDATION FAILED:');
        console.error('- Research Title is empty:', !researchTitle);
        console.error('- Research Question is empty:', !researchQuestion);
        alert('Please fill in the required fields: Research Title and Research Question');
        return;
    }
    
    // Show loading state
    document.getElementById('draftForm').style.display = 'none';
    document.getElementById('draftResult').style.display = 'none';
    document.getElementById('draftLoading').style.display = 'flex';
    
    // Get current papers from the search results
    const papers = window.currentSearchResults || [];
    
    // Prepare request data
    const requestData = {
        research_title: researchTitle,
        research_question: researchQuestion,
        research_field: researchField || 'Academic Research',
        research_type: researchType,
        citation_format: citationFormat,
        include_sections: includeSections,
        papers: papers
    };
    
    // Make API request
    fetch('/api/generate-draft', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayDraftResult(data);
        } else {
            throw new Error(data.error || 'Failed to generate draft');
        }
    })
    .catch(error => {
        console.error('Draft generation error:', error);
        alert('Failed to generate draft: ' + error.message);
        showDraftForm();
    });
}

function displayDraftResult(data) {
    // Hide loading, show result
    document.getElementById('draftLoading').style.display = 'none';
    document.getElementById('draftResult').style.display = 'block';
    
    // Format and display the draft content
    const draftContent = document.getElementById('draftContent');
    draftContent.innerHTML = formatAnalysis(data.draft);
    
    // Store draft data for export
    window.currentDraft = {
        title: data.research_title,
        content: data.draft,
        citationFormat: data.citation_format,
        timestamp: data.timestamp,
        sectionsIncluded: data.sections_included,
        papersCount: data.papers_count
    };
    
    // Scroll to top of modal content
    const modalContent = document.querySelector('#draftGeneratorModal .modal-content');
    modalContent.scrollTop = 0;
}

function copyDraft() {
    if (!window.currentDraft) {
        alert('No draft to copy');
        return;
    }
    
    const textToCopy = `# ${window.currentDraft.title}\n\n${window.currentDraft.content}`;
    
    navigator.clipboard.writeText(textToCopy).then(() => {
        // Show success feedback
        const btn = event.target.closest('button');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        btn.style.background = 'var(--success-color)';
        
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.style.background = '';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy to clipboard');
    });
}

function exportDraft() {
    if (!window.currentDraft) {
        alert('No draft to export');
        return;
    }
    
    const draft = window.currentDraft;
    
    // Create export content with metadata
    const exportContent = `# ${draft.title}

**Generated:** ${new Date(draft.timestamp).toLocaleString()}
**Citation Format:** ${draft.citationFormat.toUpperCase()}
**Papers Referenced:** ${draft.papersCount}
**Sections:** ${Object.entries(draft.sectionsIncluded)
    .filter(([_, included]) => included)
    .map(([section, _]) => section.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()))
    .join(', ')}

---

${draft.content}`;
    
    // Create and download file
    const blob = new Blob([exportContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${draft.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_draft.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    // Show success feedback
    const btn = event.target.closest('button');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-check"></i> Exported!';
    btn.style.background = 'var(--success-color)';
    
    setTimeout(() => {
        btn.innerHTML = originalText;
        btn.style.background = '';
    }, 2000);
}

// Add some additional CSS for status indicators
const additionalStyles = `
    <style>
        .trending-category {
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border-color);
        }
        
        .trending-category:last-child {
            border-bottom: none;
        }
        
        .trending-category h4 {
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }
        
        .trending-category ul {
            list-style: none;
            padding: 0;
        }
        
        .trending-category li {
            margin-bottom: 0.25rem;
        }
        
        .trending-category a {
            color: var(--text-secondary);
            text-decoration: none;
        }
        
        .trending-category a:hover {
            color: var(--primary-color);
            text-decoration: underline;
        }
        
        .status-info ul {
            list-style: none;
            padding: 0;
        }
        
        .status-info li {
            padding: 0.5rem;
            margin: 0.25rem 0;
            border-radius: 4px;
        }
        
        .status-active {
            background: #dcfce7;
            color: #166534;
        }
        
        .status-inactive {
            background: #fef2f2;
            color: #991b1b;
        }
        
        .error {
            color: #dc2626;
            font-style: italic;
        }
        
        .suggestions-btn {
            margin-top: 1rem;
            width: 100%;
            justify-content: center;
        }
    </style>
`;

document.head.insertAdjacentHTML('beforeend', additionalStyles);
