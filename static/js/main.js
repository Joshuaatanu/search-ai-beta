document.addEventListener("DOMContentLoaded", function () {
    const queryForm = document.getElementById('queryForm');
    const queryInput = document.getElementById('queryInput');
    const responseContainer = document.getElementById('responseContainer');
    const themeSwitcher = document.getElementById('themeSwitcher');

    if (!queryForm || !queryInput || !responseContainer || !themeSwitcher) {
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
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }

            const data = await response.json();

            // Construct response HTML with Markdown parsing
            let html = `<h2 class="fade-in">Your Query:</h2>
                        <p class="fade-in typewriter">${escapeHtml(data.query || "N/A")}</p>`;

            html += `<h2 class="fade-in">AI Answer:</h2>
                     <div class="ai-response fade-in typewriter">${marked.parse(data.answer || "No answer available.")}</div>`;

            // If search results exist, display them
            if (data.search_results && data.search_results.length > 0) {
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
            responseContainer.innerHTML = `<p style="color:red;">Error: ${err.message}</p>`;
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
