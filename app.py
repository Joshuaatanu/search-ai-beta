# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import config

app = Flask(__name__)
CORS(app)  # Allow cross-origin if needed

# Helper function to query Gemini
def query_gemini(user_query):
    headers = {"Authorization": f"Bearer {config.GEMINI_API_KEY}",
               "Content-Type": "application/json"}
    payload = {
        "prompt": user_query,
        "max_tokens": 150,
        "temperature": 0.7
    }
    try:
        response = requests.post(config.GEMINI_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        # Assume the API returns a field 'generated_text'
        return data.get("generated_text", "")
    except requests.RequestException as e:
        print("Gemini API error:", e)
        return None

# Helper function to query Deepseek
def query_deepseek(query_text):
    headers = {"Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
               "Content-Type": "application/json"}
    payload = {
        "query": query_text,
        "limit": 5  # Return top 5 results
    }
    try:
        response = requests.post(config.DEEPSEEK_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        # Assume the API returns a field 'results'
        return data.get("results", [])
    except requests.RequestException as e:
        print("Deepseek API error:", e)
        return []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/query", methods=["POST"])
def handle_query():
    data = request.json
    user_query = data.get("query", "")
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    # Step 1: Process with Gemini (e.g., to refine the query or produce a summary)
    gemini_response = query_gemini(user_query)
    if gemini_response is None:
        return jsonify({"error": "Error processing query with Gemini"}), 500

    # Step 2: Use the (refined) query to search Deepseek
    search_results = query_deepseek(gemini_response)

    # Compose final response
    final_response = {
        "query": user_query,
        "refined_query": gemini_response,
        "results": search_results
    }

    return jsonify(final_response)

if __name__ == "__main__":
    app.run(debug=config.DEBUG)
