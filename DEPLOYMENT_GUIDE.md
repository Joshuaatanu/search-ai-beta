# Deployment Guide - Sentino AI

## 🚀 Deployment to Render

This guide explains how to deploy Sentino AI to Render or any cloud platform.

---

## ✅ Issue Fixed: Config Module Import Error

**Problem:** The `config.py` file is in `.gitignore` and doesn't get deployed, causing `ModuleNotFoundError: No module named 'config'`.

**Solution:** All files now use a try/except pattern to import from `config.py` locally, but fall back to environment variables in deployment.

### Files Updated:
- ✅ `utils/document_processor.py`
- ✅ `utils/rag_system.py`
- ✅ `utils/security.py`
- ✅ `utils/ieee_xplore.py`
- ✅ `celery_app.py`

---

## 🔐 Required Environment Variables

### **1. API Keys (Required)**

#### **GEMINI_API_KEY** (Required)
- Google Gemini API key for AI features
- Get from: https://makersuite.google.com/app/apikey
- Example: `AIzaSyA...`

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

#### **MONGODB_URI** (Required)
- MongoDB connection string
- Get from: MongoDB Atlas or your MongoDB instance
- Example: `mongodb+srv://username:password@cluster.mongodb.net/sentino`

```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/sentino
```

#### **SECRET_KEY** (Required)
- Flask secret key for session encryption
- Generate: `python -c "import secrets; print(secrets.token_hex(32))"`

```bash
SECRET_KEY=your_generated_secret_key_here
```

---

### **2. Optional API Keys**

#### **IEEE_API_KEY** (Optional)
- IEEE Xplore API key for academic paper search
- Get from: https://developer.ieee.org/
- If not provided, IEEE search will be skipped

```bash
IEEE_API_KEY=your_ieee_api_key_here
```

#### **DEEPSEEK_API_KEY** (Optional)
- DeepSeek API key (if using DeepSeek AI)
- Get from: DeepSeek platform

```bash
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

---

### **3. Document Processing Configuration**

#### **MAX_FILE_SIZE** (Optional)
- Maximum file upload size in bytes
- Default: `10485760` (10MB)
- Recommended: `52428800` (50MB)

```bash
MAX_FILE_SIZE=52428800
```

#### **ALLOWED_EXTENSIONS** (Optional)
- Comma-separated list of allowed file extensions
- Default: `pdf,docx,txt`

```bash
ALLOWED_EXTENSIONS=pdf,docx,txt
```

#### **CHUNK_SIZE** (Optional)
- Text chunk size for document processing
- Default: `500`
- Recommended: `1000` for better context

```bash
CHUNK_SIZE=1000
```

#### **CHUNK_OVERLAP** (Optional)
- Overlap between chunks for better context
- Default: `50`
- Recommended: `200`

```bash
CHUNK_OVERLAP=200
```

#### **EMBEDDING_MODEL** (Optional)
- Sentence transformer model for embeddings
- Default: `all-MiniLM-L6-v2`
- Options: `all-MiniLM-L6-v2`, `all-mpnet-base-v2`

```bash
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

---

### **4. Security Configuration**

#### **TOTP_ISSUER_NAME** (Optional)
- Name shown in 2FA authenticator apps
- Default: `Sentino AI`

```bash
TOTP_ISSUER_NAME=Sentino AI
```

---

### **5. Celery Configuration (Optional)**

#### **CELERY_BROKER_URL** (Optional)
- Redis URL for Celery task queue
- Default: `redis://localhost:6379/0`
- Required for: Background tasks, async processing

```bash
CELERY_BROKER_URL=redis://your-redis-url:6379/0
```

#### **CELERY_RESULT_BACKEND** (Optional)
- Redis URL for Celery results
- Default: `redis://localhost:6379/0`

```bash
CELERY_RESULT_BACKEND=redis://your-redis-url:6379/0
```

---

## 📝 Setting Environment Variables on Render

### Step-by-Step:

1. **Go to your Render dashboard**
   - Navigate to your web service
   - Click on "Environment" tab

2. **Add Required Variables:**

```env
# Required
GEMINI_API_KEY=AIzaSyA...your_key_here
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/sentino
SECRET_KEY=your_generated_secret_key_here

# Recommended
MAX_FILE_SIZE=52428800
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Optional
IEEE_API_KEY=your_ieee_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
TOTP_ISSUER_NAME=Sentino AI
```

3. **Click "Save Changes"**
   - Render will automatically redeploy with new environment variables

---

## 🔧 Local Development Setup

### 1. **Create `.env` file:**

```bash
# Copy from .env.example
cp .env.example .env
```

### 2. **Edit `.env` file:**

```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key
MONGODB_URI=mongodb://localhost:27017/sentino
SECRET_KEY=dev-secret-key-change-in-production

# Document Processing
MAX_FILE_SIZE=52428800
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Optional
IEEE_API_KEY=your_ieee_key
DEEPSEEK_API_KEY=your_deepseek_key
```

### 3. **Create `config.py` (for local development only):**

```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# IEEE Xplore API Configuration
IEEE_XPLORE_API_KEY = os.getenv("IEEE_API_KEY", "")
IEEE_XPLORE_API_URL = "https://ieeexploreapi.ieee.org/api/v1/search/articles"

# Document Processing Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "pdf,docx,txt").split(",")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Security Configuration
TOTP_ISSUER_NAME = os.getenv("TOTP_ISSUER_NAME", "Sentino AI")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

# Celery Configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/sentino")

# Debug mode
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
```

### 4. **Install dependencies:**

```bash
pip install -r requirements.txt
```

### 5. **Run the application:**

```bash
python app.py
```

---

## 🐳 Docker Deployment (Optional)

