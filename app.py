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
        
def query_gemini(prompt, deep_analysis=False):  # Add deep_analysis parameter
    try:
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config={
                "max_output_tokens": 2048 if deep_analysis else 1024,
                "temperature": 0.7 if deep_analysis else 0.3
            }
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("Gemini API error:", e)
        return None
def generate_answer_from_search(user_query, search_results, deep_analysis=False):
    """
    Generates answer with optional deep analysis mode
    """
    combined_text = ""
    for result in search_results[:3]:
        title = result.get("title", "No title")
        snippet = result.get("body", "No snippet available")
        url = result.get("href", "")
        combined_text += f"Title: {title}\nSnippet: {snippet}\nURL: {url}\n\n"

    # Modified prompt with deep analysis capabilities
    base_prompt = (
        "To generate a response for the following query, follow these steps:\n\n"
        "1. Perform comprehensive analysis of all provided sources\n"
        "2. Identify technical specifications and underlying mechanisms\n"
        "3. Cross-reference with known similar systems\n"
    )
    
    if deep_analysis:
        base_prompt += (
            "4. Conduct multi-perspective evaluation (technical, social, ethical)\n"
            "5. Generate predictive models for future developments\n"
            "6. Formulate potential failure scenarios and mitigation strategies\n\n"
        )
    else:
        base_prompt += (
            "4. Extract key actionable insights\n"
            "5. Summarize in clear, concise points\n\n"
        )

    prompt = (
        f"{base_prompt}"
        "Now, apply these steps to the following data:\n\n"
        f"{combined_text}\n"
        f"Query: {user_query}\n\n"
        "Provide a comprehensive response:\n"
    )
    
    return query_gemini(prompt,deep_analysis)
    

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/query", methods=["POST"])
def handle_query():
    data = request.json
    user_query = data.get("query", "")
    deep_analysis = data.get("enable_deep_analysis", False)
    
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    search_results = query_duckduckgo_text(user_query)
    generated_answer = generate_answer_from_search(user_query, search_results, deep_analysis)
    
    if generated_answer is None:
        return jsonify({"error": "Error generating answer from Gemini"}), 500

    final_response = {
        "query": user_query,
        "search_results": search_results,
        "answer": generated_answer,
        "deep_analysis": deep_analysis
    }
    print(final_response)
    return jsonify(final_response)
if __name__ == "__main__":
    app.run(debug=config.DEBUG)

