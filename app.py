# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
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
from flask_pymongo import PyMongo
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# OAuth Libraries
from authlib.integrations.flask_client import OAuth
import google_auth_oauthlib.flow
import google.oauth2.credentials
import google.oauth2.id_token
import google.auth.transport.requests

# Import models
from models import User, SearchHistory, Favorite, Recommendation

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Flask app
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(16))
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True

# Get MongoDB URI from environment or use default
mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/sentino")
print(f"Connecting to MongoDB: {mongodb_uri}")

# Set up MongoDB
app.config["MONGO_URI"] = mongodb_uri
mongo = PyMongo(app)

# Verify the connection is working and initialize collections
with app.app_context():
    try:
        # Check if we can list collections
        collections = mongo.db.list_collection_names()
        print(f"Connected to MongoDB. Existing collections: {collections}")
        
        # Ensure required collections exist
        required_collections = ["users", "search_history", "favorites", "password_resets"]
        for collection in required_collections:
            if collection not in collections:
                print(f"Creating collection: {collection}")
                mongo.db.create_collection(collection)
        
        print("MongoDB collections initialized successfully")
    except Exception as e:
        print(f"MongoDB connection or initialization failed: {e}")
        print("WARNING: Application may not function correctly without MongoDB!")

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Set up OAuth
oauth = OAuth(app)

# Google OAuth
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
if google_client_id and google_client_secret:
    oauth.register(
        name="google",
        client_id=google_client_id,
        client_secret=google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

# GitHub OAuth
github_client_id = os.getenv("GITHUB_CLIENT_ID")
github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
if github_client_id and github_client_secret:
    oauth.register(
        name="github",
        client_id=github_client_id,
        client_secret=github_client_secret,
        access_token_url="https://github.com/login/oauth/access_token",
        access_token_params=None,
        authorize_url="https://github.com/login/oauth/authorize",
        authorize_params=None,
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "user:email"},
    )

# Apple OAuth
apple_client_id = os.getenv("APPLE_CLIENT_ID")
apple_client_secret = os.getenv("APPLE_CLIENT_SECRET")
if apple_client_id and apple_client_secret:
    oauth.register(
        name="apple",
        client_id=apple_client_id,
        client_secret=apple_client_secret,
        server_metadata_url="https://appleid.apple.com/.well-known/openid-configuration",
        client_kwargs={"scope": "name email"},
    )

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', 'yes', '1')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# Password reset token expiration (in seconds)
PASSWORD_RESET_EXPIRATION = 3600  # 1 hour

