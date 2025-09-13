document.addEventListener("DOMContentLoaded", function () {
    // Mobile menu functionality
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const nav = document.querySelector('nav');
    
    if (mobileMenuToggle && nav) {
        mobileMenuToggle.addEventListener('click', () => {
            mobileMenuToggle.classList.toggle('active');
            nav.classList.toggle('active');
            document.body.style.overflow = nav.classList.contains('active') ? 'hidden' : '';
        });

        // Close mobile menu when clicking a nav link
        const navLinks = nav.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenuToggle.classList.remove('active');
                nav.classList.remove('active');
                document.body.style.overflow = '';
            });
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            if (nav.classList.contains('active') &&
                !nav.contains(e.target) &&
                !mobileMenuToggle.contains(e.target)) {
                mobileMenuToggle.classList.remove('active');
                nav.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }

    // Global elements
    const themeSwitcher = document.getElementById('themeSwitcher');
    const clearResults = document.getElementById('clearResults');
    const navLinks = document.querySelectorAll('.nav-link');
    const featureCards = document.querySelectorAll('.feature-card');
    
    // View containers
    const welcomeView = document.getElementById('welcome-view');
    const searchView = document.getElementById('search-view');
    const deepAnalysisView = document.getElementById('deep-analysis-view');
    const academicView = document.getElementById('academic-view');
    
    // Check if we're on the main page with views
    const isMainPage = welcomeView || searchView || deepAnalysisView || academicView;
    
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
    if (themeSwitcher) {
        themeSwitcher.addEventListener('click', () => {
            currentThemeIndex = (currentThemeIndex + 1) % themes.length;
            const newTheme = themes[currentThemeIndex];
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }

    // Clear results button
    if (clearResults) {
        clearResults.addEventListener('click', () => {
            if (searchResults) searchResults.innerHTML = '';
            if (deepAnalysisResults) deepAnalysisResults.innerHTML = '';
            if (academicResults) academicResults.innerHTML = '';
        });
    }

    // Initialize views only if we're on the main page
    if (isMainPage) {
        // Show last active view from local storage or default to welcome
        const lastActiveView = localStorage.getItem('lastView') || 'welcome';
        showView(lastActiveView);
        
        // Navigation event listeners
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const viewId = link.getAttribute('data-view');
                // Only prevent default and handle internally if it has a data-view attribute
                if (viewId) {
                    e.preventDefault();
                    showView(viewId);
                }
                // Links without data-view will navigate normally
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
                const enableSciHub = document.getElementById('enableSciHub')?.checked ?? true;
                
                if (enableSciHub) {
                    // Use Sci-Hub enhanced search
                    await handleAcademicSearchWithSciHub(query, maxPapers, academicResults);
                } else {
                    // Use regular academic search
                await handleAcademicSearch(query, maxPapers, academicResults);
                }
            });
        }
        
        // If URL has query parameters, trigger appropriate search
        const urlParams = new URLSearchParams(window.location.search);
        const queryParam = urlParams.get('query');
        const typeParam = urlParams.get('type');
        
        if (queryParam) {
            setTimeout(() => {
                if (typeParam === 'deep') {
                    const deepLink = document.querySelector('.nav-link[data-view="deep-analysis"]');
                    if (deepLink) deepLink.click();
                    const deepAnalysisInput = document.getElementById('deepAnalysisInput');
                    if (deepAnalysisForm && deepAnalysisInput) {
                        deepAnalysisInput.value = queryParam;
                        deepAnalysisForm.dispatchEvent(new Event('submit'));
                    }
                } else if (typeParam === 'academic') {
                    const academicLink = document.querySelector('.nav-link[data-view="academic"]');
                    if (academicLink) academicLink.click();
                    const academicInput = document.getElementById('academicInput');
                    if (academicForm && academicInput) {
                        academicInput.value = queryParam;
                        academicForm.dispatchEvent(new Event('submit'));
                    }
                } else {
                    const searchLink = document.querySelector('.nav-link[data-view="search"]');
                    if (searchLink) searchLink.click();
                    const searchInput = document.getElementById('searchInput');
                    if (searchForm && searchInput) {
                        searchInput.value = queryParam;
                        searchForm.dispatchEvent(new Event('submit'));
                    }
                }
            }, 100);
        }
    }

    // Navigation handling
    function showView(viewId) {
        // Hide all views
        if (welcomeView) welcomeView.style.display = 'none';
        if (searchView) searchView.style.display = 'none';
        if (deepAnalysisView) deepAnalysisView.style.display = 'none';
        if (academicView) academicView.style.display = 'none';
        
        // Deactivate all nav links
        navLinks.forEach(link => link.classList.remove('active'));
        
        // Show selected view and activate its nav link
        if (viewId === 'welcome') {
            if (welcomeView) welcomeView.style.display = 'block';
        } else {
            const viewElement = document.getElementById(`${viewId}-view`);
            if (viewElement) viewElement.style.display = 'block';
            
            const navLink = document.querySelector(`.nav-link[data-view="${viewId}"]`);
            if (navLink) navLink.classList.add('active');
            
            // Save last active view to localStorage
            localStorage.setItem('lastView', viewId);
        }
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
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    max_papers: maxPapers
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to process research query');
            }
            
            const data = await response.json();
            renderAcademicResults(data, resultsContainer, query);
            
        } catch (err) {
            console.error("Error processing academic request:", err);
            showError(resultsContainer, err.message, true);
        }
    }
    
    // Sci-Hub focused academic search function
    async function handleAcademicSearchWithSciHub(query, maxPapers, resultsContainer) {
        showLoading(resultsContainer, 'Searching Sci-Hub directly for papers...');
        
        try {
            const response = await fetch('/api/scihub-search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    max_results: maxPapers
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to process research query');
            }
            
            const data = await response.json();
            renderAcademicResults(data, resultsContainer, query);
            
            // Show Sci-Hub statistics
            if (data.scihub_stats) {
                const stats = data.scihub_stats;
                showToast(`Sci-Hub: ${stats.available_on_scihub}/${stats.total_papers} papers available (${stats.availability_rate.toFixed(1)}%)`, 'info');
            }
            
        } catch (err) {
            console.error("Error processing academic request with Sci-Hub:", err);
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
        container.innerHTML = '';
        console.log("Academic papers data:", data.papers);
        
        // Create main results container
        const resultsHTML = `
            <div class="academic-results">
                <h2>Academic Research: ${escapeHtml(data.query || "N/A")}</h2>
                <div class="actions-bar">
                    <button onclick="addFavorite('${escapeHtml(originalQuery)}', 'academic')">Save to Favorites</button>
                </div>
                
                <div class="methodology-filter-container">
                    <h3>Filter by Research Methodology</h3>
                    <div class="methodology-filter">
                        <select id="methodologyFilter" onchange="filterByMethodology(this.value)">
                            <option value="all">All Methodologies</option>
                            <option value="empirical">Empirical</option>
                            <option value="theoretical">Theoretical</option>
                            <option value="review">Review/Survey</option>
                            <option value="case_study">Case Study</option>
                            <option value="simulation">Simulation</option>
                            <option value="design">Design/Implementation</option>
                            <option value="unknown">Other/Unknown</option>
                        </select>
                    </div>
                    <div id="methodologyStats" class="methodology-stats">
                        ${renderMethodologyStats(data.methodology_comparison)}
                    </div>
                </div>
                
                <div class="academic-analysis">
                    ${marked.parse(data.answer || "No analysis available.")}
                </div>
                
                <div id="papersContainer">
                    <h3>Academic Papers</h3>
                    <div class="papers-list">
                        ${data.papers.map(paper => renderPaperCard(paper)).join('')}
                    </div>
                </div>
                
                <div class="visualizations-container">
                    <div class="viz-title">Research Visualizations</div>
                    <div class="viz-tabs">
                        <div class="viz-tab active" data-viz="network">Citation Network</div>
                        <div class="viz-tab" data-viz="timeline">Research Timeline</div>
                        <div class="viz-tab" data-viz="authors">Author Collaborations</div>
                        <div class="viz-tab" data-viz="methodology">Methodology Breakdown</div>
                    </div>
                    <div class="viz-description" id="vizDescription">
                        This network visualization shows citation relationships between papers. Each node represents a paper, with edges showing citations.
                    </div>
                    <div class="viz-container" id="vizContainer"></div>
                </div>
            </div>
        `;
        
        container.innerHTML = resultsHTML;
        
        // Store papers data for filtering
        window.currentPapers = data.papers;
        window.methodologyComparison = data.methodology_comparison;
        
        // Initialize visualization tabs
        initializeVisualizationTabs(data.papers);
    }
    
    function renderMethodologyStats(comparison) {
        if (!comparison || !comparison.counts) {
            return '<p>No methodology data available</p>';
        }
        
        const counts = comparison.counts;
        const total = comparison.total_papers || 0;
        
        // Create a bar chart-like display of methodology distribution
        let statsHTML = '<div class="methodology-distribution">';
        
        for (const [methodType, count] of Object.entries(counts)) {
            const percentage = total > 0 ? (count / total * 100).toFixed(0) : 0;
            const displayName = formatMethodologyName(methodType);
            
            statsHTML += `
                <div class="methodology-bar">
                    <div class="methodology-label">${displayName}</div>
                    <div class="methodology-bar-container">
                        <div class="methodology-bar-fill" style="width: ${percentage}%"></div>
                        <div class="methodology-count">${count} (${percentage}%)</div>
                    </div>
                </div>
            `;
        }
        
        statsHTML += '</div>';
        return statsHTML;
    }

    function formatMethodologyName(methodType) {
        // Convert snake_case to Title Case with proper naming
        const methodNames = {
            'empirical': 'Empirical Research',
            'theoretical': 'Theoretical Analysis',
            'review': 'Literature Review',
            'case_study': 'Case Study',
            'simulation': 'Simulation',
            'design': 'Design/Implementation',
            'unknown': 'Other/Unknown'
        };
        
        return methodNames[methodType] || methodType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    function renderPaperCard(paper) {
        const methodologyInfo = paper.methodology || { primary_type: 'unknown' };
        const methodologyType = formatMethodologyName(methodologyInfo.primary_type);
        const methodologySentences = methodologyInfo.key_sentences || [];
        const methodologyHighlight = methodologySentences.length > 0 
            ? `<div class="methodology-highlight">${methodologySentences[0]}</div>` 
            : '';
        
        // Sci-Hub availability indicator and button
        const scihubAvailable = paper.scihub_available || false;
        const scihubIndicator = scihubAvailable 
            ? '<div class="scihub-indicator available" title="Available on Sci-Hub">🔓 Sci-Hub Available</div>'
            : '<div class="scihub-indicator unavailable" title="Not found on Sci-Hub">🔒 Sci-Hub Unavailable</div>';
        
        // Sci-Hub download button
        const scihubButton = scihubAvailable 
            ? `<button class="scihub-download-btn" onclick="downloadFromSciHub('${escapeHtml(paper.scihub_pdf_url || '')}', '${escapeHtml(paper.title.replace(/'/g, "\\'"))}.pdf')" title="Download PDF from Sci-Hub">📥 Download PDF</button>`
            : `<button class="scihub-search-btn" onclick="searchSciHub('${escapeHtml(paper.doi || paper.url || paper.title)}')" title="Search for this paper on Sci-Hub">🔍 Find on Sci-Hub</button>`;
        
        return `
            <div class="paper-card methodology-${methodologyInfo.primary_type}">
                <div class="paper-methodology-badge">${methodologyType}</div>
                ${scihubIndicator}
                <h4 class="paper-title">${escapeHtml(paper.title)}</h4>
                <div class="paper-authors">${escapeHtml(paper.authors)}</div>
                <div class="paper-date">Published: ${escapeHtml(paper.published || 'Unknown')}</div>
                <div class="paper-summary">${escapeHtml(paper.summary.substring(0, 200))}${paper.summary.length > 200 ? '...' : ''}</div>
                ${methodologyHighlight}
                <div class="paper-links">
                    <a href="${paper.pdf_url}" target="_blank" class="paper-link">View PDF</a>
                    ${scihubButton}
                    <button class="paper-methodology-btn" onclick="showMethodologyDetails('${escapeHtml(paper.title.replace(/'/g, "\\'"))}')">Methodology Details</button>
                </div>
            </div>
        `;
    }

    async function filterByMethodology(methodologyType) {
        const papersContainer = document.getElementById('papersContainer');
        const methodologyStats = document.getElementById('methodologyStats');
        
        if (!papersContainer || !window.currentPapers) return;
        
        // Show loading indicator
        papersContainer.innerHTML = '<div class="loading"><div class="spinner"></div><p>Filtering papers...</p></div>';
        
        try {
            // If "all" is selected, use all papers
            if (methodologyType === 'all') {
                // Redisplay all papers
                papersContainer.innerHTML = `
                    <h3>Academic Papers</h3>
                    <div class="papers-list">
                        ${window.currentPapers.map(paper => renderPaperCard(paper)).join('')}
                    </div>
                `;
                
                // Update methodology stats with original comparison
                if (methodologyStats && window.methodologyComparison) {
                    methodologyStats.innerHTML = renderMethodologyStats(window.methodologyComparison);
                }
                return;
            }
            
            // Call API to filter papers by methodology
            const response = await fetch('/api/methodology-filter', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    papers: window.currentPapers,
                    methodology_type: methodologyType
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to filter papers by methodology');
            }
            
            const data = await response.json();
            
            // Render filtered papers
            papersContainer.innerHTML = `
                <h3>Academic Papers (${data.papers.length} ${formatMethodologyName(methodologyType)} papers)</h3>
                <div class="papers-list">
                    ${data.papers.map(paper => renderPaperCard(paper)).join('')}
                </div>
            `;
            
            // Update methodology stats
            if (methodologyStats) {
                methodologyStats.innerHTML = renderMethodologyStats(data.methodology_comparison);
            }
            
        } catch (err) {
            console.error("Error filtering papers by methodology:", err);
            papersContainer.innerHTML = `
                <h3>Academic Papers</h3>
                <div class="error">Error filtering papers: ${err.message}</div>
                <div class="papers-list">
                    ${window.currentPapers.map(paper => renderPaperCard(paper)).join('')}
                </div>
            `;
        }
    }

    function showMethodologyDetails(paperTitle) {
        if (!window.currentPapers) return;
        
        // Find the paper by title
        const paper = window.currentPapers.find(p => p.title === paperTitle);
        if (!paper || !paper.methodology) return;
        
        // Create modal for methodology details
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.id = 'methodologyModal';
        
        const methodology = paper.methodology;
        const keySentences = methodology.key_sentences || [];
        const confidenceScores = methodology.confidence_scores || {};
        
        // Format confidence scores as percentage bars
        let scoresHTML = '';
        for (const [type, score] of Object.entries(confidenceScores)) {
            const percentage = (score * 100).toFixed(1);
            const displayName = formatMethodologyName(type);
            
            scoresHTML += `
                <div class="confidence-bar">
                    <div class="confidence-label">${displayName}</div>
                    <div class="confidence-bar-container">
                        <div class="confidence-bar-fill" style="width: ${percentage}%"></div>
                        <div class="confidence-value">${percentage}%</div>
                    </div>
                </div>
            `;
        }
        
        // Format key sentences
        const sentencesHTML = keySentences.length > 0 
            ? `<div class="key-sentences"><h4>Key Methodology Sentences</h4>${keySentences.map(s => `<p>${s}</p>`).join('')}</div>`
            : '<p>No key methodology sentences found.</p>';
        
        // Create modal content
        modal.innerHTML = `
            <div class="modal-content methodology-modal">
                <span class="modal-close">&times;</span>
                <h3>Methodology Analysis: ${escapeHtml(paper.title)}</h3>
                
                <div class="methodology-type">
                    <h4>Primary Methodology: ${formatMethodologyName(methodology.primary_type)}</h4>
                </div>
                
                <div class="methodology-confidence">
                    <h4>Methodology Confidence Scores</h4>
                    ${scoresHTML}
                </div>
                
                ${sentencesHTML}
            </div>
        `;
        
        // Add modal to body
        document.body.appendChild(modal);
        
        // Show modal
        modal.style.display = 'block';
        
        // Close button functionality
        const closeBtn = modal.querySelector('.modal-close');
        closeBtn.onclick = function() {
            modal.style.display = 'none';
            modal.remove();
        };
        
        // Close when clicking outside of modal content
        window.onclick = function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
                modal.remove();
            }
        };
    }

    function initializeVisualizationTabs(papers) {
        const vizTabs = document.querySelectorAll('.viz-tab');
        const vizContainer = document.getElementById('vizContainer');
        const vizDescription = document.getElementById('vizDescription');
        
        if (!vizTabs.length || !vizContainer || !vizDescription) return;
        
        // Description for each visualization type
        const descriptions = {
            'network': 'This network visualization shows citation relationships between papers. Each node represents a paper, with edges showing citations.',
            'timeline': 'This timeline shows the progression of research on this topic over time. Explore how the field has evolved.',
            'authors': 'This visualization shows collaboration networks between authors. Larger nodes indicate authors with more papers.',
            'methodology': 'This visualization shows the distribution of research methodologies across papers. It helps identify predominant research approaches used in this field.'
        };
        
        // Initially load the network visualization (active by default)
        loadVisualization('network', papers, vizContainer);
        
        // Add click handlers for tabs
        vizTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Update active tab
                vizTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Get visualization type
                const vizType = tab.getAttribute('data-viz');
                
                // Update description
                vizDescription.textContent = descriptions[vizType] || '';
                
                // Load visualization
                loadVisualization(vizType, papers, vizContainer);
            });
        });
    }

    async function loadVisualization(vizType, papers, container) {
        // Show loading indicator
        container.innerHTML = '<div class="loading"><div class="spinner"></div><p>Generating visualization...</p></div>';
        
        try {
            // If methodology visualization, render locally
            if (vizType === 'methodology') {
                renderMethodologyVisualization(papers, container);
                return;
            }
            
            // For other visualizations, call the server API
            const response = await fetch('/api/academic/visualizations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    papers: papers,
                    type: vizType
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to generate visualization');
            }
            
            const data = await response.json();
            
            // Create Plotly visualization
            Plotly.newPlot(container, data.data, data.layout, {responsive: true});
            
        } catch (err) {
            console.error(`Error generating ${vizType} visualization:`, err);
            container.innerHTML = `<div class="error">Error generating visualization: ${err.message}</div>`;
        }
    }

    function renderMethodologyVisualization(papers, container) {
        if (!papers || papers.length === 0) {
            container.innerHTML = '<div class="error">No papers available for visualization</div>';
            return;
        }
        
        // Count methodologies
        const methodologyCounts = {};
        papers.forEach(paper => {
            if (paper.methodology && paper.methodology.primary_type) {
                const methodType = paper.methodology.primary_type;
                methodologyCounts[methodType] = (methodologyCounts[methodType] || 0) + 1;
            }
        });
        
        // Prepare data for Plotly
        const methodTypes = Object.keys(methodologyCounts);
        const counts = Object.values(methodologyCounts);
        
        // Custom colors for methodology types
        const colorMap = {
            'empirical': '#4285F4',
            'theoretical': '#EA4335',
            'review': '#FBBC05',
            'case_study': '#34A853',
            'simulation': '#9C27B0',
            'design': '#FF9800',
            'unknown': '#9E9E9E'
        };
        
        const colors = methodTypes.map(type => colorMap[type] || '#9E9E9E');
        
        // Display names for methodology types
        const displayNames = methodTypes.map(formatMethodologyName);
        
        // Create pie chart
        const data = [{
            type: 'pie',
            labels: displayNames,
            values: counts,
            marker: {
                colors: colors
            },
            textinfo: 'label+percent',
            hoverinfo: 'label+value+percent',
            textposition: 'outside',
            automargin: true
        }];
        
        const layout = {
            title: 'Distribution of Research Methodologies',
            showlegend: true,
            legend: {
                orientation: 'h',
                y: -0.1
            },
            margin: {t: 60, b: 60, l: 20, r: 20}
        };
        
        // Render pie chart
        Plotly.newPlot(container, data, layout, {responsive: true});
        
        // Add table with paper counts by methodology
        const tableContainer = document.createElement('div');
        tableContainer.className = 'methodology-table-container';
        
        let tableHTML = `
            <h4>Research Methodologies Breakdown</h4>
            <table class="methodology-table">
                <thead>
                    <tr>
                        <th>Methodology</th>
                        <th>Paper Count</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        const total = papers.length;
        methodTypes.forEach((type, index) => {
            const count = methodologyCounts[type];
            const percentage = ((count / total) * 100).toFixed(1);
            
            tableHTML += `
                <tr>
                    <td class="methodology-name">
                        <div class="methodology-color-dot" style="background-color: ${colorMap[type] || '#9E9E9E'}"></div>
                        ${displayNames[index]}
                    </td>
                    <td>${count}</td>
                    <td>${percentage}%</td>
                </tr>
            `;
        });
        
        tableHTML += `
                </tbody>
            </table>
        `;
        
        tableContainer.innerHTML = tableHTML;
        
        // Add the table below the chart
        container.parentNode.insertBefore(tableContainer, container.nextSibling);
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

// Search functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    const resultsBody = searchResults.querySelector('.results-body');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const clearResults = document.getElementById('clearResults');

    if (searchForm) {
        searchForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const query = searchInput.value.trim();
            
            if (!query) return;

            // Show loading indicator
            loadingIndicator.style.display = 'flex';
            searchResults.style.display = 'none';
            resultsBody.innerHTML = '';

            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        query: query,
                        type: 'quick'
                    })
                });

                if (!response.ok) {
                    throw new Error('Search request failed');
                }

                const data = await response.json();
                
                // Hide loading indicator and show results
                loadingIndicator.style.display = 'none';
                searchResults.style.display = 'block';

                // Render results
                data.results.forEach(result => {
                    const resultElement = document.createElement('div');
                    resultElement.className = 'search-result';
                    resultElement.innerHTML = `
                        <h3>${result.title}</h3>
                        <p>${result.snippet}</p>
                        ${result.source ? `<div class="result-source">Source: ${result.source}</div>` : ''}
                        ${result.confidence ? `<div class="result-confidence">Confidence: ${result.confidence}%</div>` : ''}
                    `;
                    resultsBody.appendChild(resultElement);
                });

                // If no results
                if (data.results.length === 0) {
                    resultsBody.innerHTML = '<div class="no-results">No results found</div>';
                }

            } catch (error) {
                console.error('Search error:', error);
                loadingIndicator.style.display = 'none';
                searchResults.style.display = 'block';
                resultsBody.innerHTML = '<div class="error-message">An error occurred while searching. Please try again.</div>';
            }
        });
    }

    // Clear results functionality
    if (clearResults) {
        clearResults.addEventListener('click', function() {
            searchInput.value = '';
            searchResults.style.display = 'none';
            resultsBody.innerHTML = '';
        });
    }

    // Handle input changes
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            if (!this.value.trim()) {
                searchResults.style.display = 'none';
                resultsBody.innerHTML = '';
            }
        });
    }

    // Sci-Hub Integration Functions
    window.downloadFromSciHub = async function(pdfUrl, filename) {
        if (!pdfUrl) {
            alert('No Sci-Hub PDF URL available');
            return;
        }

        try {
            showToast('Downloading paper from Sci-Hub...', 'info');
            
            const response = await fetch('/api/scihub/download-paper', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    pdf_url: pdfUrl,
                    filename: filename
                })
            });

            if (response.ok) {
                // Create blob from response
                const blob = await response.blob();
                
                // Create download link
                const downloadUrl = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.style.display = 'none';
                link.href = downloadUrl;
                link.download = filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(downloadUrl);
                
                showToast('Paper downloaded successfully!', 'success');
            } else {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Download failed');
            }
        } catch (error) {
            console.error('Error downloading from Sci-Hub:', error);
            showToast(`Download failed: ${error.message}`, 'error');
        }
    };

    window.searchSciHub = async function(identifier) {
        if (!identifier) {
            alert('No identifier available for Sci-Hub search');
            return;
        }

        try {
            showToast('Searching Sci-Hub...', 'info');
            
            // Determine search type and endpoint based on identifier
            let endpoint;
            let payload;
            
            if (identifier.includes('10.') && identifier.includes('/')) {
                // Looks like a DOI
                endpoint = '/api/scihub/paper-by-doi';
                payload = { doi: identifier };
            } else if (identifier.startsWith('http')) {
                // Looks like a URL
                endpoint = '/api/scihub/paper-by-url';
                payload = { url: identifier };
            } else {
                // Treat as title
                endpoint = '/api/scihub/paper-by-title';
                payload = { title: identifier };
            }

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (data.success && data.paper) {
                showToast('Paper found on Sci-Hub!', 'success');
                
                // Show Sci-Hub result modal
                showSciHubModal(data.paper);
            } else {
                showToast('Paper not found on Sci-Hub', 'warning');
            }
        } catch (error) {
            console.error('Error searching Sci-Hub:', error);
            showToast(`Search failed: ${error.message}`, 'error');
        }
    };

    window.enhancePapersWithSciHub = async function(papers) {
        if (!papers || papers.length === 0) {
            return papers;
        }

        try {
            showToast('Checking Sci-Hub availability...', 'info');
            
            const response = await fetch('/api/scihub/enhance-papers', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ papers: papers })
            });

            const data = await response.json();

            if (data.success) {
                showToast(`Enhanced ${data.papers.length} papers with Sci-Hub data`, 'success');
                
                // Show availability stats
                if (data.stats) {
                    const availableCount = data.stats.available_on_scihub;
                    const totalCount = data.stats.total_papers;
                    const rate = data.stats.availability_rate.toFixed(1);
                    
                    showToast(`Sci-Hub Availability: ${availableCount}/${totalCount} papers (${rate}%)`, 'info');
                }
                
                return data.papers;
            } else {
                throw new Error('Failed to enhance papers with Sci-Hub data');
            }
        } catch (error) {
            console.error('Error enhancing papers with Sci-Hub:', error);
            showToast(`Enhancement failed: ${error.message}`, 'error');
            return papers; // Return original papers if enhancement fails
        }
    };

    function showSciHubModal(paper) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.id = 'scihubModal';
        
        modal.innerHTML = `
            <div class="modal-content scihub-modal">
                <span class="modal-close">&times;</span>
                <h3>📚 Paper Found on Sci-Hub</h3>
                
                <div class="scihub-paper-info">
                    <h4>${escapeHtml(paper.title || 'Unknown Title')}</h4>
                    ${paper.authors ? `<p><strong>Authors:</strong> ${escapeHtml(paper.authors)}</p>` : ''}
                    ${paper.doi ? `<p><strong>DOI:</strong> ${escapeHtml(paper.doi)}</p>` : ''}
                </div>
                
                <div class="scihub-actions">
                    <button class="scihub-download-btn" onclick="downloadFromSciHub('${escapeHtml(paper.pdf_url)}', '${escapeHtml(paper.title || 'paper')}.pdf')">
                        📥 Download PDF
                    </button>
                    <a href="${paper.scihub_url}" target="_blank" class="scihub-view-btn">
                        🔗 View on Sci-Hub
                    </a>
                </div>
                
                <div class="scihub-disclaimer">
                    <small>⚠️ Please respect copyright laws and use academic papers responsibly for research and educational purposes.</small>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add close functionality
        const closeBtn = modal.querySelector('.modal-close');
        closeBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
        
        // Show modal
        modal.style.display = 'block';
    }

    function showToast(message, type = 'info') {
        // Remove existing toasts
        const existingToasts = document.querySelectorAll('.toast');
        existingToasts.forEach(toast => toast.remove());
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        // Add toast styles if not already added
        if (!document.querySelector('#toast-styles')) {
            const style = document.createElement('style');
            style.id = 'toast-styles';
            style.textContent = `
                .toast {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 12px 24px;
                    border-radius: 8px;
                    color: white;
                    font-weight: 500;
                    z-index: 10000;
                    max-width: 400px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                    animation: slideInRight 0.3s ease-out;
                }
                .toast-info { background-color: #3498db; }
                .toast-success { background-color: #27ae60; }
                .toast-warning { background-color: #f39c12; }
                .toast-error { background-color: #e74c3c; }
                
                @keyframes slideInRight {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(toast);
        
        // Auto remove after 4 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slideInRight 0.3s ease-out reverse';
                setTimeout(() => {
                    if (toast.parentNode) {
                        toast.remove();
                    }
                }, 300);
            }
        }, 4000);
    }
});


