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
        // Debug log to see paper structure
        console.log("Academic papers data:", data.papers);
        
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
            
            // Add Visualization Section
            html += `
                <div class="viz-container">
                    <div class="viz-header">
                        <div class="viz-title">Research Visualizations</div>
                        <div class="viz-actions">
                            <button class="viz-button" id="exportViz">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                    <polyline points="7 10 12 15 17 10"></polyline>
                                    <line x1="12" y1="15" x2="12" y2="3"></line>
                                </svg>
                                Export
                            </button>
                        </div>
                    </div>
                    <div class="viz-tabs">
                        <div class="viz-tab active" data-viz="network">Citation Network</div>
                        <div class="viz-tab" data-viz="timeline">Research Timeline</div>
                        <div class="viz-tab" data-viz="authors">Author Collaboration</div>
                    </div>
                    <div class="viz-content">
                        <div class="viz-loading">
                            <div class="spinner"></div>
                            <span>Loading visualization...</span>
                        </div>
                    </div>
                    <div class="viz-description">
                        <p>This visualization helps you understand relationships between papers based on their citations. Hover over elements to see detailed information.</p>
                    </div>
                </div>
            `;
        }
        
        html += `</div>`;
        container.innerHTML = html;
        
        // If papers exist, load visualizations
        if (data.papers && data.papers.length > 0) {
            loadVisualization('network', data.papers);
            
            // Add event listeners for visualization tabs
            document.querySelectorAll('.viz-tab').forEach(tab => {
                tab.addEventListener('click', () => {
                    // Update active tab
                    document.querySelectorAll('.viz-tab').forEach(t => t.classList.remove('active'));
                    tab.classList.add('active');
                    
                    // Load the corresponding visualization
                    const vizType = tab.getAttribute('data-viz');
                    loadVisualization(vizType, data.papers);
                    
                    // Update description
                    const descriptions = {
                        'network': 'This visualization helps you understand relationships between papers based on their citations. Hover over elements to see detailed information.',
                        'timeline': 'This timeline shows the progression of research on this topic over time. Explore how the field has evolved.',
                        'authors': 'This network displays collaboration relationships between authors. Larger nodes represent authors with more papers.'
                    };
                    document.querySelector('.viz-description p').textContent = descriptions[vizType];
                });
            });
            
            // Export button event listener
            document.getElementById('exportViz').addEventListener('click', () => {
                const activeVizType = document.querySelector('.viz-tab.active').getAttribute('data-viz');
                exportVisualization(activeVizType);
            });
        }
    }
    
    // Function to load visualizations from the server
    async function loadVisualization(vizType, papers) {
        const vizContent = document.querySelector('.viz-content');
        vizContent.innerHTML = `
            <div class="viz-loading">
                <div class="spinner"></div>
                <span>Loading visualization...</span>
            </div>
        `;
        
        try {
            const response = await fetch('/api/academic/visualizations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    type: vizType,
                    papers: papers.map(paper => {
                        // Try to extract year from published string (e.g., "2022-01-01" -> 2022)
                        let publishedYear = null;
                        if (paper.published) {
                            const yearMatch = paper.published.match(/\d{4}/);
                            if (yearMatch) {
                                publishedYear = parseInt(yearMatch[0]);
                            }
                        }
                        
                        // Convert authors string to list format for the author visualization
                        let authorsList = [];
                        if (paper.authors) {
                            const authorNames = paper.authors.split(',').map(a => a.trim());
                            authorsList = authorNames.map(name => ({ name }));
                        }
                        
                        return {
                            title: paper.title,
                            authors: paper.authors,
                            authors_list: authorsList,
                            published: paper.published,
                            published_year: publishedYear,
                            summary: paper.summary,
                            pdf_url: paper.pdf_url,
                            arxiv_id: paper.id || paper.entry_id || paper.title.substring(0, 20).replace(/\s+/g, '-').toLowerCase()
                        };
                    })
                })
            });
            
            if (!response.ok) {
                throw new Error(`Failed to load visualization: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Create a container for the visualization
            vizContent.innerHTML = `<div id="${vizType}-container" class="${vizType}-container"></div>`;
            
            // The backend now returns direct data and layout objects
            if (data.data && data.layout) {
                Plotly.newPlot(
                    `${vizType}-container`, 
                    data.data, 
                    data.layout, 
                    {responsive: true}
                );
            } else {
                throw new Error("No visualization data received from server");
            }
            
        } catch (error) {
            console.error("Visualization error:", error);
            vizContent.innerHTML = `
                <div class="viz-placeholder">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <h3>Visualization unavailable</h3>
                    <p>${error.message || "Could not generate visualization. Try searching for a topic with more papers."}</p>
                    <p>Try searching for a topic with more papers (5-7 minimum) for better visualizations.</p>
                </div>
            `;
        }
    }

    // Function to export visualization as image
    function exportVisualization(vizType) {
        const vizElement = document.getElementById(`${vizType}-container`);
        if (!vizElement) return;
        
        Plotly.toImage(vizElement, {
            format: 'png',
            height: 800,
            width: 1200
        }).then(function(dataUrl) {
            // Create a download link
            const downloadLink = document.createElement('a');
            downloadLink.href = dataUrl;
            downloadLink.download = `sentino-${vizType}-visualization.png`;
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);
        }).catch(function(error) {
            console.error('Error exporting visualization:', error);
            alert('Failed to export visualization. Please try again.');
        });
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

// Global function for adding favorites (called from HTML)
window.addFavorite = function(query, searchType, result = null) {
    // Check if user is authenticated by looking for a user profile link
    const isAuthenticated = document.querySelector('.user-profile') !== null;
    
    if (isAuthenticated) {
        const favoritePrompt = document.getElementById('save-favorite-modal');
        if (favoritePrompt) {
            // Show the save favorite modal
            favoritePrompt.style.display = 'block';
            favoritePrompt.querySelector('input[name="query"]').value = query;
            favoritePrompt.querySelector('input[name="search_type"]').value = searchType;
        } else {
            // Fallback to prompt
            const name = prompt('Enter a name for this favorite:', query);
            if (name) {
                saveFavorite(name, query, searchType, result);
            }
        }
    } else {
        if (confirm('You need to be logged in to save favorites. Would you like to login now?')) {
            window.location.href = '/login';
        }
    }
}

function saveFavorite(name, query, searchType, result = null) {
    fetch('/api/favorites/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name,
            query,
            search_type: searchType,
            result
        })
    })
    .then(response => {
        if (response.ok) {
            alert('Added to favorites!');
        } else {
            alert('Failed to add to favorites');
        }
    })
    .catch(error => {
        console.error('Error adding favorite:', error);
        alert('An error occurred');
    });
}
