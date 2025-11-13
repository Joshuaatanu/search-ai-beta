# Sentino AI - Academic Research Platform

## 📚 Project Overview

Sentino AI is a comprehensive academic research platform that combines multi-source academic search, AI-powered analysis, and document processing capabilities. Built with Flask, MongoDB, and Google's Gemini AI, it provides researchers with powerful tools for literature review, paper analysis, and research planning.

---

## 🎯 Core Features

### 1. **Multi-Source Academic Search**

Search across 6+ academic databases simultaneously:

- **arXiv** - Open-access preprints in STEM fields
- **Semantic Scholar** - AI-powered academic search
- **CORE** - World's largest collection of open access papers
- **Crossref** - Scholarly metadata database
- **PubMed** - Biomedical and life sciences literature
- **IEEE Xplore** - Engineering and technology research

**Key Capabilities:**
- ✅ Unified search interface
- ✅ Adjustable result count (5-50 papers)
- ✅ Multiple sorting options (relevance, date, citations)
- ✅ Sci-Hub integration for PDF access
- ✅ Real-time status checking for Sci-Hub mirrors
- ✅ Duplicate detection and deduplication
- ✅ Rich metadata display (authors, citations, venue, year)

---

### 2. **AI-Powered Analysis** (Gemini 2.0 Flash)

#### a) **Automatic Paper Analysis**
- Comprehensive analysis of search results
- Identifies key themes and research gaps
- Provides methodology recommendations
- Suggests future research directions
- Markdown-formatted output with sections:
  - Key Themes & Trends
  - Research Gaps
  - Methodology Insights
  - Future Directions

#### b) **Quick Search**
- Fast AI-powered answers to general questions
- 2-3 paragraph responses
- Simple, clear language
- Ideal for quick queries and definitions
- Auto-saves to search history

#### c) **Deep Analysis**
- Comprehensive analysis with multiple perspectives
- 7-section structured output:
  1. Overview
  2. Key Perspectives
  3. Detailed Analysis
  4. Challenges & Opportunities
  5. Practical Implications
  6. Critical Evaluation
  7. Conclusions
- Evidence-based insights
- Longer, more detailed responses

#### d) **Literature Review Generator**
- Automatically generates structured literature reviews
- Multiple citation formats:
  - APA (American Psychological Association)
  - MLA (Modern Language Association)
  - Chicago (Author-Date)
  - IEEE (Numbered citations)
  - Harvard (Author-Date system)
- Includes:
  - Abstract/Summary
  - Introduction
  - Thematic Analysis
  - Key Findings
  - Research Gaps
  - Conclusions
  - References (properly formatted)
- Export as text file
- Copy to clipboard functionality

#### e) **Methodology Analysis**
- Detailed research methodology recommendations
- Based on paper abstracts and research questions
- Provides:
  - Research design suggestions
  - Data collection methods
  - Analysis techniques
  - Best practices
  - Potential challenges
  - Recommendations
- Modal-based interface

#### f) **Research Framework Generator**
- Comprehensive research planning tool
- Generates 10-section framework:
  1. Research Question/Hypothesis
  2. Theoretical Framework
  3. Methodology
  4. Data Collection
  5. Analysis Strategy
  6. Expected Outcomes
  7. Limitations
  8. Ethical Considerations
  9. Timeline
  10. References
- Based on current search context
- Downloadable as text file

#### g) **Academic Draft Generator**
- Full paper draft creation
- Customizable sections (up to 15)
- Based on search results and user specifications
- AI-generated content for each section
- Professional academic formatting
- Export functionality

---

### 3. **PDF Analysis & RAG System**

#### a) **PDF Upload & Processing**
- Drag & drop interface
- PDF-only validation
- Automatic text extraction
- Document chunking for optimal retrieval
- Semantic embeddings generation
- MongoDB storage with user association

#### b) **Document Management**
- List all uploaded documents
- View chunk count and upload date
- Select documents for analysis
- Delete documents
- User-specific document library