### **Dockerfile:**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

### **docker-compose.yml:**

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - MONGODB_URI=${MONGODB_URI}
      - SECRET_KEY=${SECRET_KEY}
      - MAX_FILE_SIZE=52428800
      - CHUNK_SIZE=1000
      - CHUNK_OVERLAP=200
      - EMBEDDING_MODEL=all-MiniLM-L6-v2
    depends_on:
      - mongodb
      - redis

  mongodb:
    image: mongo:6
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  mongodb_data:
```

### **Run with Docker:**

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop
docker-compose down
```

---

## 🔍 Troubleshooting

### **Error: ModuleNotFoundError: No module named 'config'**

**Solution:** This is now fixed. The code automatically falls back to environment variables. Make sure all required environment variables are set on Render.

### **Error: GEMINI_API_KEY not found**

**Solution:** 
1. Check if `GEMINI_API_KEY` is set in Render environment variables
2. Verify the key is correct (starts with `AIzaSy`)
3. Check if the key has proper permissions in Google Cloud Console

### **Error: MongoDB connection failed**

**Solution:**
1. Verify `MONGODB_URI` is correct
2. Check if MongoDB Atlas IP whitelist includes `0.0.0.0/0` (allow all)
3. Verify username and password are correct
4. Test connection string using MongoDB Compass

### **Error: ModuleNotFoundError: No module named 'sentence_transformers'**

**Solution:**
1. Make sure `requirements.txt` includes `sentence-transformers`
2. Rebuild on Render
3. Check build logs for pip install errors

### **Error: Out of memory during model loading**

**Solution:**
1. Increase Render instance size (Standard or higher)
2. Use smaller embedding model: `all-MiniLM-L6-v2` instead of `all-mpnet-base-v2`
3. Add lazy loading for models

---

## 📊 Render Build Settings

### **Build Command:**

```bash
pip install -r requirements.txt
```

### **Start Command:**

```bash
gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app
```

### **Environment:**

- **Python Version:** 3.9 or higher
- **Region:** Choose closest to your users
- **Instance Type:** Standard (minimum) for production

---

## ⚡ Performance Optimization for Production

### **1. Add Gunicorn to requirements.txt:**

```txt
gunicorn==21.2.0
```

### **2. Create `Procfile` (for some platforms):**

```
web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app
```

### **3. Update app.py for production:**

```python
# At the end of app.py
if __name__ == '__main__':
    # Development server
    if os.getenv('FLASK_ENV') == 'development':
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        # Production: use gunicorn instead
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
```

---

## 🔐 Security Best Practices

### **1. Strong SECRET_KEY:**

```bash
# Generate a strong key
python -c "import secrets; print(secrets.token_hex(32))"
```

### **2. Environment Variables Security:**

- ✅ Never commit `.env` file to git
- ✅ Never commit `config.py` to git (already in `.gitignore`)
- ✅ Use strong, unique keys for each environment
- ✅ Rotate keys periodically
- ✅ Use Render's secret management

### **3. MongoDB Security:**

- ✅ Use strong passwords
- ✅ Enable IP whitelisting in MongoDB Atlas
- ✅ Use connection string with SSL: `?ssl=true`
- ✅ Create database-specific users (not admin)

### **4. API Key Security:**

- ✅ Restrict Gemini API key to specific domains
- ✅ Set usage quotas and alerts
- ✅ Monitor API usage regularly
- ✅ Rotate keys if compromised

---

## 📈 Monitoring & Logging

### **1. Enable Logging on Render:**

- View logs in Render dashboard
- Set up log aggregation (Papertrail, Loggly)
- Monitor error rates

### **2. Set up Health Checks:**

Add to `app.py`:

```python
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }), 200
```

### **3. Monitor Performance:**

- Use Render's built-in metrics
- Set up Sentry for error tracking
- Monitor API response times
- Track database query performance

---

## ✅ Deployment Checklist

### **Before Deployment:**

- [ ] All environment variables set on Render
- [ ] MongoDB Atlas configured and accessible
- [ ] Gemini API key valid and working
- [ ] `requirements.txt` up to date
- [ ] `.gitignore` includes `config.py` and `.env`
- [ ] Build command configured
- [ ] Start command configured

### **After Deployment:**

- [ ] Test homepage loads
- [ ] Test user registration
- [ ] Test user login
- [ ] Test academic search
- [ ] Test PDF upload
- [ ] Test AI features
- [ ] Check logs for errors
- [ ] Verify database connections
- [ ] Test mobile responsiveness

---

## 🆘 Support

If you encounter issues:

1. **Check Render Logs:**
   - Dashboard → Your Service → Logs
   - Look for error messages

2. **Test Locally:**
   - Run app locally with same environment variables
   - Check if issue persists

3. **Verify Environment Variables:**
   - Double-check all required vars are set
   - Verify no typos in variable names

4. **Database Connection:**
   - Test MongoDB URI with MongoDB Compass
   - Check IP whitelist in MongoDB Atlas

5. **Contact Support:**
   - Render Support: https://render.com/docs/support
   - GitHub Issues: [Your repo]

---

## 📚 Additional Resources

- **Render Documentation:** https://render.com/docs
- **Flask Deployment Guide:** https://flask.palletsprojects.com/en/2.3.x/deploying/
- **MongoDB Atlas:** https://www.mongodb.com/docs/atlas/
- **Google Gemini API:** https://ai.google.dev/docs
- **Gunicorn Documentation:** https://docs.gunicorn.org/

---

**Last Updated:** November 13, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅

---

## 🎉 Success!

Your Sentino AI application should now be successfully deployed on Render with all environment variables properly configured!

Visit your deployed URL and verify all features are working correctly.

**Happy Researching!** 🚀📚

