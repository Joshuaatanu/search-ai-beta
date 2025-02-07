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
            // Build the HTML output using the new structure
            let html = `<h2>Your query:</h2><p>${data.query}</p>`;
            html += `<h2>Response from Gemini:</h2>`;
            if (data.response) {
                html += `<p>${data.response}</p>`;
            } else {
                html += "<p>No response generated.</p>";
            }
            responseContainer.innerHTML = html;
        }
    } catch (err) {
        responseContainer.innerHTML = `<p>Error: ${err.message}</p>`;
    }
});




