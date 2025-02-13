# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import config
from duckduckgo_search import DDGS
# Import the Gemini client from Google’s generative AI library
import google.generativeai as genai

from google.genai import types
app = Flask(__name__)
CORS(app)
def query_duckduckgo_text(query):
    """
    Uses DuckDuckGo's text search via the duckduckgo_search library to get search results.
    """
    try:
        ddgs = DDGS()
        # Perform a text search with the provided query.
        # You can adjust parameters like region, safesearch, and max_results as needed.
        results = ddgs.text(keywords=query, region="wt-wt", safesearch="moderate", max_results=5)
        return results
    except Exception as e:
        print("DuckDuckGo text search error:", e)
        return []
        
def query_gemini(user_query):
    """
    Uses Google's genai client to generate content with the Gemini model.
    """
    try:
        # Create a client instance with your API key
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        response = model.generate_content(user_query)
        
        # Assume the response object has a `.text` attribute with the generated output
        print("Gemini API raw response:", response.text)

        return response.text
    except Exception as e:
        print("Gemini API error:", e)
        return None


def generate_answer_from_search(user_query, search_results):
    """
    Combines search results with the user query into a prompt that instructs Gemini to generate a summary.
    The prompt follows the provided step-by-step summarization instructions.
    """
    # Build a text block from up to 3 search results.
    combined_text = ""
    for result in search_results[:3]:
        title = result.get("title", "No title")
        snippet = result.get("body", "No snippet available")
        url = result.get("href", "")
        combined_text += f"Title: {title}\nSnippet: {snippet}\nURL: {url}\n\n"
    
    # Use the provided summarization prompt.
    prompt = (
        "To generate an output  of the following text, follow these steps:\n\n"
        "1. Read the text carefully to understand and analyse and add to  the main ideas and themes.\n"
        "2. Identify the key points and arguments presented in the text.\n"
        "3. Organize the information into related groups to form a coherent structure.\n"
        "4. Write a concise summary for each group of ideas.\n"
        "5. Combine the summaries into a single, cohesive summary.\n"
        "6. Review and refine the final summary for clarity and accuracy.\n\n"
        "Now, apply these steps to the following text:\n\n"
        f"{combined_text}\n"
        f"Question: {user_query}\n\n"
        "Answer:"
    )
    
    return query_gemini(prompt)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/query", methods=["POST"])
def handle_query():
    data = request.json
    user_query = data.get("query", "")
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    # 1. Retrieve search results using DuckDuckGo text search.
    search_results = query_duckduckgo_text(user_query)
    
    # 2. Generate an answer using Gemini with search results as context.
    generated_answer = generate_answer_from_search(user_query, search_results)
    if generated_answer is None:
        return jsonify({"error": "Error generating answer from Gemini"}), 500

    final_response = {
        "query": user_query,
        "search_results": search_results,
        "answer": generated_answer
    }

    return jsonify(final_response)

if __name__ == "__main__":
    app.run(debug=config.DEBUG)
