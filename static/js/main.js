document.addEventListener("DOMContentLoaded", function () {
    const queryForm = document.getElementById('queryForm');
    const queryInput = document.getElementById('queryInput');
    const responseContainer = document.getElementById('responseContainer');
    const themeSwitcher = document.getElementById('themeSwitcher');
    const deepAnalysisCheckbox = document.getElementById('deepAnalysisCheckbox');
    const deepResearchCheckbox = document.getElementById('deepResearchCheckbox');
    const clearResults = document.getElementById('clearResults');

    if (!queryForm || !queryInput || !responseContainer || !themeSwitcher || !deepAnalysisCheckbox || !deepResearchCheckbox) {
        console.error("Some elements are missing in the DOM. Ensure IDs match the HTML.");
        return;
    }

    // Load Markdown parser
    if (typeof marked === "undefined") {
        console.error("Markdown parser 'marked.js' not loaded.");
        return;
    }

    // Available themes
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
    if (clearResults) {
        clearResults.addEventListener('click', () => {
            responseContainer.innerHTML = '';
            responseContainer.style.opacity = 0;
        });
    }

    // Form submission
    queryForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = queryInput.value.trim();
        if (!query) return;

        const submitButton = queryForm.querySelector('button');

        // Disable button and show loading
        submitButton.disabled = true;
        responseContainer.innerHTML = `
            <div class="spinner"></div>
            <p class="processing typewriter">Processing your request...</p>
        `;
        responseContainer.style.opacity = 1;

        try {
            // Determine which endpoint to use based on checkboxes
            let endpoint = '/api/query';
            let requestBody = { query };
            
            // Deep Research mode (arXiv papers)
            if (deepResearchCheckbox.checked) {
                endpoint = '/api/deep-research';
                // Show special message for arXiv search
                responseContainer.innerHTML = `
                    <div class="spinner"></div>
                    <p class="processing typewriter">Searching academic papers on arXiv...</p>
                    <p class="processing">This may take a bit longer than regular searches</p>
                `;
            } else {
                // Regular search with optional deep analysis
                requestBody.enable_deep_analysis = deepAnalysisCheckbox.checked;
            }

            console.log(`Sending request to ${endpoint} with query: ${query}`);
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `API error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();
            console.log("Received response:", data);

            // Construct response HTML with Markdown parsing
            let html = `<h2 class="fade-in">Your Query:</h2>
                        <p class="fade-in typewriter">${escapeHtml(data.query || "N/A")}</p>`;

            html += `<h2 class="fade-in">AI Answer:</h2>
                     <div class="ai-response fade-in typewriter">${marked.parse(data.answer || "No answer available.")}</div>`;

            // If this is a deep research response with papers
            if (data.feature === "deep_research" && data.papers && data.papers.length > 0) {
                html += `<h2 class="fade-in">AI Analysis of Academic Papers</h2>`;
                html += `<div class="ai-response academic-analysis fade-in">${marked.parse(data.answer || "No analysis available.")}</div>`;
                
                html += `<h2 class="fade-in">Academic Papers Used in Analysis:</h2><div class="paper-list">`;
                data.papers.forEach(paper => {
                    html += `
                    <div class="paper-item fade-in">
                        <div class="paper-title">${escapeHtml(paper.title)}</div>
                        <div class="paper-authors">Authors: ${escapeHtml(paper.authors)}</div>
                        <div>Published: ${escapeHtml(paper.published)}</div>
                        <div class="paper-summary">${escapeHtml(paper.summary.substring(0, 200))}${paper.summary.length > 200 ? '...' : ''}</div>
                        <a class="paper-link" href="${paper.pdf_url}" target="_blank">View PDF</a>
                    </div>`;
                });
                html += `</div>`;
            }
            // If regular search results exist, display them
            else if (data.search_results && data.search_results.length > 0) {
                html += `<h2 class="fade-in">Search Results:</h2><ul>`;
                data.search_results.forEach(result => {
                    html += `<li class="fade-in">
                        <strong>${escapeHtml(result.title || "No title")}</strong><br>
                        <span>${escapeHtml(result.body || "No snippet available")}</span><br>
                        <a href="${result.href}" target="_blank">${result.href}</a>
                    </li>`;
                });
                html += `</ul>`;
            } else {
                html += "<p class='fade-in'>No search results found.</p>";
            }

            responseContainer.innerHTML = html;
            responseContainer.classList.add("fade-in");

        } catch (err) {
            console.error("Error processing request:", err);
            responseContainer.innerHTML = `
                <div class="error-container">
                    <h2>Error</h2>
                    <p>${escapeHtml(err.message)}</p>
                    ${deepResearchCheckbox.checked ? 
                        '<p>The arXiv search feature may be experiencing issues. Please try again with a more specific query or use the regular search option.</p>' : 
                        ''}
                </div>`;
        } finally {
            submitButton.disabled = false;
            queryInput.value = '';
        }
    });
});

// Function to escape HTML (for security)
function escapeHtml(text) {
    let element = document.createElement("div");
    element.innerText = text;
    return element.innerHTML;
}