#### c) **AI-Powered Chat**
- Chat with your PDF documents
- Context-aware responses using RAG
- Auto-generated document summaries
- Conversation history
- Source references with confidence scores
- Chunk-level citations
- Real-time responses

**RAG Technical Stack:**
- Document processing with PyPDF2
- Semantic chunking for context preservation
- Embedding generation for vector search
- Retrieval-Augmented Generation
- Gemini AI for response generation
- MongoDB for vector storage

---

### 4. **User Authentication & Management**

#### a) **Authentication System**
- Email/Username + Password login
- Secure password hashing (Werkzeug)
- Flask-Login session management
- Protected routes with @login_required
- Persistent sessions
- Logout functionality

#### b) **User Registration**
- Username (min 3 characters)
- Email validation
- Password strength meter (weak/medium/strong)
- Password confirmation
- Real-time validation
- Flash messages for feedback

#### c) **User Profile**
- Beautiful gradient header with avatar
- User information display
- Account statistics dashboard:
  - Total searches count
  - PDF documents count
  - Member since date
  - Last login timestamp
- Recent search history (quick access)
- Profile picture support

#### d) **Account Settings**
- Update profile information:
  - Username
  - Full name
  - Email address
- Change password:
  - Current password verification
  - New password with confirmation
  - Minimum 8 characters
- Account statistics view
- Danger zone:
  - Clear all search history
  - Delete account (coming soon)

---

### 5. **Search History Management**

#### a) **Automatic History Saving**
- All searches saved for logged-in users
- Captures:
  - Search query
  - Search type (academic/quick/deep)
  - Papers found
  - AI analysis
  - Timestamp
  - Result count

#### b) **History Interface**
- Collapsible history panel
- Recent searches with timestamps
- Smart date formatting ("2 hours ago", "Just now")
- Click to re-run searches
- Search type badges
- Result count display

#### c) **History Management**
- View full history (up to 20 recent)
- Clear all history (with confirmation)
- Filtered by user
- Sorted by date (newest first)
- Accessible from multiple locations

---

### 6. **Trending Topics**

- Real-time trending research topics
- AI-generated explanations
- Topic categories
- Modal-based display
- Auto-refresh capability
- Clickable topics for instant search

---

### 7. **Sci-Hub Integration**

#### a) **Mirror Status Checker**
- Real-time mirror availability testing
- Multiple mirror URLs
- Response time measurement
- Status indicators (active/inactive)
- Auto-selection of fastest mirror

#### b) **PDF Access**
- Direct Sci-Hub links for each paper
- DOI-based lookup
- Alternative access methods
- Legal disclaimer
- One-click access

---

## 🎨 UI/UX Features

### Design System

