document.addEventListener("DOMContentLoaded", function () {
    // DOM elements
    const themeSwitcher = document.getElementById('themeSwitcher');
    const clearResults = document.getElementById('clearResults');
    const navLinks = document.querySelectorAll('.nav-link');
    const featureCards = document.querySelectorAll('.feature-card');
    
    // View containers
    const welcomeView = document.getElementById('welcome-view');
    const searchView = document.getElementById('search-view');
    const deepAnalysisView = document.getElementById('deep-analysis-view');
    const academicView = document.getElementById('academic-view');
    
    // Form elements
    const searchForm = document.getElementById('searchForm');
    const deepAnalysisForm = document.getElementById('deepAnalysisForm');
    const academicForm = document.getElementById('academicForm');
    
    // Result containers
    const searchResults = document.getElementById('searchResults');
    const deepAnalysisResults = document.getElementById('deepAnalysisResults');
    const academicResults = document.getElementById('academicResults');

    // Theme handling
    const themes = ['classic', 'amber', 'blue'];
    let currentThemeIndex = 0;

    // Load saved theme from local storage
    if (localStorage.getItem('theme')) {
        document.documentElement.setAttribute('data-theme', localStorage.getItem('theme'));
        currentThemeIndex = themes.indexOf(localStorage.getItem('theme'));
    }

    // Handle theme switching
    themeSwitcher.addEventListener('click', () => {
        currentThemeIndex = (currentThemeIndex + 1) % themes.length;
        const newTheme = themes[currentThemeIndex];
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });

    // Clear results button
    clearResults.addEventListener('click', () => {
        searchResults.innerHTML = '';
        deepAnalysisResults.innerHTML = '';
        academicResults.innerHTML = '';
    });

    // Navigation handling
    function showView(viewId) {
        // Hide all views
        welcomeView.style.display = 'none';
        searchView.style.display = 'none';
        deepAnalysisView.style.display = 'none';
        academicView.style.display = 'none';
        
        // Deactivate all nav links
        navLinks.forEach(link => link.classList.remove('active'));
        
        // Show selected view and activate its nav link
        if (viewId === 'welcome') {
            welcomeView.style.display = 'block';
        } else {
            document.getElementById(`${viewId}-view`).style.display = 'block';
            document.querySelector(`.nav-link[data-view="${viewId}"]`).classList.add('active');
            
            // Save last active view to localStorage
            localStorage.setItem('lastView', viewId);
        }
    }
    
    // Navigation event listeners
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const viewId = link.getAttribute('data-view');
            showView(viewId);
        });
    });
    
    // Feature card event listeners
    featureCards.forEach(card => {
        card.addEventListener('click', () => {
            const viewId = card.getAttribute('data-target');
            showView(viewId);
        });
    });
    
    // Form submissions
    if (searchForm) {
        searchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = document.getElementById('searchInput').value.trim();
            if (!query) return;
            await handleSearch(query, searchResults, '/api/query', false, 'quick');
        });
    }
    
    if (deepAnalysisForm) {
        deepAnalysisForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = document.getElementById('deepAnalysisInput').value.trim();
            if (!query) return;
            await handleSearch(query, deepAnalysisResults, '/api/query', true, 'deep');
        });
    }
    
    if (academicForm) {
        academicForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = document.getElementById('academicInput').value.trim();
            if (!query) return;
            const maxPapers = document.getElementById('maxPapers').value;
            await handleAcademicSearch(query, maxPapers, academicResults);
        });
    }
    
    // API request handlers
    async function handleSearch(query, resultsContainer, endpoint, isDeepAnalysis = false, searchType = 'quick') {
        showLoading(resultsContainer);
        
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    query,
                    enable_deep_analysis: isDeepAnalysis
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `API error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            renderSearchResults(data, resultsContainer, query, searchType);
            
        } catch (err) {
            console.error("Error processing request:", err);
            showError(resultsContainer, err.message);
        }
    }
    
    async function handleAcademicSearch(query, maxPapers, resultsContainer) {
        showLoading(resultsContainer, 'Searching academic papers on arXiv...');
        
        try {
            const response = await fetch('/api/deep-research', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    query,
                    max_papers: parseInt(maxPapers)
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `API error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            renderAcademicResults(data, resultsContainer, query);
            
        } catch (err) {
            console.error("Error processing academic request:", err);
            showError(resultsContainer, err.message, true);
        }
    }
    
    // UI Rendering Functions
    function showLoading(container, message = 'Processing your request...') {
        container.innerHTML = `
            <div class="spinner-container">
                <div class="spinner"></div>
                <p>${message}</p>
                <p class="loading-info">This may take a moment depending on the complexity of the query</p>
            </div>
        `;
    }
    
    function showError(container, message, isAcademic = false) {
        container.innerHTML = `
            <div class="error-container">
                <h2>Error</h2>
                <p>${escapeHtml(message)}</p>
                ${isAcademic ? 
                    '<p>The arXiv search feature may be experiencing issues. Please try again with a more specific query or use regular search.</p>' : 
                    ''}
            </div>
        `;
    }
    
    function renderSearchResults(data, container, originalQuery, searchType) {
        let html = `
            <div class="results-header">
                <h2>Results for: ${escapeHtml(data.query || "N/A")}</h2>
                <div class="results-actions">
                    <button onclick="addFavorite('${escapeHtml(originalQuery)}', '${searchType}')">Save to Favorites</button>
                </div>
            </div>
            <div class="results-body">
                <div class="answer-container">
                    <h2>AI Answer</h2>
                    <div>${marked.parse(data.answer || "No answer available.")}</div>
                </div>
        `;
        
        // If search results exist, display them
        if (data.search_results && data.search_results.length > 0) {
            html += `<h3>Search Results</h3><ul class="search-results-list">`;
            data.search_results.forEach(result => {
                html += `<li class="search-result-item">
                    <strong>${escapeHtml(result.title || "No title")}</strong>
                    <p>${escapeHtml(result.body || "No snippet available")}</p>
                    <a href="${result.href}" target="_blank" rel="noopener noreferrer">${result.href}</a>
                </li>`;
            });
            html += `</ul>`;
        }
        
        html += `</div>`;
        container.innerHTML = html;
    }
    
    function renderAcademicResults(data, container, originalQuery) {
        let html = `
            <div class="results-header">
                <h2>Academic Research: ${escapeHtml(data.query || "N/A")}</h2>
                <div class="results-actions">
                    <button onclick="addFavorite('${escapeHtml(originalQuery)}', 'academic')">Save to Favorites</button>
                </div>
            </div>
            <div class="results-body">
                <div class="academic-analysis">
                    ${marked.parse(data.answer || "No analysis available.")}
                </div>
        `;
        
        // If papers exist, display them
        if (data.papers && data.papers.length > 0) {
            html += `
                <div class="papers-container">
                    <h3>Academic Papers</h3>
                    <div class="paper-list">
            `;
            
            data.papers.forEach(paper => {
                html += `
                <div class="paper-item">
                    <div class="paper-title">${escapeHtml(paper.title)}</div>
                    <div class="paper-authors">Authors: ${escapeHtml(paper.authors)}</div>
                    <div>Published: ${escapeHtml(paper.published)}</div>
                    <div class="paper-summary">${escapeHtml(paper.summary.substring(0, 200))}${paper.summary.length > 200 ? '...' : ''}</div>
                    <a class="paper-link" href="${paper.pdf_url}" target="_blank">View PDF</a>
                </div>`;
            });
            
            html += `</div></div>`;
        }
        
        html += `</div>`;
        container.innerHTML = html;
    }
    
    // Check for URL parameters to handle searches from history/favorites
    const urlParams = new URLSearchParams(window.location.search);
    const prefilledQuery = urlParams.get('query');
    const searchType = urlParams.get('type');
    
    if (prefilledQuery && searchType) {
        // Handle the search based on the type
        switch (searchType) {
            case 'deep':
                document.querySelector('.nav-link[data-view="deep-analysis"]').click();
                document.getElementById('deepAnalysisInput').value = prefilledQuery;
                setTimeout(() => {
                    document.getElementById('deepAnalysisForm').dispatchEvent(new Event('submit'));
                }, 100);
                break;
            
            case 'academic':
                document.querySelector('.nav-link[data-view="academic"]').click();
                document.getElementById('academicInput').value = prefilledQuery;
                setTimeout(() => {
                    document.getElementById('academicForm').dispatchEvent(new Event('submit'));
                }, 100);
                break;
            
            default: // 'quick' or any other value
                document.querySelector('.nav-link[data-view="search"]').click();
                document.getElementById('searchInput').value = prefilledQuery;
                setTimeout(() => {
                    document.getElementById('searchForm').dispatchEvent(new Event('submit'));
                }, 100);
        }
        
        // Clean the URL without reloading the page
        window.history.replaceState({}, document.title, window.location.pathname);
    } else {
        // Initialize: load last active view or default to welcome
        const lastView = localStorage.getItem('lastView');
        if (lastView) {
            showView(lastView);
        } else {
            showView('welcome');
        }
    }
});

// Helper function to escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const element = document.createElement("div");
    element.innerText = text;
    return element.innerHTML;
}
