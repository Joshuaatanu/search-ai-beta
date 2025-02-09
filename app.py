# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import config
from duckduckgo_search import DDGS
# Import the Gemini client from Google’s generative AI library
import google.generativeai as genai
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
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Generate content using the Gemini model.
        # You can adjust parameters like model and prompt contents as needed.
        response = model.generate_content(user_query)
        # Assume the response object has a `.text` attribute with the generated output
        print("Gemini API raw response:", response.text)

        return response.text
    except Exception as e:
        print("Gemini API error:", e)
        return None


def generate_answer_from_search(user_query, search_results):
    """
    Combines search results with the user query into a prompt and generates an AI answer via Gemini.
    """
    prompt = "You are a knowledgeable assistant. Based on the following search results, answer the question:\n\n"
    # Use up to 3 search results for context.
    for result in search_results[:3]:
        title = result.get("title", "No title")
        snippet = result.get("body", "No snippet available")
        # For DuckDuckGo text results, the URL is typically under the key "href"
        url = result.get("href", "")
        prompt += f"Title: {title}\nSnippet: {snippet}\nURL: {url}\n\n"
    prompt += f"Question: {user_query}\n\nAnswer:"
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
