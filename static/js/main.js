// static/js/main.js
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
            // Display the refined query and search results
            let html = `<h2>Your query:</h2><p>${data.query}</p>`;
            html += `<h2>Refined Query (Gemini):</h2><p>${data.refined_query}</p>`;
            html += `<h2>Search Results (Deepseek):</h2>`;
            if (data.results.length) {
                html += '<ul>';
                data.results.forEach(result => {
                    // Assuming each result has a title, snippet, and citation URL
                    html += `<li>
                      <h3>${result.title || "Result"}</h3>
                      <p>${result.snippet || ""}</p>
                      ${result.citation ? `<a href="${result.citation}" target="_blank">Citation</a>` : ""}
                     </li>`;
                });
                html += '</ul>';
            } else {
                html += "<p>No results found.</p>";
            }
            responseContainer.innerHTML = html;
        }
    } catch (err) {
        responseContainer.innerHTML = `<p>Error: ${err.message}</p>`;
    }
});
