# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import config

# Import the Gemini client from Google’s generative AI library
import google.generativeai as genai
app = Flask(__name__)
CORS(app)

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
        return response.text
    except Exception as e:
        print("Gemini API error:", e)
        return None


    """
    Queries the Deepseek API using an HTTP POST request.
    """
    headers = {
        "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
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

    # Use Gemini to generate a response.
    gemini_response = query_gemini(user_query)
    if gemini_response is None:
        return jsonify({"error": "Error processing query with Gemini"}), 500

    final_response = {
        "query": user_query,
        "response": gemini_response
    }

    return jsonify(final_response)

if __name__ == "__main__":
    app.run(debug=config.DEBUG)