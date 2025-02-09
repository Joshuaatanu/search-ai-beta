document.getElementById('queryForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const queryInput = document.getElementById('queryInput');
    const query = queryInput.value.trim();
    if (!query) return;

    const responseContainer = document.getElementById('responseContainer');

    // Show spinner and processing message
    responseContainer.innerHTML = `
      <div class="spinner"></div>
      <p class="processing">Processing your request...</p>
    `;
    responseContainer.style.opacity = 1;  // Ensure the container is visible

    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });
        const data = await response.json();

        // Build the HTML output based on the API response.
        let html = `<h2>Your Query:</h2><p>${data.query}</p>`;
        html += `<h2>AI Answer:</h2><p>${data.answer}</p>`;

        if (data.search_results && data.search_results.length > 0) {
            html += `<h2>Search Results:</h2><ul>`;
            data.search_results.forEach(result => {
                html += `<li>
            <strong>${result.title || "No title"}</strong><br>
            <span>${result.body || "No snippet available"}</span><br>
            <a href="${result.href}" target="_blank">${result.href}</a>
          </li>`;
            });
            html += `</ul>`;
        } else {
            html += "<p>No search results found.</p>";
        }

        // Apply fade-in effect by adding the fade-in class.
        responseContainer.innerHTML = html;
        responseContainer.classList.add("fade-in");
    } catch (err) {
        responseContainer.innerHTML = `<p>Error: ${err.message}</p>`;
    }
});
