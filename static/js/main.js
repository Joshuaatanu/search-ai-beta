document.getElementById('queryForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const queryInput = document.getElementById('queryInput');
    const query = queryInput.value.trim();
    if (!query) return;

    const responseContainer = document.getElementById('responseContainer');
    responseContainer.innerHTML = "<p>Loading...</p>";

    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query })
        });
        const data = await response.json();
        if (data.error) {
            responseContainer.innerHTML = `<p>Error: ${data.error}</p>`;
        } else {
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
            responseContainer.innerHTML = html;
        }
    } catch (err) {
        responseContainer.innerHTML = `<p>Error: ${err.message}</p>`;
    }
});