# Function to send email
def send_email(to, subject, body_html):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = app.config['MAIL_DEFAULT_SENDER']
    msg['To'] = to
    
    html_part = MIMEText(body_html, 'html')
    msg.attach(html_part)
    
    try:
        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.ehlo()
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.sendmail(app.config['MAIL_DEFAULT_SENDER'], to, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.get_by_id(mongo.db, user_id)
    except Exception as e:
        print(f"Error loading user: {e}")
        return None

# Verify MongoDB is connected before handling requests
@app.before_request
def check_mongodb():
    if request.endpoint in ['login', 'static', 'github_callback', 'google_callback', 'apple_callback']:
        try:
            # Quick connectivity check
            mongo.db.command('ping')
        except Exception as e:
            print(f"MongoDB not available: {e}")
            if not request.path.startswith('/static/'):
                flash("Database connection issue. Some features may not work properly.", "error")

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
    deep_analysis_enabled = data.get("deep_analysis", False)
    use_search_enabled = data.get("use_search", False)

    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    gemini_response_text = query_gemini_chat(
        messages,
        context,
        deep_analysis=deep_analysis_enabled,
        use_search=use_search_enabled
    )

    if gemini_response_text is None:
        return jsonify({"error": "Error generating chat response from Gemini"}), 500

    final_response = {
        "response": gemini_response_text,
        "deep_analysis": deep_analysis_enabled,
        "use_search": use_search_enabled
    }
    
    # Log search history for logged-in users
    if current_user.is_authenticated and len(messages) > 0:
        query = messages[-1]['content']
        search_type = "deep" if deep_analysis_enabled else "quick"
        SearchHistory.add_search(mongo.db, current_user.get_id(), query, search_type)
    
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
    
    # Log search history for logged-in users
    if current_user.is_authenticated:
        search_type = "deep" if deep_analysis else "quick"
        results_count = len(search_results) if search_results else 0
        SearchHistory.add_search(mongo.db, current_user.get_id(), user_query, search_type, results_count)
    
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
        max_papers = data.get("max_papers", 3)
        
        # Ensure max_papers is an integer and within reasonable bounds
        try:
            max_papers = int(max_papers)
            max_papers = min(max(max_papers, 1), 10)
        except (ValueError, TypeError):
            max_papers = 3
            
        print(f"Deep research request: query='{query}', max_papers={max_papers}")
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        # Get papers from arXiv
        try:
            paper_results = query_arxiv(query, max_papers)
            print(f"Found {len(paper_results)} papers for query: {query}")
        except Exception as e:
            print(f"Error querying arXiv: {str(e)}")
            return jsonify({"error": f"Error querying arXiv: {str(e)}"}), 500
        
        if not paper_results:
            return jsonify({"error": "No relevant papers found"}), 404
        
        # Generate context from papers
        arxiv_context = generate_arxiv_context(paper_results)
        
        # Create an enhanced prompt for Gemini
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
        
        # Generate answer using Gemini
        try:
            # Use more tokens and higher temperature for academic analysis
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel(
                "gemini-2.0-flash",
                generation_config={
                    "max_output_tokens": 4096,
                    "temperature": 0.7,
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
            "analysis_type": "academic",
            "paper_count": len(paper_results)
        }
        
        # Log search history for logged-in users
        if current_user.is_authenticated:
            SearchHistory.add_search(
                mongo.db, 
                current_user.get_id(), 
                query, 
                "academic", 
                len(paper_results), 
                paper_results
            )
        
        return jsonify(final_response)
    
    except Exception as e:
        print(f"Unexpected error in deep research: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Authentication routes
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
        
    error = None
    
    if request.method == 'POST':
        email = request.form.get('email_or_username')
        password = request.form.get('password')
        
        if not email or not password:
            error = 'Email/username and password are required'
            return render_template('login.html', error=error)
            
        try:
            # Find user by email or username
            user_data = mongo.db.users.find_one({
                '$or': [
                    {'email': email},
                    {'username': email}
                ],
                'provider': 'local'
            })
            
            if user_data and check_password_hash(user_data.get('password_hash', ''), password):
                user = User(user_data)
                login_user(user)
                
                # Update last login timestamp
                mongo.db.users.update_one(
                    {'_id': user_data['_id']},
                    {'$set': {'last_login': datetime.utcnow()}}
                )
                
                # Get next parameter or default to profile
                next_page = request.args.get('next', 'profile')
                return redirect(url_for(next_page))
            else:
                error = 'Invalid email/username or password'
        except Exception as e:
            print(f"Error during login: {str(e)}")
            error = 'An error occurred. Please try again later.'
    
    return render_template('login.html', error=error)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('signup.html', error='All fields are required')
            
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html', error='Passwords do not match')
            
        # Check if username or email already exists
        try:
            existing_user = mongo.db.users.find_one({
                '$or': [
                    {'username': username},
                    {'email': email}
                ]
            })
            
            if existing_user:
                if existing_user.get('username') == username:
                    flash('Username already taken', 'error')
                    return render_template('signup.html', error='Username already taken')
                else:
                    flash('Email already registered', 'error')
                    return render_template('signup.html', error='Email already registered')
                    
            # Hash the password
            password_hash = generate_password_hash(password, method='pbkdf2:sha256')
            
            # Create new user
            new_user = {
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'provider': 'local',
                'provider_id': None,
                'created_at': datetime.now(),
                'picture': None,
                'last_login': datetime.now()
            }
            
            result = mongo.db.users.insert_one(new_user)
            
            if result.inserted_id:
                # Create user object and login
                new_user['_id'] = result.inserted_id
                user = User(new_user)
                login_user(user)
                
                flash('Account created successfully!', 'success')
                return redirect(url_for('profile'))
            else:
                flash('Failed to create account', 'error')
                return render_template('signup.html', error='Failed to create account')
                
        except Exception as e:
            print(f"Error during signup: {str(e)}")
            flash('An error occurred during signup', 'error')
            return render_template('signup.html', error='An error occurred during signup')
    
    return render_template('signup.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out successfully", "success")
    return redirect(url_for("home"))

@app.route("/account/settings")
@login_required
def account_settings():
    return render_template("account_settings.html", user=current_user)

@app.route("/account/update", methods=["POST"])
@login_required
def update_account():
    try:
        data = request.form
        username = data.get("username", "").strip()
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        
        # Update user profile
        success, message = current_user.update_profile(
            mongo.db,
            username=username if username else None,
            name=name if name else None,
            email=email if email else None
        )
        
        if success:
            flash(message, "success")
        else:
            flash(message, "error")
            
        return redirect(url_for("account_settings"))
        
    except Exception as e:
        print(f"Error updating account: {e}")
        flash("An error occurred while updating your account", "error")
        return redirect(url_for("account_settings"))

@app.route("/account/change-password", methods=["POST"])
@login_required
def change_password():
    try:
        data = request.form
        current_password = data.get("current_password", "")
        new_password = data.get("new_password", "")
        confirm_password = data.get("confirm_password", "")
        
        # Basic validation
        if new_password != confirm_password:
            flash("New passwords do not match", "error")
            return redirect(url_for("account_settings"))
            
        if len(new_password) < 8:
            flash("New password must be at least 8 characters long", "error")
            return redirect(url_for("account_settings"))
        
        # Change password
        success, message = current_user.change_password(mongo.db, current_password, new_password)
        
        if success:
            flash(message, "success")
        else:
            flash(message, "error")
            
        return redirect(url_for("account_settings"))
        
    except Exception as e:
        print(f"Error changing password: {e}")
        flash("An error occurred while changing your password", "error")
        return redirect(url_for("account_settings"))

@app.route("/account/delete", methods=["POST"])
@login_required
def delete_account():
    try:
        # Confirm with password for email users
        if current_user.provider == 'email':
            password = request.form.get("password", "")
            if not current_user.check_password(password):
                flash("Incorrect password", "error")
                return redirect(url_for("account_settings"))
        
        # Delete account
        success, message = current_user.delete_account(mongo.db)
        
        if success:
            logout_user()
            session.clear()
            flash(message, "success")
            return redirect(url_for("home"))
        else:
            flash(message, "error")
            return redirect(url_for("account_settings"))
            
    except Exception as e:
        print(f"Error deleting account: {e}")
        flash("An error occurred while deleting your account", "error")
        return redirect(url_for("account_settings"))

# Google login route
@app.route("/login/google")
def google_login():
    redirect_uri = url_for("google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route("/login/google/callback")
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.parse_id_token(token)
    
    # Check if user exists
    user = User.get_by_provider_id(mongo.db, "google", user_info["sub"])
    
    if not user:
        # Create a new user
        user_data = {
            "email": user_info.get("email", ""),
            "username": user_info.get("email", "").split("@")[0],
            "name": user_info.get("name", ""),
            "picture": user_info.get("picture", ""),
            "provider": "google",
            "provider_id": user_info["sub"],
        }
        user = User(user_data).save(mongo.db)
    else:
        # Update user info
        user.name = user_info.get("name", user.name)
        user.picture = user_info.get("picture", user.picture)
        user.save(mongo.db)
    
    login_user(user)
    return redirect(url_for("home"))

# GitHub login route
@app.route("/login/github")
def github_login():
    redirect_uri = url_for("github_callback", _external=True)
    print(f"GitHub callback URL: {redirect_uri}")
    return oauth.github.authorize_redirect(redirect_uri)

@app.route("/login/github/callback")
def github_callback():
    try:
        token = oauth.github.authorize_access_token()
        resp = oauth.github.get("user", token=token)
        user_info = resp.json()
        
        # Get email (GitHub doesn't include it in basic profile)
        resp = oauth.github.get("user/emails", token=token)
        emails = resp.json()
        email = next((email["email"] for email in emails if email["primary"]), None)
        
        print(f"GitHub login: {user_info.get('login')}, ID: {user_info.get('id')}")
        
        # Verify MongoDB connection before proceeding
        try:
            mongo.db.command('ping')
        except Exception as e:
            print(f"MongoDB not available during GitHub callback: {e}")
            flash("Database connection issue. Please try again later.", "error")
            return redirect(url_for("login"))
        
        # Check if user exists
        user = User.get_by_provider_id(mongo.db, "github", str(user_info["id"]))
        
        if not user:
            # Create a new user
            user_data = {
                "email": email or "",
                "username": user_info.get("login", ""),
                "name": user_info.get("name", ""),
                "picture": user_info.get("avatar_url", ""),
                "provider": "github",
                "provider_id": str(user_info["id"]),
            }
            print(f"Creating new GitHub user: {user_data['username']}")
            user = User(user_data).save(mongo.db)
        else:
            # Update user info
            user.name = user_info.get("name", user.name)
            user.picture = user_info.get("avatar_url", user.picture)
            user.save(mongo.db)
        
        login_user(user)
        return redirect(url_for("home"))
    except Exception as e:
        print(f"Error in GitHub callback: {e}")
        flash(f"Authentication error: {str(e)}", "error")
        return redirect(url_for("login"))

# Apple login route
@app.route("/login/apple")
def apple_login():
    redirect_uri = url_for("apple_callback", _external=True)
    return oauth.apple.authorize_redirect(redirect_uri)

@app.route("/login/apple/callback")
def apple_callback():
    token = oauth.apple.authorize_access_token()
    user_info = oauth.apple.parse_id_token(token)
    
    # Check if user exists
    user = User.get_by_provider_id(mongo.db, "apple", user_info["sub"])
    
    if not user:
        # Create a new user
        user_data = {
            "email": user_info.get("email", ""),
            "username": user_info.get("email", "").split("@")[0],
            "name": user_info.get("name", {}).get("firstName", "") + " " + user_info.get("name", {}).get("lastName", ""),
            "picture": "",  # Apple doesn't provide profile pictures
            "provider": "apple",
            "provider_id": user_info["sub"],
        }
        user = User(user_data).save(mongo.db)
    
    login_user(user)
    return redirect(url_for("home"))

# User profile and settings
@app.route("/profile")
@login_required
def profile():
    search_history = SearchHistory.get_user_history(mongo.db, current_user.get_id())
    favorites = Favorite.get_favorites(mongo.db, current_user.get_id())
    recommendations = Recommendation.get_recommendations(mongo.db, current_user.get_id())
    
    return render_template(
        "profile.html", 
        user=current_user, 
        search_history=search_history,
        favorites=favorites,
        recommendations=recommendations
    )

# API routes for user data
@app.route("/api/history", methods=["GET"])
@login_required
def get_history():
    history = SearchHistory.get_user_history(mongo.db, current_user.get_id())
    # Convert ObjectId to string for JSON serialization
    for item in history:
        item["_id"] = str(item["_id"])
        item["user_id"] = str(item["user_id"])
        item["timestamp"] = item["timestamp"].isoformat()
    
    return jsonify({"history": history})

@app.route("/api/history/clear", methods=["POST"])
@login_required
def clear_history():
    SearchHistory.clear_history(mongo.db, current_user.get_id())
    return jsonify({"success": True})

@app.route("/api/favorites", methods=["GET"])
@login_required
def get_favorites():
    favorites = Favorite.get_favorites(mongo.db, current_user.get_id())
    # Convert ObjectId to string for JSON serialization
    for item in favorites:
        item["_id"] = str(item["_id"])
        item["user_id"] = str(item["user_id"])
        item["timestamp"] = item["timestamp"].isoformat()
    
    return jsonify({"favorites": favorites})

@app.route("/api/favorites/add", methods=["POST"])
@login_required
def add_favorite():
    data = request.json
    Favorite.add_favorite(
        mongo.db,
        current_user.get_id(),
        data.get("name", "Unnamed"),
        data.get("query", ""),
        data.get("search_type", "quick"),
        data.get("result"),
        data.get("paper")
    )
    return jsonify({"success": True})

@app.route("/api/favorites/remove", methods=["POST"])
@login_required
def remove_favorite():
    data = request.json
    Favorite.remove_favorite(mongo.db, data.get("favorite_id"))
    return jsonify({"success": True})

@app.route("/api/recommendations", methods=["GET"])
@login_required
def get_recommendations():
    recommendations = Recommendation.get_recommendations(mongo.db, current_user.get_id())
    return jsonify({"recommendations": recommendations})

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            return render_template('forgot_password.html', error='Email is required')
            
        # Check if user exists
        user = mongo.db.users.find_one({'email': email})
        if not user:
            # Don't reveal that the user doesn't exist for security reasons
            return render_template('forgot_password.html', 
                                  message='If an account with that email exists, a password reset link has been sent.')
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        expiration = datetime.utcnow() + timedelta(seconds=PASSWORD_RESET_EXPIRATION)
        
        # Store token in database
        mongo.db.password_resets.insert_one({
            'email': email,
            'token': reset_token,
            'expires_at': expiration
        })
        
        # Create reset link
        reset_url = url_for('reset_password', token=reset_token, _external=True)
        
        # Send email
        subject = "Reset Your Sentino Password"
        html_body = f"""
        <html>
            <body>
                <h2>Reset Your Password</h2>
                <p>You've requested to reset your password. Click the link below to set a new password:</p>
                <p><a href="{reset_url}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <p>Thanks,<br>The Sentino Team</p>
            </body>
        </html>
        """
        
        if send_email(email, subject, html_body):
            return render_template('forgot_password.html', 
                                  message='If an account with that email exists, a password reset link has been sent.')
        else:
            return render_template('forgot_password.html', 
                                  error='Failed to send reset email. Please try again later.')
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Check if token exists and is valid
    reset_record = mongo.db.password_resets.find_one({
        'token': token,
        'expires_at': {'$gt': datetime.utcnow()}
    })
    
    if not reset_record:
        flash('Password reset link is invalid or has expired')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            return render_template('reset_password.html', token=token, error='Both fields are required')
            
        if password != confirm_password:
            return render_template('reset_password.html', token=token, error='Passwords do not match')
            
        if len(password) < 8:
            return render_template('reset_password.html', token=token, error='Password must be at least 8 characters')
            
        # Update user's password
        user = mongo.db.users.find_one({'email': reset_record['email']})
        
        if not user:
            return render_template('reset_password.html', token=token, error='User not found')
            
        # Hash new password
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Update user record
        mongo.db.users.update_one(
            {'_id': user['_id']},
            {'$set': {'password_hash': password_hash}}
        )
        
        # Remove used token
        mongo.db.password_resets.delete_one({'token': token})
        
        # Redirect to login page with success message
        flash('Your password has been updated successfully. You can now log in with your new password.')
        return redirect(url_for('login'))
        
    return render_template('reset_password.html', token=token)

@app.route("/login/email", methods=["POST"])
def email_login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    email_or_username = request.form.get('email_or_username')
    password = request.form.get('password')
    
    if not email_or_username or not password:
        return redirect(url_for('login', error='Email/username and password are required'))
        
    try:
        # Find user by email or username
        user_data = mongo.db.users.find_one({
            '$or': [
                {'email': email_or_username},
                {'username': email_or_username}
            ],
            'provider': 'local'
        })
        
        if user_data and check_password_hash(user_data.get('password_hash', ''), password):
            user = User(user_data)
            login_user(user)
            
            # Update last login timestamp
            mongo.db.users.update_one(
                {'_id': user_data['_id']},
                {'$set': {'last_login': datetime.utcnow()}}
            )
            
            # Get next parameter or default to profile
            next_page = request.args.get('next', 'profile')
            return redirect(url_for(next_page))
        else:
            return redirect(url_for('login', error='Invalid email/username or password'))
    except Exception as e:
        print(f"Error during email login: {str(e)}")
        return redirect(url_for('login', error='An error occurred. Please try again later.'))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', debug=True, port=port)