# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
# from google import genai
from duckduckgo_search import DDGS
import os
from dotenv import load_dotenv
# Import the Gemini client from Google's generative AI library
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

def query_duckduckgo_text(query):
    """
    Uses DuckDuckGo's text search via the duckduckgo_search library to get search results.
    """
    try:
        ddgs = DDGS()
        results = ddgs.text(keywords=query, region="wt-wt", safesearch="moderate", max_results=3) # Reduced max_results for chat context
        return results
    except Exception as e:
        print("DuckDuckGo text search error:", e)
        return []

def generate_search_context(search_results):
    """
    Generates a combined text string from search results to provide context to Gemini.
    """
    combined_text = ""
    for result in search_results:
        title = result.get("title", "No title")
        snippet = result.get("body", "No snippet available")
        url = result.get("href", "")
        combined_text += f"Title: {title}\nSnippet: {snippet}\nURL: {url}\n\n"
    return combined_text


def query_gemini_chat(messages, context=None, deep_analysis=False, use_search=False):
    """
    Uses the Gemini API to generate a chat response based on conversation history,
    with optional deep analysis and DuckDuckGo search integration.
    """
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.0-flash") # or "gemini-pro"

        gemini_messages = []
        if context:
            gemini_messages.append({"role": "user", "parts": [{"text": f"Context for this conversation: {context}"}]})

        # Incorporate search results if use_search is True
        search_context_text = ""
        if use_search and messages: # Only search if there are messages (to have a query)
            last_user_message_content = messages[-1]['content']
            search_results = query_duckduckgo_text(last_user_message_content)
            search_context_text = generate_search_context(search_results)
            if search_context_text:
                gemini_messages.append({"role": "user", "parts": [{"text": f"Search Results:\n{search_context_text}"}]}) # Add search results as context

        for msg in messages:
            gemini_messages.append({"role": msg['role'], "parts": [{"text": msg['content']}]})


        prompt_prefix = ""
        if deep_analysis:
            prompt_prefix += (
                "Perform a deep and comprehensive analysis in your response. "
                "Consider multiple perspectives, underlying mechanisms, and potential implications. "
            )

        # Prepend prompt prefix to the last user message (which is the current turn's prompt)
        if gemini_messages and gemini_messages[-1]['role'] == 'user': # Ensure there's a user message
            last_message_content = gemini_messages[-1]['parts'][0]['text']
            gemini_messages[-1]['parts'][0]['text'] = prompt_prefix + last_message_content


        chat = model.start_chat(history=gemini_messages)
        response = chat.send_message(gemini_messages[-1]["parts"][0]["text"]) # Send the (potentially modified) last user message

        return response.text
    except Exception as e:
        print("Gemini API chat error:", e)
        return None


@app.route("/api/chat", methods=["POST"])
def handle_chat():
    data = request.json
    messages = data.get("messages", [])
    context = data.get("context")
    deep_analysis_enabled = data.get("deep_analysis", False) # Get deep_analysis flag
    use_search_enabled = data.get("use_search", False) # Get use_search flag


    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    gemini_response_text = query_gemini_chat(
        messages,
        context,
        deep_analysis=deep_analysis_enabled, # Pass deep_analysis flag
        use_search=use_search_enabled # Pass use_search flag
    )

    if gemini_response_text is None:
        return jsonify({"error": "Error generating chat response from Gemini"}), 500

    final_response = {
        "response": gemini_response_text,
        "deep_analysis": deep_analysis_enabled, # Return flags in response for frontend awareness
        "use_search": use_search_enabled
    }
    print(f'{final_response=}')
    return jsonify(final_response)


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


def query_gemini(prompt, deep_analysis=False):  # Add deep_analysis parameter
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
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


if __name__ == "__main__":
    port =int(os.getenv("PORT",10000))
    app.run(host='0.0.0.0',debug=True, port=port)