#### **Color Palette**
- Primary: Blue gradient (#667eea → #764ba2)
- Secondary: Purple (#764ba2)
- Success: Green (#10b981)
- Error: Red (#ef4444)
- Warning: Orange (#f59e0b)
- Surface: White (#ffffff)
- Background: Light gray (#f9fafb)

#### **Components**
- 6 button styles (primary, secondary, outline, success, danger, icon)
- 4 card types (standard, flat, bordered, gradient)
- Complete form system with validation
- 3 modal sizes (standard, large, extra-large)
- 4 notification types (success, error, info, warning)
- Loading states and spinners
- Responsive grid system

#### **Typography**
- Font: Inter (sans-serif)
- Headings: 700 weight
- Body: 400 weight
- Code: JetBrains Mono

#### **Animations**
- Fade in/out
- Slide animations
- Hover effects
- Loading spinners
- Smooth transitions (0.3s)

### Responsive Design

- **Mobile-First Approach**
- **5 Breakpoints:**
  - XS: < 480px (Mobile)
  - SM: 480px - 768px (Large mobile)
  - MD: 768px - 1024px (Tablet)
  - LG: 1024px - 1440px (Desktop)
  - XL: > 1440px (Large desktop)

### Navigation

#### **Desktop Navigation**
- Logo (left)
- Main nav items (center):
  - Home
  - Papers
  - Quick Search
  - Deep Analysis
  - PDF Analysis
- User section (right):
  - Search history button
  - User menu dropdown
  - Login/Signup (guests)

#### **Mobile Navigation**
- Hamburger menu
- Full-screen dropdown
- Touch-friendly targets (44px min)
- Smooth animations
- Auto-close after selection

### Unified Header Component

- Consistent across all pages
- Server-side rendering (Jinja2)
- Active page indicators
- Hover effects
- Responsive breakpoints
- Icon + text labels

---

## 🗄️ Technical Architecture

### Backend Stack

- **Framework:** Flask 3.0+
- **Database:** MongoDB (PyMongo)
- **Authentication:** Flask-Login
- **AI:** Google Gemini 2.0 Flash
- **PDF Processing:** PyPDF2, pdfplumber
- **Vector Storage:** MongoDB (embeddings)
- **Task Queue:** Celery + Redis (background jobs)
- **API Clients:** Custom multi-source API wrapper

### Frontend Stack

- **HTML5** with Jinja2 templating
- **CSS3** with custom design system
- **Vanilla JavaScript** (no frameworks)
- **Font Awesome** 6.0 icons
- **Responsive design** with CSS Grid & Flexbox

### Database Schema

#### **Users Collection**
```javascript
{
  _id: ObjectId,
  username: String (unique),
  email: String (unique),
  password_hash: String,
  full_name: String,
  profile_pic: String,
  account_type: String,
  email_verified: Boolean,
  created_at: Date,
  last_login: Date
}
```

#### **Search History Collection**
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  query: String,
  search_type: String, // 'academic', 'quick', 'deep'
  results_count: Number,
  papers: Array,
  ai_analysis: String,
  methodology_analysis: String,
  timestamp: Date
}
```

#### **Documents Collection**
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  filename: String,
  upload_date: Date,
  file_path: String,
  chunks: Array, // Text chunks with embeddings
  metadata: Object
}
```

### API Endpoints

#### **Authentication**
- `POST /login` - User login
- `POST /signup` - User registration
- `GET /logout` - User logout

#### **Search**
- `POST /academic-search` - Multi-source search
- `POST /api/quick-search` - Quick AI search
- `POST /api/deep-analysis` - Deep AI analysis

#### **User**
- `GET /api/user/info` - User information
- `GET /api/user/search-history` - Search history
- `DELETE /api/user/clear-history` - Clear history
- `GET /profile` - Profile page
- `GET /settings` - Settings page
- `POST /account/update` - Update profile
- `POST /account/change-password` - Change password

#### **PDF Analysis**
- `GET /pdf-analysis` - PDF analysis page
- `POST /api/upload-pdf` - Upload PDF
- `POST /api/analyze-pdf` - Get AI summary
- `POST /api/chat-with-pdf` - Chat with document
- `GET /api/user-documents` - List user PDFs
- `DELETE /api/delete-document/<id>` - Delete PDF

#### **AI Features**
- `POST /api/generate-literature-review` - Generate review
- `POST /api/analyze-methodology` - Methodology analysis
- `POST /api/generate-research-framework` - Research framework
- `POST /api/generate-draft` - Academic draft

#### **Utilities**
- `GET /api/trending` - Trending topics
- `GET /api/scihub-status` - Sci-Hub mirrors status

---

## 🚀 Future Features

### Phase 1: Enhanced AI Capabilities (Q2 2025)

#### 1. **Citation Network Visualization**
- Interactive graph visualization of paper citations
- D3.js or Cytoscape.js integration
- Filter by date, citations, authors
- Export as image or data
- Identify influential papers

#### 2. **Research Question Generator**
- AI-powered research question suggestions
- Based on literature gaps
- Multiple question types (exploratory, explanatory, descriptive)
- Refinement suggestions
- Feasibility assessment

#### 3. **Hypothesis Testing Framework**
- Statistical test recommendations
- Sample size calculators
- Power analysis tools
- Test assumptions checker
- Results interpretation guide

#### 4. **AI Writing Assistant**
- Real-time writing suggestions
- Grammar and style checking
- Academic tone optimization
- Plagiarism detection
- Citation format checking

### Phase 2: Collaboration Features (Q3 2025)

#### 1. **Team Workspaces**
- Shared search history
- Collaborative literature reviews
- Team annotations
- Permission management (owner, editor, viewer)
- Activity logs
- Team chat

#### 2. **Document Annotation System**
- Highlight and comment on PDFs
- Shared annotations
- Tag system
- Search within annotations
- Export annotated PDFs

#### 3. **Project Management**
- Research project organization
- Task tracking
- Milestone setting
- Gantt charts
- Progress reports
- Deadline reminders

#### 4. **Real-Time Collaboration**
- WebSocket integration
- Live editing of shared documents
- Presence indicators
- Conflict resolution
- Version control

### Phase 3: Advanced Analytics (Q4 2025)

#### 1. **Research Impact Tracker**
- Citation tracking for your papers
- H-index calculator
- Impact factor analysis
- Collaboration network
- Geographic distribution
- Trend analysis

#### 2. **Literature Gap Analysis**
- AI-powered gap identification
- Opportunity scoring
- Novelty assessment
- Feasibility ratings
- Recommendation engine

#### 3. **Author Profiling**
- Author expertise mapping
- Collaboration patterns
- Publication trends
- Impact metrics
- Suggested collaborators

#### 4. **Topic Modeling**
- LDA/NMF topic extraction
- Trend visualization over time
- Emerging topics detection
- Topic similarity mapping
- Interactive topic browser

### Phase 4: Integration & Export (Q1 2026)

#### 1. **Reference Manager Integration**
- Zotero sync
- Mendeley integration
- EndNote compatibility
- BibTeX export/import
- RIS format support

#### 2. **LaTeX Support**
- Direct LaTeX export
- Template library
- Bibliography generation
- Equation editor
- Preview mode

#### 3. **Cloud Storage Integration**
- Google Drive sync
- Dropbox integration
- OneDrive support
- Box.com integration
- Auto-backup

#### 4. **API Access**
- RESTful API
- Rate limiting
- API key management
- Documentation
- Client libraries (Python, JavaScript)

### Phase 5: Mobile Applications (Q2 2026)

#### 1. **Mobile Apps**
- iOS native app (Swift)
- Android native app (Kotlin)
- Progressive Web App (PWA)
- Offline mode
- Push notifications
- Biometric authentication

#### 2. **Mobile-Specific Features**
- Voice search
- OCR for paper scanning
- Audio paper summaries
- Bookmark sync
- Quick share

### Phase 6: Advanced AI Features (Q3 2026)

#### 1. **Custom AI Models**
- Fine-tuned models for specific fields
- User-trained models
- Transfer learning
- Model marketplace
- Performance metrics

#### 2. **Multimodal Analysis**
- Image analysis in papers
- Graph/chart extraction
- Table understanding
- Formula recognition
- Video paper summaries

#### 3. **Predictive Analytics**
- Research trend prediction
- Citation count prediction
- Collaboration success prediction
- Grant success estimation
- Field emergence detection

#### 4. **Automated Peer Review**
- AI-assisted review suggestions
- Quality assessment
- Methodology validation
- Statistical analysis checking
- Ethical considerations flagging

### Phase 7: Institutional Features (Q4 2026)

#### 1. **Enterprise Plan**
- SSO integration (SAML, OAuth)
- LDAP support
- Institutional licensing
- Usage analytics
- Admin dashboard
- Bulk user management

#### 2. **Compliance & Security**
- GDPR compliance tools
- Data encryption at rest
- Audit logs
- Access control policies
- Data retention policies

#### 3. **Custom Branding**
- White-label option
- Custom domain
- Logo customization
- Color scheme control
- Email templates

#### 4. **Analytics Dashboard**
- Usage statistics
- User engagement metrics
- Popular searches
- Citation analytics
- ROI tracking

---

## 🔒 Security Features

### Current Implementation

- ✅ Password hashing (Werkzeug)
- ✅ HTTPS enforcement
- ✅ CSRF protection (Flask-WTF)
- ✅ Session security (Flask-Login)
- ✅ Input validation
- ✅ SQL injection prevention (MongoDB)
- ✅ XSS protection
- ✅ Rate limiting (basic)

### Planned Enhancements

- 🔄 Two-factor authentication (2FA)
- 🔄 Email verification
- 🔄 Password reset via email
- 🔄 Advanced rate limiting (Redis)
- 🔄 DDoS protection
- 🔄 API key rotation
- 🔄 Security headers (CSP, HSTS)
- 🔄 Vulnerability scanning
- 🔄 Penetration testing
- 🔄 Security audit logs

---

## 📈 Performance Optimization

### Current Performance

- Average search time: 3-5 seconds
- AI analysis time: 10-20 seconds
- PDF processing time: 5-15 seconds
- Page load time: < 2 seconds
- Mobile performance: Good (85+ Lighthouse score)

### Planned Improvements

- **Caching Strategy:**
  - Redis for search results (1 hour TTL)
  - API response caching
  - Static asset CDN
  - Browser caching policies

- **Database Optimization:**
  - Index optimization
  - Query performance tuning
  - Connection pooling
  - Read replicas

- **Frontend Optimization:**
  - Code splitting
  - Lazy loading
  - Image optimization (WebP)
  - Minification and compression
  - Service workers (PWA)

- **AI Optimization:**
  - Model caching
  - Batch processing
  - Prompt optimization
  - Response streaming

---

## 🌍 Localization & Accessibility

### Planned Features

#### **Internationalization (i18n)**
- Multi-language support:
  - English (default)
  - Spanish
  - French
  - German
  - Chinese
  - Japanese
  - Portuguese
- Translation management system
- Language detection
- User preference storage

#### **Accessibility (a11y)**
- WCAG 2.1 Level AA compliance
- Screen reader optimization
- Keyboard navigation
- High contrast mode
- Font size controls
- Alt text for images
- ARIA labels
- Skip navigation links
- Focus indicators
- Color blind friendly palette

---

## 📊 Analytics & Monitoring

### Current Monitoring

- Basic error logging (Flask logging)
- Console error tracking
- Manual testing

### Planned Monitoring

- **Application Monitoring:**
  - Sentry for error tracking
  - New Relic for APM
  - DataDog for infrastructure
  - Custom dashboards

- **User Analytics:**
  - Google Analytics 4
  - Mixpanel for user behavior
  - Hotjar for heatmaps
  - Custom event tracking

- **Performance Monitoring:**
  - Lighthouse CI
  - WebPageTest integration
  - Core Web Vitals tracking
  - API response time monitoring

---

## 🧪 Testing Strategy

### Planned Testing

#### **Unit Tests**
- Backend route tests (pytest)
- Model tests
- Utility function tests
- API client tests
- Target coverage: 80%+

#### **Integration Tests**
- Database integration
- API integration
- Authentication flow
- Search functionality
- PDF processing

#### **End-to-End Tests**
- Selenium/Playwright
- User flow testing
- Cross-browser testing
- Mobile testing
- Visual regression testing

#### **Performance Tests**
- Load testing (Locust)
- Stress testing
- API endpoint testing
- Database query performance

---

## 📦 Deployment & Infrastructure

### Current Infrastructure

- Single server deployment
- MongoDB Atlas (cloud)
- Static file serving
- Basic monitoring

### Planned Infrastructure

#### **Containerization**
- Docker containers
- Docker Compose for local dev
- Kubernetes orchestration
- Helm charts

#### **CI/CD Pipeline**
- GitHub Actions
- Automated testing
- Automated deployment
- Rolling updates
- Rollback capability

#### **Scalability**
- Load balancer (Nginx)
- Auto-scaling
- Database sharding
- CDN (CloudFlare)
- Message queue (RabbitMQ)

#### **Backup & Recovery**
- Automated daily backups
- Point-in-time recovery
- Disaster recovery plan
- Multi-region deployment

---

## 💰 Monetization Strategy

### Planned Pricing Tiers

#### **Free Tier**
- 20 searches/month
- 5 PDF uploads
- Basic AI features
- Search history (30 days)
- Community support

#### **Pro Tier** ($19/month)
- Unlimited searches
- 100 PDF uploads/month
- Advanced AI features
- Search history (unlimited)
- Priority support
- Export all formats
- No ads

#### **Team Tier** ($49/month, 5 users)
- Everything in Pro
- Team workspaces
- Collaboration tools
- Shared resources
- Admin controls
- Usage analytics
- API access (limited)

#### **Enterprise Tier** (Custom pricing)
- Everything in Team
- Unlimited users
- SSO integration
- Custom branding
- Dedicated support
- SLA guarantee
- On-premise option
- Custom integrations

---

## 🤝 Community & Support

### Planned Community Features

- **Discussion Forums**
- **Research Blog**
- **Tutorial Videos**
- **Webinar Series**
- **User Groups**
- **Feature Voting**
- **Bug Bounty Program**

### Support Channels

- Email support
- Live chat (Pro+)
- Phone support (Enterprise)
- Help center with FAQs
- Video tutorials
- Community forum
- GitHub issues (bugs)

---

## 📄 Documentation Plan

### Developer Documentation

- API documentation (OpenAPI/Swagger)
- Code architecture guide
- Database schema documentation
- Deployment guide
- Contributing guide
- Code style guide

### User Documentation

- Getting started guide
- Feature tutorials
- Video walkthroughs
- Best practices
- FAQ section
- Troubleshooting guide
- Tips & tricks

---

## 🎓 Use Cases

### Academic Researchers
- Literature review for dissertation
- Finding research gaps
- Methodology selection
- Paper discovery
- Citation management

### Graduate Students
- Thesis research
- Paper writing
- Literature organization
- Citation formatting
- Research planning

### Industry Researchers
- Market research
- Competitive analysis
- Patent search
- Technology trends
- Innovation tracking

### Librarians
- Research assistance
- Database searching
- Resource curation
- User training
- Collection development

### Journal Editors
- Paper review
- Quality assessment
- Trend analysis
- Author discovery
- Peer reviewer matching

---

## 🏆 Competitive Advantages

1. **Multi-Source Search** - Single interface for 6+ databases
2. **AI-Powered Analysis** - Gemini 2.0 Flash integration
3. **RAG-Based PDF Chat** - Chat with your research papers
4. **Comprehensive Tools** - Search, analyze, write, cite
5. **Modern UI/UX** - Beautiful, responsive design
6. **Open Architecture** - Extensible and customizable
7. **No Vendor Lock-In** - Export all your data
8. **Privacy-Focused** - User data ownership
9. **Affordable Pricing** - Free tier + reasonable paid plans
10. **Active Development** - Regular feature updates

---

## 📞 Contact & Contributions

### Project Information
- **Repository:** Private (contact for access)
- **License:** Proprietary (commercial licensing available)
- **Version:** 1.0.0 (Beta)
- **Last Updated:** November 13, 2025

### Contributors
- Lead Developer: [Your Name]
- AI Integration: [Team]
- UI/UX Design: [Team]
- Documentation: [Team]

### Contributing
We welcome contributions! Please see our `CONTRIBUTING.md` for guidelines.

### Support
For support, email support@sentino-ai.com or visit our help center.

---

## 🎯 Roadmap Summary

**2025 Q2:** Enhanced AI, Citation Networks  
**2025 Q3:** Collaboration Features, Teams  
**2025 Q4:** Advanced Analytics, Author Profiling  
**2026 Q1:** Integrations, LaTeX, Cloud Storage  
**2026 Q2:** Mobile Apps, Voice Features  
**2026 Q3:** Custom AI, Multimodal Analysis  
**2026 Q4:** Enterprise Features, White-Label  

---

## ✨ Vision Statement

*"To democratize academic research by providing researchers worldwide with powerful, AI-driven tools that accelerate discovery, enhance collaboration, and unlock human potential for innovation."*

---

**Sentino AI - Empowering Research, Accelerating Discovery** 🚀📚

---

*Last updated: November 13, 2025*  
*Version: 1.0.0*  
*Status: Beta Release*

