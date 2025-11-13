# Sentino AI - Quick Start Guide

## Prerequisites

1. Python 3.9+
2. MongoDB running locally or remotely
3. Google Gemini API key

## Setup Instructions

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here
MONGODB_URI=mongodb://localhost:27017/
SECRET_KEY=your_secret_key_here

# Optional
PORT=5000
IEEE_API_KEY=your_ieee_key_if_needed
```

### 2. Install Dependencies

```bash
# Activate virtual environment (if you have one)
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install requirements
pip install -r requirements.txt
```

### 3. Start MongoDB

```bash
# If using local MongoDB
mongod

# Or use MongoDB Atlas (cloud) and update MONGODB_URI
```

### 4. Run the Application

```bash
python app.py
```

The app will start on `http://localhost:5000`

---

## First-Time Usage

### 1. Access the App
Open your browser and go to `http://localhost:5000`

### 2. Create an Account
- Click "Sign Up" in the top right
- Fill in username, email, and password
- Password must be at least 8 characters
- Click "Create Account"

### 3. Perform Your First Search
- Enter a research query (e.g., "machine learning transformers")
- Select sources you want to search
- Click "Search"
- Wait for results and AI analysis

### 4. Explore Features

**Search Results:**
- Click "AI Analysis" on any paper for detailed analysis
- View Sci-Hub availability
- Click paper titles to view abstracts

**Generate Content:**
- Click "Generate Literature Review" for a comprehensive review
- Click "Methodology Analysis" for research methodology guidance
- Click "Research Framework" for complete research planning
- Click "Generate Academic Draft" to create a full paper draft

**Manage History:**
- Click "History" to view your past searches
- Click any history item to re-run that search
- Click "Clear History" to delete all searches

---

## Feature Walkthrough

### Basic Search
1. Enter query in search box
2. Adjust "Results" dropdown (10, 20, or 50)
3. Choose "Sort by" (relevance, date, or updated)
4. Select sources from multi-select (hold Ctrl/Cmd for multiple)
5. Toggle "Include Sci-Hub access" if needed
6. Click "Search"

### Paper Analysis
1. After search results load
2. Find an interesting paper
3. Click "AI Analysis" button on the paper card
4. Read comprehensive analysis in modal
5. Click outside modal or X to close

### Literature Review
1. After search completes
2. Click "Generate Literature Review" button
3. Select review type (systematic, narrative, etc.)
4. Select citation format (APA, MLA, etc.)
5. Wait for generation
6. Click "Export" to save or "Copy" to clipboard

### Methodology Analysis
1. Click "Methodology Analysis" button
2. Enter your research question (auto-filled from search)
3. Select research type
4. Click "Generate Analysis"
5. Read recommendations
6. Export if needed

### Academic Draft Generator
1. Click "Generate Academic Draft" (purple button)
2. Fill in:
   - Research title
   - Research question
   - Research field
   - Research type
   - Citation format
3. Select sections to include
4. Click "Generate Draft"
5. Wait for AI to generate (can take 30-60 seconds)
6. Copy or export the draft

---

## Tips & Tricks

### Search Tips
- Use specific terms for better results
- Select multiple sources for comprehensive coverage
- Sort by date for latest research
- Enable Sci-Hub if you need full-text access

### AI Features
- The more papers in your search results, the better the literature review
- Methodology analysis works best with specific research questions
- Research framework provides comprehensive planning guidance
- Academic draft generator creates publication-ready structure

### User Management
- Your searches are automatically saved when logged in
- Use search history to track your research journey
- History items show result counts and timestamps
- Click history items to quickly re-run searches

### UI/UX
- Hover over buttons to see effects
- Use keyboard shortcuts where available
- Modals can be closed with Escape key
- All notifications auto-dismiss after 3 seconds

---

## Troubleshooting

### "MongoDB connection error"
- Ensure MongoDB is running: `mongod`
- Check MONGODB_URI in .env
- Verify MongoDB port (default: 27017)

### "Gemini API error"
- Check your GEMINI_API_KEY in .env
- Verify your Google Cloud project has Gemini enabled
- Check if you've exceeded free tier quota
- Make sure you're using Gemini 2.0 Flash or 1.5 Flash

### "Search failed"
- Check internet connection
- Some sources may have rate limits
- Try fewer sources
- Wait a moment and try again

### "No papers found"
- Try broader search terms
- Select more sources
- Check spelling
- Try different keywords

### Login/Signup not working
- Clear browser cache
- Check MongoDB is running
- Verify user doesn't already exist (for signup)
- Check browser console for errors

### Features not appearing
- Make sure you're logged in (some features require auth)
- Check JavaScript console for errors
- Refresh the page
- Try a different browser

---

## API Endpoints Reference

### Public Endpoints
- `GET /` - Home page
- `GET /login` - Login page
- `POST /login` - Submit login
- `GET /signup` - Signup page
- `POST /signup` - Submit registration
- `GET /api/user/info` - Check auth status
- `GET /api/sources` - Available sources info
- `GET /api/trending-topics` - Trending topics
- `GET /api/scihub/mirror-status` - Sci-Hub status

### Authenticated Endpoints (Login Required)
- `POST /api/academic-search` - Search papers (history saved if logged in)
- `POST /api/paper-analysis` - Analyze single paper
- `POST /api/research-suggestions` - Research framework
- `POST /api/literature-review` - Generate review
- `POST /api/methodology-analysis` - Methodology guidance
- `POST /api/generate-draft` - Academic draft
- `GET /api/user/search-history` - Get search history
- `POST /api/user/clear-history` - Clear history
- `GET /logout` - Logout

---

## Performance Notes

- First search may take 5-10 seconds (API warm-up)
- AI analysis takes 3-5 seconds per paper
- Literature review generation: 10-20 seconds
- Academic draft generation: 30-60 seconds
- Search history loads instantly
- Trending topics cached for performance

---

## Security Notes

- Passwords are hashed using werkzeug's pbkdf2:sha256
- Sessions are server-side with secure cookies
- CORS is enabled for API access
- MongoDB credentials should never be committed
- API keys should be in .env only

---

## Development Notes

### Adding New Features
1. Add route in `app.py`
2. Add frontend function in `static/js/academic.js`
3. Add button/trigger in `templates/academic_research.html`
4. Add styling in `static/css/academic.css`
5. Test thoroughly
6. Update documentation

### Code Structure
```
app.py                          # Main Flask application
models.py                       # User, SearchHistory, Favorite models
templates/
  ├── academic_research.html    # Main search interface
  ├── login.html                # Login page
  └── signup.html               # Signup page
static/
  ├── css/academic.css          # All styles
  └── js/academic.js            # All JavaScript
utils/
  ├── scihub_api.py            # Sci-Hub integration
  └── multi_source_api.py       # Academic sources
```

---

## Support

For issues or questions:
1. Check this guide
2. Check FEATURES_IMPLEMENTATION.md
3. Check browser console for errors
4. Check Flask logs in terminal
5. Verify environment variables
6. Test MongoDB connection

---

## Getting the Most Out of Sentino AI

1. **Start with a clear research question**
2. **Use multiple academic sources**
3. **Enable Sci-Hub for full-text access**
4. **Generate literature review early** in your research
5. **Use methodology analysis** to plan your approach
6. **Create drafts incrementally** as you gather more papers
7. **Review your search history** to track progress
8. **Export everything** - reviews, analyses, drafts
9. **Re-run searches** periodically for new papers
10. **Leverage AI analysis** for quick paper evaluation

---

Enjoy researching with Sentino AI! 🎓🔬📚







