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
import arxiv
import re

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

def query_arxiv(query, max_results=3):
    """
    Searches arXiv for academic papers based on the query.
    Returns a list of paper details including title, authors, summary, and PDF URL.
    """
    try:
        print(f"Querying arXiv with: {query}")
        # Clean the query for better arXiv search results
        cleaned_query = re.sub(r'[^\w\s]', ' ', query).strip()
        if not cleaned_query:
            cleaned_query = query  # Use original if cleaning removed everything
        
        print(f"Cleaned query: {cleaned_query}")
        
        # Create a client with appropriate parameters
        client = arxiv.Client(
            page_size=max_results,
            delay_seconds=1,
            num_retries=2
        )
        
        # Create the search query
        search = arxiv.Search(
            query=cleaned_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        # Execute the search and collect results
        print("Executing arXiv search...")
        papers = []
        for result in client.results(search):
            try:
                # Extract publication date safely
                try:
                    published_date = result.published.strftime("%Y-%m-%d") if result.published else "Unknown"
                except:
                    published_date = "Unknown"
                
                # Extract authors safely
                try:
                    authors = ", ".join(author.name for author in result.authors) if result.authors else "Unknown"
                except:
                    authors = "Unknown"
                
                paper = {
                    "title": result.title or "Unknown Title",
                    "authors": authors,
                    "summary": result.summary or "No summary available",
                    "pdf_url": result.pdf_url or "#",
                    "published": published_date,
                    "arxiv_id": result.entry_id.split("/")[-1] if result.entry_id else "unknown"
                }
                papers.append(paper)
                print(f"Found paper: {paper['title']}")
            except Exception as e:
                print(f"Error processing paper result: {str(e)}")
                continue
        
        print(f"Found {len(papers)} papers")
        return papers
    except Exception as e:
        print(f"arXiv search error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def generate_arxiv_context(paper_results):
    """
    Generates a combined text string from arXiv papers to provide context to Gemini.
    """
    combined_text = ""
    for i, paper in enumerate(paper_results, 1):
        combined_text += f"Paper {i}:\n"
        combined_text += f"Title: {paper['title']}\n"
        combined_text += f"Authors: {paper['authors']}\n"
        combined_text += f"Published: {paper['published']}\n"
        combined_text += f"Summary: {paper['summary']}\n"
        combined_text += f"URL: {paper['pdf_url']}\n\n"
    return combined_text

@app.route("/api/deep-research", methods=["POST"])
def handle_deep_research():
    try:
        data = request.json
        query = data.get("query", "")
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        # Get papers from arXiv
        try:
            paper_results = query_arxiv(query)
            print(f"Found {len(paper_results)} papers for query: {query}")
        except Exception as e:
            print(f"Error querying arXiv: {str(e)}")
            return jsonify({"error": f"Error querying arXiv: {str(e)}"}), 500
        
        if not paper_results:
            return jsonify({"error": "No relevant papers found"}), 404
        
        # Generate context from papers
        arxiv_context = generate_arxiv_context(paper_results)
        
        # Create an enhanced prompt for Gemini with more detailed instructions
        prompt = (
            f"You are an advanced academic research assistant with expertise in analyzing scientific papers. "
            f"I need you to provide a comprehensive analysis of the following arXiv papers to answer this query: '{query}'\n\n"
            f"Research Question: {query}\n\n"
            f"Here are the relevant papers and their summaries:\n\n{arxiv_context}\n\n"
            f"Please provide a detailed analysis that includes:\n"
            f"1. A comprehensive answer to the research question based on the papers\n"
            f"2. Key findings and methodologies from each relevant paper\n"
            f"3. Any consensus or contradictions among the different papers\n"
            f"4. Limitations of current research on this topic\n"
            f"5. Potential directions for future research\n\n"
            f"When citing papers, use the format 'According to [Authors] in [Title]...'\n"
            f"Your analysis should be well-structured with headings and sections, thorough, and scientifically accurate."
        )
        
        print("Sending enhanced prompt to Gemini for deep analysis")
        
        # Generate answer using Gemini with deep analysis mode
        try:
            # Use more tokens and higher temperature for academic analysis
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel(
                "gemini-2.0-flash",
                generation_config={
                    "max_output_tokens": 4096,  # Increased token limit for detailed analysis
                    "temperature": 0.7,  # Slightly higher temperature for academic analysis
                    "top_p": 0.95,
                    "top_k": 40
                }
            )
            
            response = model.generate_content(prompt)
            answer = response.text
            
            if not answer or answer.strip() == "":
                raise Exception("Gemini returned empty response")
                
            print("Successfully received analysis from Gemini")
            
        except Exception as e:
            print(f"Error generating answer from Gemini: {str(e)}")
            return jsonify({"error": f"Error generating answer from Gemini: {str(e)}"}), 500
        
        final_response = {
            "query": query,
            "papers": paper_results,
            "answer": answer,
            "feature": "deep_research",
            "analysis_type": "academic"
        }
        
        return jsonify(final_response)
    
    except Exception as e:
        print(f"Unexpected error in deep research: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    port =int(os.getenv("PORT",10000))
    app.run(host='0.0.0.0',debug=True, port=port)