#!/usr/bin/env python3
"""
Sentino AI - Academic Research Platform with Sci-Hub Integration
Focused on academic paper search, analysis, and access through Sci-Hub
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, make_response
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai
import arxiv
import re
from datetime import datetime, timedelta
import requests
import json
import logging
from typing import Dict, List, Optional
import time

# Import our Sci-Hub integration
from utils.scihub_api import scihub_api

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "sentino-academic-research-key")

# Configuration
PAPERS_PER_PAGE = 20
MAX_SEARCH_RESULTS = 100

def query_gemini(prompt, context=""):
    """Enhanced Gemini query function for academic analysis with fallback"""
    # Check if API key is available
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        logger.warning("Gemini API key not configured, using fallback analysis")
        return generate_fallback_analysis(prompt, context)
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Enhanced prompt for academic research
        academic_prompt = f"""
You are an expert academic research assistant. Analyze the following query and provide comprehensive insights.

Query: {prompt}

Context: {context}

Please provide:
1. Key research themes and concepts
2. Relevant academic fields and disciplines
3. Suggested search terms for finding related papers
4. Important considerations for this research topic

Respond in a clear, academic tone suitable for researchers.
"""
        
        response = model.generate_content(academic_prompt)
        if response and response.text:
            return response.text
        else:
            logger.warning("Empty response from Gemini API, using fallback")
            return generate_fallback_analysis(prompt, context)
        
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        logger.info("Using fallback analysis due to API error")
        return generate_fallback_analysis(prompt, context)

def generate_fallback_analysis(prompt, context=""):
    """Generate basic analysis when AI is unavailable"""
    return f"""
**Analysis for: {prompt}**

**Note: This is a basic analysis generated without AI assistance. For comprehensive AI-powered insights, please configure your Gemini API key.**

**Key Research Areas:**
Based on your query, this research appears to relate to multiple academic domains. Consider exploring:
- Primary research methodologies in this field
- Theoretical frameworks commonly applied
- Recent developments and emerging trends
- Cross-disciplinary applications

**Research Approach:**
1. **Literature Search Strategy**: Use multiple academic databases (arXiv, PubMed, IEEE Xplore, Google Scholar)
2. **Methodology Considerations**: Consider both quantitative and qualitative approaches
3. **Theoretical Framework**: Identify established theories and emerging paradigms
4. **Current Gaps**: Look for unexplored areas and methodological innovations

**Next Steps:**
- Conduct systematic literature search
- Identify key researchers and institutions
- Analyze methodological approaches in recent papers
- Consider interdisciplinary perspectives

**Limitations:**
This analysis is generated without AI assistance. For comprehensive insights including detailed methodology recommendations, literature synthesis, and research planning, please configure the Gemini API key in your .env file.
"""

def format_citation(paper, citation_format="apa", reference_number=None):
    """Format a paper citation in the specified format"""
    title = paper.get('title', 'Unknown Title')
    authors = paper.get('authors', 'Unknown Author')
    year = paper.get('published_year', 'n.d.')
    url = paper.get('url', '')
    doi = paper.get('doi', '')
    categories = paper.get('categories', [])
    
    # Clean up authors - take first few if too many
    if len(authors) > 100:
        authors_list = authors.split(', ')
        if len(authors_list) > 3:
            authors = f"{authors_list[0]}, {authors_list[1]}, et al."
    
    # Format based on citation style
    if citation_format.lower() == "apa":
        citation = f"{authors} ({year}). {title}. arXiv preprint."
        if doi:
            citation += f" https://doi.org/{doi}"
        elif url:
            citation += f" Retrieved from {url}"
    
    elif citation_format.lower() == "mla":
        citation = f"{authors}. \"{title}.\" arXiv preprint, {year}."
        if url:
            citation += f" Web. {url}"
    
    elif citation_format.lower() == "chicago":
        citation = f"{authors}. \"{title}.\" arXiv preprint, {year}."
        if url:
            citation += f" {url}"
    
    elif citation_format.lower() == "ieee":
        if reference_number:
            citation = f"[{reference_number}] {authors}, \"{title},\" arXiv preprint, {year}."
        else:
            citation = f"{authors}, \"{title},\" arXiv preprint, {year}."
        if doi:
            citation += f" doi: {doi}"
    
    elif citation_format.lower() == "harvard":
        citation = f"{authors} {year}, '{title}', arXiv preprint."
        if url:
            citation += f" Available at: {url}"
    
    else:  # Default to APA
        citation = f"{authors} ({year}). {title}. arXiv preprint."
        if doi:
            citation += f" https://doi.org/{doi}"
        elif url:
            citation += f" Retrieved from {url}"
    
    return citation

def generate_references_section(papers, citation_format="apa"):
    """Generate a properly formatted references section"""
    references = []
    
    for i, paper in enumerate(papers, 1):
        citation = format_citation(paper, citation_format, reference_number=i)
        references.append(citation)
    
    # Sort references alphabetically for most formats (except IEEE which uses numbers)
    if citation_format.lower() != "ieee":
        references.sort()
    
    references_text = "\n".join(references)
    
    return f"""
## REFERENCES

{references_text}

---
**Citation Format**: {citation_format.upper()}
**Total References**: {len(references)}
"""

def create_in_text_citations(papers, citation_format="apa"):
    """Create in-text citation mappings for papers"""
    citations = {}
    
    for i, paper in enumerate(papers, 1):
        title = paper.get('title', 'Unknown Title')
        authors = paper.get('authors', 'Unknown Author')
        year = paper.get('published_year', 'n.d.')
        
        # Get first author surname for in-text citations
        first_author = authors.split(',')[0].strip()
        if ' ' in first_author:
            surname = first_author.split()[-1]
        else:
            surname = first_author
        
        if citation_format.lower() == "apa":
            if ',' in authors and 'et al' not in authors:
                citations[title] = f"({surname} et al., {year})"
            else:
                citations[title] = f"({surname}, {year})"
        
        elif citation_format.lower() == "mla":
            citations[title] = f"({surname})"
        
        elif citation_format.lower() == "chicago":
            citations[title] = f"({surname} {year})"
        
        elif citation_format.lower() == "ieee":
            citations[title] = f"[{i}]"
        
        elif citation_format.lower() == "harvard":
            citations[title] = f"({surname} {year})"
        
        else:  # Default to APA
            citations[title] = f"({surname}, {year})"
    
    return citations

def query_arxiv(query, max_results=20, sort_by=arxiv.SortCriterion.Relevance):
    """Enhanced arXiv search with better metadata extraction"""
    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_by
        )
        
        papers = []
        for result in arxiv.Client(page_size=max_results, delay_seconds=1, num_retries=3).results(search):
            try:
                published_date = result.published.strftime("%Y-%m-%d") if result.published else "Unknown"
                published_year = result.published.year if result.published else None
                authors = ", ".join(author.name for author in result.authors) if result.authors else "Unknown"
                
                # Extract arXiv ID
                if result.entry_id:
                    arxiv_id = result.entry_id.split("/")[-1]
                else:
                    arxiv_id = "unknown"
                
                # Extract DOI if available
                doi = None
                if hasattr(result, 'doi') and result.doi:
                    doi = result.doi
                
                # Extract categories
                categories = result.categories if hasattr(result, 'categories') else []
                
                paper = {
                    "title": result.title or "Unknown Title",
                    "authors": authors,
                    "summary": result.summary or "No summary available",
                    "pdf_url": result.pdf_url or "#",
                    "published": published_date,
                    "published_year": published_year,
                    "arxiv_id": arxiv_id,
                    "doi": doi,
                    "url": result.entry_id,
                    "categories": categories,
                    "source": "arXiv"
                }
                papers.append(paper)
            except Exception as e:
                logger.error(f"Error processing paper: {str(e)}")
                continue
            
        return papers
    except Exception as e:
        logger.error(f"Error querying arXiv: {str(e)}")
        return []

def analyze_papers_with_ai(papers, query):
    """Comprehensive AI analysis of papers with literature review insights"""
    try:
        if not papers:
            return papers, ""
        
        # Create detailed summary of papers for comprehensive analysis
        papers_summary = []
        for i, paper in enumerate(papers[:15]):  # Analyze top 15 papers
            summary_text = paper.get('summary', '')[:300] + '...' if len(paper.get('summary', '')) > 300 else paper.get('summary', '')
            papers_summary.append(f"""
{i+1}. **{paper['title']}**
   Authors: {paper['authors']}
   Year: {paper['published_year']}
   Categories: {', '.join(paper.get('categories', []))}
   Abstract: {summary_text}
""")
        
        analysis_prompt = f"""
As an expert academic research analyst, provide a comprehensive analysis of these papers for the query: "{query}"

Papers for Analysis:
{chr(10).join(papers_summary)}

Provide a detailed analysis covering:

**1. RESEARCH LANDSCAPE OVERVIEW**
- Current state of research in this field
- Evolution of research themes over time
- Key research gaps identified

**2. THEMATIC ANALYSIS**
- Primary research themes and clusters
- Methodological approaches being used
- Theoretical frameworks employed
- Emerging trends and directions

**3. LITERATURE REVIEW INSIGHTS**
- Most influential papers in this collection (by relevance and impact)
- Key findings and contributions from each major theme
- Contradictions or debates in the literature
- Consensus areas and established knowledge

**4. METHODOLOGY ANALYSIS**
- Common methodological approaches
- Innovative methods being employed
- Methodological gaps and opportunities
- Best practices identified

**5. RESEARCH OPPORTUNITIES**
- Unexplored research questions
- Methodological innovations needed
- Interdisciplinary opportunities
- Future research directions

**6. PRACTICAL IMPLICATIONS**
- Real-world applications
- Policy implications
- Industry relevance

Provide specific paper references (by number) to support each point. Make this analysis suitable for researchers planning their own studies.
"""
        
        analysis = query_gemini(analysis_prompt)
        return papers, analysis
    except Exception as e:
        logger.error(f"Error in AI analysis: {str(e)}")
        return papers, ""

@app.route('/')
def index():
    """Main academic research interface"""
    return render_template('academic_research.html')

@app.route('/api/academic-search', methods=['POST'])
def academic_search():
    """Enhanced academic search with AI analysis and Sci-Hub integration"""
    try:
        data = request.json
        query = data.get("query", "").strip()
        max_results = min(data.get("max_results", PAPERS_PER_PAGE), MAX_SEARCH_RESULTS)
        include_scihub = data.get("include_scihub", True)
        sort_by = data.get("sort_by", "relevance")
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        logger.info(f"Academic search: query='{query}', max_results={max_results}")
        
        # Map sort options
        sort_mapping = {
            "relevance": arxiv.SortCriterion.Relevance,
            "date": arxiv.SortCriterion.SubmittedDate,
            "updated": arxiv.SortCriterion.LastUpdatedDate
        }
        sort_criterion = sort_mapping.get(sort_by, arxiv.SortCriterion.Relevance)
        
        # Search arXiv
        papers = query_arxiv(query, max_results, sort_criterion)
        
        if not papers:
            return jsonify({
                "success": True,
                "papers": [],
                "total_count": 0,
                "analysis": "No papers found for this query.",
                "scihub_stats": {"total_papers": 0, "available_on_scihub": 0, "availability_rate": 0}
            })
        
        # Enhance with Sci-Hub if requested
        scihub_stats = {"total_papers": len(papers), "available_on_scihub": 0, "availability_rate": 0}
        if include_scihub:
            logger.info("Enhancing papers with Sci-Hub access information...")
            papers = scihub_api.batch_enhance_papers(papers)
            scihub_stats = scihub_api.get_availability_stats(papers)
        
        # AI analysis of papers
        papers, ai_analysis = analyze_papers_with_ai(papers, query)
        
        return jsonify({
            "success": True,
            "papers": papers,
            "total_count": len(papers),
            "analysis": ai_analysis,
            "scihub_stats": scihub_stats,
            "query": query,
            "sort_by": sort_by
        })
            
    except Exception as e:
        logger.error(f"Error in academic search: {str(e)}")
        return jsonify({"error": "Search failed"}), 500

@app.route('/api/paper-analysis', methods=['POST'])
def analyze_paper():
    """Comprehensive AI analysis of a specific paper"""
    try:
        data = request.json
        paper_title = data.get("title", "")
        paper_abstract = data.get("abstract", "")
        paper_authors = data.get("authors", "")
        paper_year = data.get("year", "")
        paper_categories = data.get("categories", [])
        
        if not paper_title:
            return jsonify({"error": "Paper title is required"}), 400
        
        analysis_prompt = f"""
As an expert academic reviewer, provide a comprehensive analysis of this research paper:

**Paper Details:**
Title: {paper_title}
Authors: {paper_authors}
Year: {paper_year}
Categories: {', '.join(paper_categories) if paper_categories else 'Not specified'}
Abstract: {paper_abstract}

**Provide a detailed analysis covering:**

**1. RESEARCH CONTRIBUTION ANALYSIS**
- Novel contributions and innovations
- Significance to the field
- Originality and creativity
- Theoretical vs. practical contributions

**2. METHODOLOGY EVALUATION**
- Research design and approach
- Data collection methods
- Analysis techniques employed
- Methodological rigor and validity
- Reproducibility considerations

**3. THEORETICAL FRAMEWORK**
- Underlying theoretical foundations
- Conceptual models used
- Integration with existing theories
- Theoretical gaps addressed

**4. KEY FINDINGS & IMPLICATIONS**
- Primary research findings
- Statistical significance and effect sizes
- Practical implications
- Policy implications
- Industry applications

**5. STRENGTHS & LIMITATIONS**
- Methodological strengths
- Analytical rigor
- Limitations and constraints
- Potential biases
- Generalizability issues

**6. LITERATURE POSITIONING**
- How this work builds on previous research
- Gaps in existing literature addressed
- Contradictions with previous findings
- Consensus with established knowledge

**7. FUTURE RESEARCH DIRECTIONS**
- Unanswered questions raised
- Methodological improvements needed
- Extensions and applications
- Interdisciplinary opportunities

**8. QUALITY ASSESSMENT**
- Overall methodological quality (1-10 scale)
- Clarity of presentation
- Completeness of analysis
- Ethical considerations

**9. RECOMMENDED CITATIONS**
- Key papers that should be cited alongside this work
- Foundational papers in this area
- Recent relevant developments

Provide specific, actionable insights suitable for researchers, reviewers, and practitioners.
"""
        
        analysis = query_gemini(analysis_prompt)
        
        return jsonify({
            "success": True,
            "analysis": analysis,
            "paper_title": paper_title
        })
        
    except Exception as e:
        logger.error(f"Error in paper analysis: {str(e)}")
        return jsonify({"error": "Analysis failed"}), 500

@app.route('/api/research-suggestions', methods=['POST'])
def research_suggestions():
    """Generate comprehensive research suggestions based on query"""
    try:
        data = request.json
        query = data.get("query", "").strip()
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        suggestions_prompt = f"""
As an expert research advisor, provide comprehensive research guidance for the query: "{query}"

**RESEARCH FRAMEWORK:**

**1. RESEARCH QUESTIONS & HYPOTHESES**
- 7-10 specific, testable research questions
- Primary and secondary research hypotheses
- Null and alternative hypotheses where applicable
- Research objectives (descriptive, explanatory, exploratory)

**2. LITERATURE REVIEW STRATEGY**
- Key databases to search (beyond arXiv)
- Essential search terms and Boolean combinations
- Inclusion/exclusion criteria for literature
- Systematic review methodology recommendations
- Citation analysis approaches

**3. THEORETICAL FOUNDATIONS**
- Relevant theoretical frameworks
- Conceptual models to consider
- Interdisciplinary theories that apply
- Emerging theoretical perspectives

**4. METHODOLOGY RECOMMENDATIONS**
- Quantitative approaches (experimental, survey, observational)
- Qualitative methods (interviews, ethnography, case studies)
- Mixed-methods designs
- Novel methodological approaches
- Data collection strategies

**5. KEY RESEARCHERS & INSTITUTIONS**
- Leading researchers in this field
- Influential research groups and labs
- Key institutions and universities
- Emerging scholars to follow

**6. PUBLICATION VENUES**
- Top-tier journals in this area
- Relevant conferences and symposiums
- Special issues and themed collections
- Open access publication opportunities

**7. RESEARCH GAPS & OPPORTUNITIES**
- Underexplored areas
- Methodological innovations needed
- Interdisciplinary opportunities
- Practical applications lacking research

**8. FUNDING & COLLABORATION**
- Potential funding sources
- Grant opportunities
- Collaboration possibilities
- Industry partnerships

**9. ETHICAL CONSIDERATIONS**
- IRB/Ethics approval requirements
- Data privacy and security issues
- Participant consent considerations
- Potential ethical dilemmas

**10. TIMELINE & MILESTONES**
- Suggested research timeline (6 months to 3 years)
- Key milestones and deliverables
- Publication strategy
- Dissemination plan

Provide specific, actionable guidance suitable for researchers at all career stages.
"""
        
        suggestions = query_gemini(suggestions_prompt)
        
        return jsonify({
            "success": True,
            "suggestions": suggestions,
            "query": query
        })
        
    except Exception as e:
        logger.error(f"Error generating research suggestions: {str(e)}")
        return jsonify({"error": "Failed to generate suggestions"}), 500

@app.route('/api/literature-review', methods=['POST'])
def generate_literature_review():
    """Generate a comprehensive literature review based on papers"""
    try:
        data = request.json
        papers = data.get("papers", [])
        query = data.get("query", "")
        review_type = data.get("review_type", "systematic")  # systematic, narrative, scoping
        citation_format = data.get("citation_format", "apa")  # apa, mla, chicago, ieee, harvard
        
        if not papers:
            return jsonify({"error": "Papers list is required"}), 400
        
        # Generate structured analysis of papers first
        paper_analysis = analyze_papers_structure(papers, query)
        
        # Create in-text citations mapping
        in_text_citations = create_in_text_citations(papers, citation_format)
        
        # Generate references section
        references_section = generate_references_section(papers, citation_format)
        
        # Create detailed paper summaries with citations
        papers_detail = []
        for i, paper in enumerate(papers[:20]):  # Limit to top 20 papers
            title = paper.get('title', 'Unknown Title')
            citation = in_text_citations.get(title, f"(Paper {i+1})")
            papers_detail.append(f"""
Paper {i+1}: {paper.get('title', 'Unknown Title')} {citation}
Authors: {paper.get('authors', 'Unknown')}
Year: {paper.get('published_year', 'Unknown')}
Abstract: {paper.get('summary', 'No abstract available')[:400]}...
Categories: {', '.join(paper.get('categories', []))}
DOI: {paper.get('doi', 'Not available')}
""")
        
        review_prompt = f"""
As an expert academic writer, create a comprehensive literature review on "{query}" based on the following papers.

**Citation Format**: {citation_format.upper()}
**In-text Citation Examples**: {list(in_text_citations.values())[:3]}

**Papers to Review:**
{chr(10).join(papers_detail)}

**Structural Analysis:**
{paper_analysis}

**Create a {review_type.title()} Literature Review with the following structure:**

**1. INTRODUCTION**
- Define the scope and objectives of this review
- Explain the significance of this research area
- Outline the review methodology and selection criteria

**2. THEORETICAL BACKGROUND**
- Key theoretical frameworks identified in the literature
- Evolution of theoretical understanding
- Competing theories and paradigms

**3. METHODOLOGICAL APPROACHES**
- Overview of research methods used across studies
- Strengths and limitations of different approaches
- Methodological trends and innovations
- Quality assessment of methodologies

**4. THEMATIC ANALYSIS**
- Major themes and research clusters
- Convergent findings across studies
- Divergent findings and contradictions
- Gaps in current knowledge

**5. CHRONOLOGICAL DEVELOPMENT**
- Evolution of research over time
- Milestone studies and breakthrough findings
- Shifts in research focus and methodology
- Emerging trends

**6. CRITICAL ANALYSIS**
- Strengths of the current literature
- Limitations and weaknesses identified
- Methodological concerns
- Theoretical gaps

**7. SYNTHESIS OF FINDINGS**
- Consensus areas in the literature
- Unresolved debates and controversies
- Integration of findings across studies
- Implications for theory and practice

**8. RESEARCH GAPS AND FUTURE DIRECTIONS**
- Identified gaps in current research
- Methodological improvements needed
- Theoretical developments required
- Practical applications to explore

**9. CONCLUSIONS**
- Summary of key insights
- Implications for researchers and practitioners
- Recommendations for future research

**10. METHODOLOGICAL APPENDIX**
- Review methodology details
- Search strategy and databases used
- Inclusion/exclusion criteria
- Quality assessment framework

**IMPORTANT CITATION INSTRUCTIONS:**
- Use {citation_format.upper()} format for all citations
- Include in-text citations throughout the review using the format: {list(in_text_citations.values())[0] if in_text_citations else "(Author, Year)"}
- Reference papers by their assigned citations from the list above
- Ensure proper citation placement after key statements and findings
- Include a complete References section at the end

Make this suitable for publication in an academic journal with proper {citation_format.upper()} citations throughout.
"""
        
        review = query_gemini(review_prompt)
        
        # If AI failed, generate a structured review using our analysis
        if not review or "basic analysis generated without AI" in review:
            review = generate_structured_literature_review(papers, query, review_type, paper_analysis, citation_format, in_text_citations)
        
        # Always append references section
        if not "## REFERENCES" in review and not "# REFERENCES" in review:
            review += f"\n\n{references_section}"
        
        return jsonify({
            "success": True,
            "literature_review": review,
            "query": query,
            "review_type": review_type,
            "citation_format": citation_format,
            "papers_analyzed": len(papers),
            "structural_analysis": paper_analysis,
            "references": references_section
        })
        
    except Exception as e:
        logger.error(f"Error generating literature review: {str(e)}")
        return jsonify({"error": "Failed to generate literature review"}), 500

def analyze_papers_structure(papers, query):
    """Analyze paper structure and extract key information"""
    if not papers:
        return "No papers provided for analysis."
    
    # Temporal analysis
    years = [p.get('published_year') for p in papers if p.get('published_year')]
    year_range = f"{min(years)}-{max(years)}" if years else "Unknown"
    
    # Category analysis
    all_categories = []
    for paper in papers:
        if paper.get('categories'):
            all_categories.extend(paper['categories'])
    
    from collections import Counter
    category_counts = Counter(all_categories)
    top_categories = category_counts.most_common(5)
    
    # Author analysis
    all_authors = []
    for paper in papers:
        if paper.get('authors'):
            authors = paper['authors'].split(', ')
            all_authors.extend(authors)
    
    author_counts = Counter(all_authors)
    prolific_authors = author_counts.most_common(5)
    
    analysis = f"""
**STRUCTURAL ANALYSIS OF {len(papers)} PAPERS**

**Temporal Distribution:**
- Publication years: {year_range}
- Total papers: {len(papers)}
- Recent papers (last 3 years): {len([p for p in papers if p.get('published_year', 0) >= 2021])}

**Research Categories:**
- Primary categories: {', '.join([cat[0] for cat in top_categories[:3]])}
- Category distribution: {dict(top_categories)}

**Author Analysis:**
- Unique authors: {len(set(all_authors))}
- Most prolific authors: {', '.join([f"{author[0]} ({author[1]} papers)" for author in prolific_authors[:3]])}

**Methodological Indicators:**
- Papers with experimental keywords: {len([p for p in papers if any(keyword in p.get('summary', '').lower() for keyword in ['experiment', 'empirical', 'study'])])}
- Papers with theoretical keywords: {len([p for p in papers if any(keyword in p.get('summary', '').lower() for keyword in ['theory', 'theoretical', 'framework'])])}
- Papers with review keywords: {len([p for p in papers if any(keyword in p.get('summary', '').lower() for keyword in ['review', 'survey', 'overview'])])}
"""
    
    return analysis

def generate_structured_literature_review(papers, query, review_type, structural_analysis, citation_format="apa", in_text_citations=None):
    """Generate a structured literature review without AI"""
    
    # Sort papers by year
    sorted_papers = sorted(papers, key=lambda x: x.get('published_year', 0), reverse=True)
    
    # Generate citations if not provided
    if not in_text_citations:
        in_text_citations = create_in_text_citations(papers, citation_format)
    
    review = f"""
# {review_type.title()} Literature Review: {query}

## 1. INTRODUCTION

This {review_type} literature review examines the current state of research on "{query}" based on an analysis of {len(papers)} academic papers. The review aims to synthesize existing knowledge, identify research gaps, and provide directions for future research.

### Scope and Objectives
- Analyze current research trends in {query}
- Identify methodological approaches and theoretical frameworks
- Synthesize key findings and contributions
- Highlight research gaps and future opportunities

### Review Methodology
- Database: arXiv academic papers
- Search strategy: Keyword-based search for "{query}"
- Inclusion criteria: Relevant academic papers with available abstracts
- Analysis period: Recent publications with focus on emerging trends

{structural_analysis}

## 2. THEORETICAL BACKGROUND

The literature on {query} draws from multiple theoretical frameworks and disciplinary perspectives. Based on the analysis of included papers, several key theoretical approaches emerge:

### Key Theoretical Frameworks
The reviewed papers demonstrate diverse theoretical foundations, reflecting the interdisciplinary nature of research in this area. Common theoretical approaches include:

- Empirical research methodologies
- Theoretical modeling and framework development  
- Applied research with practical implications
- Cross-disciplinary integration approaches

## 3. METHODOLOGICAL APPROACHES

### Research Design Patterns
The reviewed literature employs various methodological approaches:

**Quantitative Methods:**
- Experimental designs and controlled studies
- Statistical analysis and data modeling
- Computational approaches and simulations

**Qualitative Methods:**
- Case study methodologies
- Theoretical analysis and conceptual development
- Literature reviews and meta-analyses

**Mixed Methods:**
- Combined quantitative and qualitative approaches
- Multi-phase research designs
- Triangulation strategies

## 4. THEMATIC ANALYSIS

### Major Research Themes

Based on the analysis of {len(papers)} papers, several major themes emerge:

"""
    
    # Add paper summaries by theme with proper citations
    for i, paper in enumerate(sorted_papers[:10], 1):
        title = paper.get('title', 'Unknown Title')
        citation = in_text_citations.get(title, f"(Paper {i})")
        review += f"""
**{title}** {citation}
- Authors: {paper.get('authors', 'Unknown')}
- Year: {paper.get('published_year', 'Unknown')}
- Key contribution: {paper.get('summary', 'No abstract available')[:200]}...
- Categories: {', '.join(paper.get('categories', []))}

"""
    
    review += f"""
## 5. CHRONOLOGICAL DEVELOPMENT

The research in {query} has evolved significantly over time, with notable developments in recent years:

### Recent Trends ({max([p.get('published_year', 0) for p in papers if p.get('published_year')]) if papers else 'Recent'} and beyond)
- Increased focus on practical applications
- Integration of computational methods
- Cross-disciplinary collaboration
- Methodological innovations

## 6. CRITICAL ANALYSIS

### Strengths of Current Literature
- Diverse methodological approaches
- Growing body of empirical evidence
- Strong theoretical foundations in established areas
- Increasing interdisciplinary collaboration

### Limitations and Gaps
- Limited longitudinal studies
- Need for more standardized methodologies
- Gaps in cross-cultural research
- Limited replication studies

## 7. SYNTHESIS OF FINDINGS

### Consensus Areas
The literature shows general agreement on:
- The importance of methodological rigor
- The need for interdisciplinary approaches
- The value of both theoretical and practical contributions

### Ongoing Debates
Key areas of ongoing discussion include:
- Optimal methodological approaches
- Theoretical framework selection
- Practical application strategies
- Future research priorities

## 8. RESEARCH GAPS AND FUTURE DIRECTIONS

### Identified Gaps
1. **Methodological Gaps**: Need for more standardized approaches
2. **Theoretical Gaps**: Limited integration of emerging theories
3. **Empirical Gaps**: Insufficient longitudinal and replication studies
4. **Practical Gaps**: Limited real-world application studies

### Future Research Opportunities
- Development of novel methodological approaches
- Integration of emerging technologies
- Cross-disciplinary collaboration
- Longitudinal and comparative studies

## 9. CONCLUSIONS

This {review_type} literature review of {len(papers)} papers on "{query}" reveals a dynamic and evolving field with significant research activity. The literature demonstrates:

- Strong methodological diversity
- Growing theoretical sophistication
- Increasing practical relevance
- Substantial opportunities for future research

### Implications for Researchers
- Consider interdisciplinary approaches
- Focus on methodological rigor
- Address identified research gaps
- Build on existing theoretical foundations

### Implications for Practitioners
- Apply evidence-based approaches
- Consider multiple methodological perspectives
- Stay current with emerging trends
- Contribute to practice-research integration

## 10. METHODOLOGICAL APPENDIX

### Search Strategy
- Primary database: arXiv
- Search terms: "{query}"
- Time period: Recent publications
- Language: English

### Inclusion Criteria
- Relevant to research question
- Available abstract/summary
- Academic quality standards
- Accessible through search database

### Analysis Framework
- Thematic analysis approach
- Chronological organization
- Methodological categorization
- Quality assessment considerations

---

**Note:** This literature review was generated using structured analysis techniques. For enhanced AI-powered insights and deeper analytical capabilities, configure the Gemini API key in your environment settings.

**Total Papers Analyzed:** {len(papers)}
**Review Type:** {review_type.title()}
**Citation Format:** {citation_format.upper()}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    # Add references section
    references_section = generate_references_section(papers, citation_format)
    review += f"\n\n{references_section}"
    
    return review

@app.route('/api/methodology-analysis', methods=['POST'])
def methodology_analysis():
    """Analyze and suggest research methodologies with fallback"""
    try:
        data = request.json
        research_question = data.get("research_question", "")
        papers = data.get("papers", [])
        research_type = data.get("research_type", "empirical")  # empirical, theoretical, applied
        citation_format = data.get("citation_format", "apa")  # apa, mla, chicago, ieee, harvard
        
        if not research_question:
            return jsonify({"error": "Research question is required"}), 400
        
        # Analyze methodologies from papers if provided
        methodology_context = ""
        paper_methods_analysis = ""
        in_text_citations = {}
        references_section = ""
        
        if papers:
            # Generate citations for papers
            in_text_citations = create_in_text_citations(papers, citation_format)
            references_section = generate_references_section(papers, citation_format)
            
            methods_used = []
            paper_methods_analysis = analyze_paper_methodologies(papers)
            for paper in papers[:10]:
                title = paper.get('title', 'Unknown')
                citation = in_text_citations.get(title, f"(Paper {len(methods_used)+1})")
                methods_used.append(f"- {title} {citation}: {paper.get('summary', '')[:200]}...")
            methodology_context = f"""
**Methodologies observed in related literature:**
{chr(10).join(methods_used)}

{paper_methods_analysis}
"""
        
        methodology_prompt = f"""
As a research methodology expert, provide comprehensive methodology guidance for this research question: "{research_question}"

Research Type: {research_type.title()}
Citation Format: {citation_format.upper()}

{methodology_context}

**METHODOLOGY ANALYSIS & RECOMMENDATIONS:**
**Note: Include proper {citation_format.upper()} citations when referencing the literature above.**

**1. RESEARCH DESIGN FRAMEWORK**
- Appropriate research paradigm (positivist, interpretivist, pragmatic)
- Research design type (experimental, quasi-experimental, descriptive, exploratory)
- Justification for chosen design
- Alternative designs and their trade-offs

**2. QUANTITATIVE APPROACHES**
- Experimental designs (RCT, factorial, crossover)
- Survey methodologies (cross-sectional, longitudinal)
- Observational studies (cohort, case-control)
- Statistical analysis methods required
- Sample size calculations and power analysis

**3. QUALITATIVE APPROACHES**
- Interview methodologies (structured, semi-structured, unstructured)
- Focus group designs
- Ethnographic approaches
- Case study methodologies
- Grounded theory applications
- Phenomenological approaches

**4. MIXED-METHODS DESIGNS**
- Sequential explanatory design
- Sequential exploratory design
- Concurrent triangulation
- Concurrent embedded design
- Integration strategies

**5. DATA COLLECTION STRATEGIES**
- Primary data collection methods
- Secondary data sources
- Instrument development and validation
- Pilot study recommendations
- Data quality assurance measures

**6. SAMPLING METHODOLOGY**
- Target population definition
- Sampling frame considerations
- Probability sampling methods
- Non-probability sampling approaches
- Sample size justification
- Recruitment strategies

**7. DATA ANALYSIS PLAN**
- Descriptive analysis approach
- Inferential statistical methods
- Qualitative analysis techniques (thematic, content, narrative)
- Software recommendations (R, SPSS, NVivo, Atlas.ti)
- Validity and reliability measures

**8. ETHICAL CONSIDERATIONS**
- IRB/Ethics approval requirements
- Informed consent procedures
- Data privacy and confidentiality
- Risk assessment and mitigation
- Vulnerable population considerations

**9. VALIDITY & RELIABILITY**
- Internal validity threats and controls
- External validity considerations
- Construct validity measures
- Reliability assessment methods
- Triangulation strategies

**10. IMPLEMENTATION TIMELINE**
- Phase-by-phase methodology timeline
- Resource requirements
- Potential challenges and solutions
- Quality checkpoints
- Contingency planning

**11. INNOVATIVE METHODOLOGICAL APPROACHES**
- Digital and computational methods
- Big data analytics approaches
- Machine learning applications
- Crowdsourcing methodologies
- Virtual and remote data collection

**12. REPORTING AND DISSEMINATION**
- Reporting standards (CONSORT, STROBE, COREQ)
- Publication strategy
- Data sharing protocols
- Replication considerations

Provide specific, actionable methodology recommendations with justifications for each choice.
"""
        
        analysis = query_gemini(methodology_prompt)
        
        # If AI failed, generate structured methodology analysis
        if not analysis or "basic analysis generated without AI" in analysis:
            analysis = generate_structured_methodology_analysis(research_question, research_type, papers, paper_methods_analysis, citation_format, in_text_citations)
        
        # Always append references section if papers were provided
        if papers and not "## REFERENCES" in analysis and not "# REFERENCES" in analysis:
            analysis += f"\n\n{references_section}"
        
        return jsonify({
            "success": True,
            "methodology_analysis": analysis,
            "research_question": research_question,
            "research_type": research_type,
            "citation_format": citation_format,
            "paper_methods_context": paper_methods_analysis,
            "references": references_section if papers else None
        })
        
    except Exception as e:
        logger.error(f"Error in methodology analysis: {str(e)}")
        return jsonify({"error": "Failed to generate methodology analysis"}), 500

def analyze_paper_methodologies(papers):
    """Analyze methodological approaches in the provided papers"""
    if not papers:
        return "No papers provided for methodology analysis."
    
    # Keywords for different methodological approaches
    quant_keywords = ['experiment', 'statistical', 'quantitative', 'survey', 'regression', 'correlation', 'analysis', 'data', 'sample']
    qual_keywords = ['qualitative', 'interview', 'case study', 'ethnographic', 'phenomenological', 'grounded theory']
    mixed_keywords = ['mixed methods', 'mixed-methods', 'triangulation', 'sequential', 'concurrent']
    theory_keywords = ['theoretical', 'framework', 'model', 'conceptual', 'theory']
    
    method_counts = {
        'quantitative': 0,
        'qualitative': 0,
        'mixed_methods': 0,
        'theoretical': 0,
        'computational': 0,
        'experimental': 0,
        'survey': 0,
        'case_study': 0
    }
    
    for paper in papers:
        summary = paper.get('summary', '').lower()
        title = paper.get('title', '').lower()
        text = summary + ' ' + title
        
        if any(keyword in text for keyword in quant_keywords):
            method_counts['quantitative'] += 1
        if any(keyword in text for keyword in qual_keywords):
            method_counts['qualitative'] += 1
        if any(keyword in text for keyword in mixed_keywords):
            method_counts['mixed_methods'] += 1
        if any(keyword in text for keyword in theory_keywords):
            method_counts['theoretical'] += 1
        if any(keyword in text for keyword in ['computational', 'algorithm', 'simulation', 'model']):
            method_counts['computational'] += 1
        if any(keyword in text for keyword in ['experiment', 'empirical', 'study']):
            method_counts['experimental'] += 1
        if any(keyword in text for keyword in ['survey', 'questionnaire']):
            method_counts['survey'] += 1
        if any(keyword in text for keyword in ['case study', 'case-study']):
            method_counts['case_study'] += 1
    
    total_papers = len(papers)
    analysis = f"""
**METHODOLOGICAL ANALYSIS OF {total_papers} PAPERS**

**Methodological Distribution:**
- Quantitative approaches: {method_counts['quantitative']} papers ({method_counts['quantitative']/total_papers*100:.1f}%)
- Qualitative approaches: {method_counts['qualitative']} papers ({method_counts['qualitative']/total_papers*100:.1f}%)
- Mixed methods: {method_counts['mixed_methods']} papers ({method_counts['mixed_methods']/total_papers*100:.1f}%)
- Theoretical papers: {method_counts['theoretical']} papers ({method_counts['theoretical']/total_papers*100:.1f}%)
- Computational methods: {method_counts['computational']} papers ({method_counts['computational']/total_papers*100:.1f}%)

**Specific Method Indicators:**
- Experimental studies: {method_counts['experimental']} papers
- Survey-based research: {method_counts['survey']} papers  
- Case study approaches: {method_counts['case_study']} papers

**Methodological Trends:**
- Predominant approach: {"Quantitative" if method_counts['quantitative'] >= method_counts['qualitative'] else "Qualitative"}
- Computational integration: {"High" if method_counts['computational'] > total_papers*0.3 else "Moderate" if method_counts['computational'] > total_papers*0.1 else "Low"}
- Theoretical foundation: {"Strong" if method_counts['theoretical'] > total_papers*0.4 else "Moderate" if method_counts['theoretical'] > total_papers*0.2 else "Limited"}
"""
    
    return analysis

def generate_structured_methodology_analysis(research_question, research_type, papers, paper_methods_analysis, citation_format="apa", in_text_citations=None):
    """Generate structured methodology analysis without AI"""
    
    # Generate citations if not provided
    if papers and not in_text_citations:
        in_text_citations = create_in_text_citations(papers, citation_format)
    
    analysis = f"""
# METHODOLOGY ANALYSIS & RECOMMENDATIONS

**Research Question:** {research_question}
**Research Type:** {research_type.title()}
**Citation Format:** {citation_format.upper()}

{paper_methods_analysis if paper_methods_analysis else ""}

## 1. RESEARCH DESIGN FRAMEWORK

### Recommended Research Paradigm
For {research_type} research on "{research_question}":

**Primary Paradigm:** {"Positivist" if research_type == "empirical" else "Interpretivist" if research_type == "theoretical" else "Pragmatic"}

**Justification:**
- {research_type.title()} research typically benefits from {"quantitative, hypothesis-testing approaches" if research_type == "empirical" else "qualitative, meaning-making approaches" if research_type == "theoretical" else "mixed-methods, problem-solving approaches"}
- The research question suggests {"causal relationships" if research_type == "empirical" else "conceptual understanding" if research_type == "theoretical" else "practical solutions"}

### Research Design Type
**Recommended Design:** {"Experimental or Quasi-experimental" if research_type == "empirical" else "Descriptive or Exploratory" if research_type == "theoretical" else "Applied or Action Research"}

## 2. QUANTITATIVE APPROACHES

### Experimental Designs
- **Randomized Controlled Trial (RCT)**: If feasible and ethical
- **Quasi-experimental Design**: When randomization is not possible
- **Factorial Design**: For multiple variables
- **Crossover Design**: For repeated measures

### Survey Methodologies
- **Cross-sectional Survey**: For snapshot data
- **Longitudinal Survey**: For change over time
- **Panel Study**: For tracking same participants

### Statistical Analysis Methods
- **Descriptive Statistics**: Mean, median, standard deviation
- **Inferential Statistics**: t-tests, ANOVA, regression analysis
- **Advanced Methods**: Structural equation modeling, multilevel analysis

## 3. QUALITATIVE APPROACHES

### Interview Methodologies
- **Structured Interviews**: For standardized data collection
- **Semi-structured Interviews**: For flexibility with consistency
- **Unstructured Interviews**: For exploratory research

### Other Qualitative Methods
- **Focus Groups**: For group dynamics and consensus
- **Ethnographic Observation**: For cultural understanding
- **Case Study Methodology**: For in-depth analysis
- **Grounded Theory**: For theory development
- **Phenomenological Approach**: For lived experiences

## 4. MIXED-METHODS DESIGNS

### Sequential Designs
- **Sequential Explanatory**: Quantitative followed by qualitative
- **Sequential Exploratory**: Qualitative followed by quantitative

### Concurrent Designs
- **Concurrent Triangulation**: Simultaneous data collection
- **Concurrent Embedded**: One method embedded in another

## 5. DATA COLLECTION STRATEGIES

### Primary Data Collection
- **Surveys and Questionnaires**: For standardized data
- **Interviews**: For in-depth insights
- **Observations**: For behavioral data
- **Experiments**: For causal relationships

### Secondary Data Sources
- **Existing Datasets**: For large-scale analysis
- **Literature Reviews**: For theoretical foundation
- **Archival Records**: For historical perspective

### Instrument Development
- **Questionnaire Design**: Clear, unbiased questions
- **Interview Guides**: Structured yet flexible
- **Observation Protocols**: Systematic recording methods

## 6. SAMPLING METHODOLOGY

### Target Population
Define your population clearly based on:
- **Inclusion Criteria**: Who should be included
- **Exclusion Criteria**: Who should be excluded
- **Accessibility**: Practical considerations

### Sampling Methods
**Probability Sampling:**
- Simple Random Sampling
- Stratified Random Sampling
- Cluster Sampling

**Non-probability Sampling:**
- Convenience Sampling
- Purposive Sampling
- Snowball Sampling

### Sample Size Considerations
- **Power Analysis**: For statistical significance
- **Saturation Point**: For qualitative research
- **Resource Constraints**: Practical limitations

## 7. DATA ANALYSIS PLAN

### Quantitative Analysis
- **Descriptive Analysis**: Frequencies, means, distributions
- **Inferential Analysis**: Hypothesis testing, confidence intervals
- **Software**: R, SPSS, SAS, Stata

### Qualitative Analysis
- **Thematic Analysis**: Identifying patterns and themes
- **Content Analysis**: Systematic categorization
- **Narrative Analysis**: Story-based interpretation
- **Software**: NVivo, Atlas.ti, MAXQDA

## 8. ETHICAL CONSIDERATIONS

### IRB/Ethics Approval
- **Institutional Review**: Required for human subjects research
- **Risk Assessment**: Minimal, moderate, or high risk
- **Special Populations**: Additional protections needed

### Informed Consent
- **Consent Process**: Clear explanation of study
- **Voluntary Participation**: Right to withdraw
- **Confidentiality**: Data protection measures

## 9. VALIDITY & RELIABILITY

### Internal Validity
- **Control for Confounding**: Design and statistical controls
- **Randomization**: When possible
- **Blinding**: To reduce bias

### External Validity
- **Generalizability**: To broader populations
- **Ecological Validity**: Real-world applicability

### Reliability
- **Test-retest Reliability**: Consistency over time
- **Inter-rater Reliability**: Agreement between observers
- **Internal Consistency**: Cronbach's alpha for scales

## 10. IMPLEMENTATION TIMELINE

### Phase 1: Preparation (Months 1-2)
- Literature review completion
- Methodology finalization
- Ethics approval
- Instrument development

### Phase 2: Data Collection (Months 3-8)
- Pilot study
- Main data collection
- Quality assurance monitoring

### Phase 3: Analysis (Months 9-11)
- Data cleaning and preparation
- Statistical/qualitative analysis
- Results interpretation

### Phase 4: Dissemination (Month 12+)
- Report writing
- Publication preparation
- Conference presentations

## 11. INNOVATIVE METHODOLOGICAL APPROACHES

### Digital Methods
- **Online Surveys**: Broader reach, cost-effective
- **Social Media Analysis**: Real-time data
- **Mobile Data Collection**: Convenient and accessible

### Computational Approaches
- **Big Data Analytics**: Large dataset analysis
- **Machine Learning**: Pattern recognition
- **Text Mining**: Automated content analysis

## 12. REPORTING AND DISSEMINATION

### Reporting Standards
- **CONSORT**: For randomized trials
- **STROBE**: For observational studies
- **COREQ**: For qualitative research
- **PRISMA**: For systematic reviews

### Publication Strategy
- **Target Journals**: Identify appropriate venues
- **Open Access**: Consider accessibility
- **Data Sharing**: Follow discipline standards

---

**Note:** This methodology analysis was generated using structured analytical frameworks. For enhanced AI-powered recommendations and deeper methodological insights, configure the Gemini API key in your environment settings.

**Research Question:** {research_question}
**Research Type:** {research_type.title()}
**Citation Format:** {citation_format.upper()}
**Analysis Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    # Add references section if papers were provided
    if papers:
        references_section = generate_references_section(papers, citation_format)
        analysis += f"\n\n{references_section}"
    
    return analysis

# Sci-Hub API routes
@app.route("/api/scihub/paper-by-doi", methods=["POST"])
def get_paper_by_doi():
    """Get paper from Sci-Hub using DOI"""
    try:
        data = request.json
        doi = data.get("doi", "").strip()
        
        if not doi:
            return jsonify({"error": "DOI is required"}), 400
        
        logger.info(f"Searching Sci-Hub for DOI: {doi}")
        paper_data = scihub_api.get_paper_by_doi(doi)
        
        if paper_data:
            return jsonify({
                "success": True,
                "paper": paper_data,
                "message": "Paper found on Sci-Hub"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Paper not found on Sci-Hub"
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting paper by DOI: {str(e)}")
        return jsonify({"error": "Failed to search Sci-Hub"}), 500

@app.route("/api/scihub/paper-by-title", methods=["POST"])
def search_paper_by_title():
    """Search paper on Sci-Hub by title"""
    try:
        data = request.json
        title = data.get("title", "").strip()
        
        if not title:
            return jsonify({"error": "Title is required"}), 400
        
        logger.info(f"Searching Sci-Hub for title: {title[:50]}...")
        paper_data = scihub_api.search_paper_by_title(title)
        
        if paper_data:
            return jsonify({
                "success": True,
                "paper": paper_data,
                "message": "Paper found on Sci-Hub"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Paper not found on Sci-Hub"
            }), 404
            
    except Exception as e:
        logger.error(f"Error searching paper by title: {str(e)}")
        return jsonify({"error": "Failed to search Sci-Hub"}), 500

@app.route("/api/scihub/download-paper", methods=["POST"])
def download_paper_from_scihub():
    """Download paper PDF from Sci-Hub"""
    try:
        data = request.json
        pdf_url = data.get("pdf_url", "").strip()
        filename = data.get("filename", "paper.pdf")
        
        if not pdf_url:
            return jsonify({"error": "PDF URL is required"}), 400
        
        logger.info(f"Downloading paper from Sci-Hub: {pdf_url}")
        pdf_content = scihub_api.download_paper(pdf_url)
        
        if pdf_content:
            response = make_response(pdf_content)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            return jsonify({
                "success": False,
                "message": "Failed to download paper"
            }), 404
            
    except Exception as e:
        logger.error(f"Error downloading paper: {str(e)}")
        return jsonify({"error": "Failed to download paper"}), 500

@app.route("/api/scihub/mirror-status", methods=["GET"])
def get_scihub_mirror_status():
    """Get status of Sci-Hub mirrors"""
    try:
        mirror_status = scihub_api.get_mirror_status()
        
        return jsonify({
            "success": True,
            "mirrors": mirror_status,
            "active_mirror": scihub_api.active_mirror
        })
        
    except Exception as e:
        logger.error(f"Error getting mirror status: {str(e)}")
        return jsonify({"error": "Failed to get mirror status"}), 500

@app.route('/api/trending-topics', methods=['GET'])
def trending_topics():
    """Get trending research topics from recent arXiv papers"""
    try:
        # Search for recent papers in popular categories
        categories = ['cs.AI', 'cs.LG', 'cs.CL', 'physics', 'math', 'q-bio']
        trending = []
        
        for category in categories:
            try:
                papers = query_arxiv(f"cat:{category}", max_results=5, sort_by=arxiv.SortCriterion.SubmittedDate)
                if papers:
                    trending.append({
                        "category": category,
                        "papers": papers[:3]  # Top 3 recent papers
                    })
            except:
                    continue
        
        return jsonify({
            "success": True,
            "trending": trending
        })
        
    except Exception as e:
        logger.error(f"Error getting trending topics: {str(e)}")
        return jsonify({"error": "Failed to get trending topics"}), 500

@app.route('/api/generate-draft', methods=['POST'])
def generate_academic_draft():
    """Generate a complete academic project draft"""
    try:
        data = request.json
        research_title = data.get("research_title", "")
        research_question = data.get("research_question", "")
        research_field = data.get("research_field", "")
        research_type = data.get("research_type", "empirical")  # empirical, theoretical, applied
        papers = data.get("papers", [])
        citation_format = data.get("citation_format", "apa")
        include_sections = data.get("include_sections", {
            "introduction": True,
            "literature_review": True,
            "methodology": True,
            "conclusion": True,
            "future_works": True
        })
        
        if not research_title or not research_question:
            return jsonify({"error": "Research title and question are required"}), 400
        
        # Generate in-text citations and references
        in_text_citations = create_in_text_citations(papers, citation_format) if papers else {}
        references_section = generate_references_section(papers, citation_format) if papers else ""
        
        # Prepare paper context
        papers_context = ""
        if papers:
            papers_detail = []
            for i, paper in enumerate(papers[:15]):  # Limit to top 15 papers
                title = paper.get('title', 'Unknown Title')
                citation = in_text_citations.get(title, f"(Paper {i+1})")
                papers_detail.append(f"""
Paper {i+1}: {paper.get('title', 'Unknown Title')} {citation}
Authors: {paper.get('authors', 'Unknown')}
Year: {paper.get('published_year', 'Unknown')}
Abstract: {paper.get('summary', 'No abstract available')[:300]}...
Categories: {', '.join(paper.get('categories', []))}
""")
            papers_context = "\n".join(papers_detail)
        
        # Generate the complete draft
        draft_prompt = f"""
As an expert academic writer, create a complete research project draft with the following specifications:

**Research Title**: {research_title}
**Research Question**: {research_question}
**Research Field**: {research_field}
**Research Type**: {research_type}
**Citation Format**: {citation_format.upper()}

**Available Papers for Reference:**
{papers_context}

**Instructions:**
- Write in formal academic style
- Use proper {citation_format.upper()} citations throughout
- Include specific examples and evidence from the provided papers
- Maintain logical flow between sections
- Ensure each section is substantial and well-developed
- Use appropriate academic vocabulary and terminology

**Create the following sections:**

**1. INTRODUCTION** (if requested)
- Background and context of the research problem
- Problem statement and research gap identification
- Research objectives and questions
- Significance and contribution of the study
- Scope and limitations
- Structure overview of the paper

**2. LITERATURE REVIEW** (if requested)
- Comprehensive review of existing research
- Theoretical foundations
- Key findings from previous studies
- Research gaps and contradictions
- Synthesis of current knowledge
- Position of current research in the field

**3. METHODOLOGY** (if requested)
- Research design and approach
- Data collection methods
- Sample selection and size
- Data analysis techniques
- Validity and reliability measures
- Ethical considerations
- Limitations of the methodology

**4. CONCLUSION** (if requested)
- Summary of key findings
- Implications for theory and practice
- Contribution to the field
- Limitations of the study
- Recommendations

**5. FUTURE WORKS** (if requested)
- Potential research directions
- Methodological improvements
- Expanded scope possibilities
- Interdisciplinary opportunities
- Practical applications
- Long-term research agenda

**Format Requirements:**
- Use markdown formatting for headers and emphasis
- Include proper {citation_format.upper()} citations
- Write each section as a complete, coherent unit
- Aim for academic rigor and clarity
- Include transition sentences between major points

Generate a comprehensive academic draft that demonstrates deep understanding of the research area.
"""
        
        # Query AI for draft generation
        draft_content = query_gemini(draft_prompt, papers_context)
        
        # If AI is unavailable, generate a structured template
        if not draft_content or "I don't have access" in draft_content:
            draft_content = generate_draft_template(
                research_title, research_question, research_field, 
                research_type, papers, citation_format, include_sections
            )
        
        # Append references section if papers are available
        if papers and references_section:
            draft_content += f"\n\n## REFERENCES\n\n{references_section}"
        
        return jsonify({
            "success": True,
            "draft": draft_content,
            "research_title": research_title,
            "research_question": research_question,
            "research_field": research_field,
            "research_type": research_type,
            "citation_format": citation_format,
            "sections_included": include_sections,
            "papers_count": len(papers),
            "references": references_section,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Draft generation error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Failed to generate draft: {str(e)}"
        }), 500

def generate_draft_template(research_title, research_question, research_field, research_type, papers, citation_format, include_sections):
    """Generate a structured draft template when AI is unavailable"""
    template_sections = []
    
    if include_sections.get("introduction", True):
        template_sections.append(f"""
## 1. INTRODUCTION

### Background and Context
The field of {research_field} has witnessed significant developments in recent years. This research addresses the critical question: "{research_question}"

### Problem Statement
[Describe the specific problem or gap in knowledge that your research addresses]

### Research Objectives
The primary objective of this study is to investigate {research_question.lower()}. Specifically, this research aims to:
- [Objective 1]
- [Objective 2]
- [Objective 3]

### Significance of the Study
This research contributes to {research_field} by providing insights into [specific contribution].

### Scope and Limitations
This study focuses on [scope definition] while acknowledging limitations in [limitation areas].
""")
    
    if include_sections.get("literature_review", True):
        template_sections.append(f"""
## 2. LITERATURE REVIEW

### Theoretical Foundation
The theoretical framework for this study draws from [relevant theories in {research_field}].

### Previous Research
{"Recent studies have explored various aspects of this field:" if papers else "Key research in this area includes:"}
{chr(10).join([f"- {paper.get('title', 'Unknown')} ({paper.get('published_year', 'Unknown')})" for paper in papers[:10]]) if papers else "- [Key study 1]" + chr(10) + "- [Key study 2]" + chr(10) + "- [Key study 3]"}

### Research Gaps
Despite extensive research, several gaps remain:
- [Gap 1]
- [Gap 2]
- [Gap 3]

### Synthesis
The literature reveals that {research_question.lower()} remains an important area for investigation.
""")
    
    if include_sections.get("methodology", True):
        approach_desc = {
            "empirical": "This study employs an empirical approach using quantitative/qualitative data collection and analysis.",
            "theoretical": "This research adopts a theoretical approach, developing conceptual frameworks and models.",
            "applied": "This study uses an applied research approach, focusing on practical solutions and implementations."
        }.get(research_type, "This study employs a mixed-methods approach.")
        
        template_sections.append(f"""
## 3. METHODOLOGY

### Research Design
{approach_desc}

### Data Collection
[Describe your data collection methods, instruments, and procedures]

### Sample Selection
[Detail your sampling strategy and sample characteristics]

### Data Analysis
[Explain your analytical approach and techniques]

### Validity and Reliability
[Discuss measures to ensure research quality]

### Ethical Considerations
[Address ethical aspects of the research]
""")
    
    if include_sections.get("conclusion", True):
        template_sections.append(f"""
## 4. CONCLUSION

### Key Findings
This research on "{research_question}" has revealed several important insights:
- [Finding 1]
- [Finding 2]
- [Finding 3]

### Theoretical Implications
The findings contribute to {research_field} theory by [theoretical contribution].

### Practical Implications
The results have practical applications in [practical applications].

### Limitations
This study acknowledges limitations in [limitation areas].

### Recommendations
Based on the findings, the following recommendations are proposed:
- [Recommendation 1]
- [Recommendation 2]
- [Recommendation 3]
""")
    
    if include_sections.get("future_works", True):
        template_sections.append(f"""
## 5. FUTURE WORKS

### Research Directions
Future research in {research_field} should explore:
- [Direction 1]: Expanding the scope to include [specific area]
- [Direction 2]: Investigating the relationship between [variables]
- [Direction 3]: Developing new methodological approaches

### Methodological Improvements
- Enhanced data collection techniques
- Longitudinal study designs
- Cross-cultural validation

### Interdisciplinary Opportunities
- Collaboration with [related field 1]
- Integration with [related field 2]
- Application in [practical domain]

### Long-term Vision
The ultimate goal is to develop a comprehensive understanding of {research_question.lower()} that can inform both theory and practice in {research_field}.
""")
    
    return "\n".join(template_sections)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "scihub": scihub_api.active_mirror is not None,
            "gemini": os.getenv("GEMINI_API_KEY") is not None
        }
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("🚀 Starting Sentino AI - Academic Research Platform")
    print("📚 Features:")
    print("   • Academic paper search (arXiv)")
    print("   • Sci-Hub integration for paper access")
    print("   • AI-powered paper analysis")
    print("   • Research suggestions and insights")
    print(f"🌐 Access the app at: http://localhost:{port}")
    
    # Initialize Sci-Hub on startup
    try:
        scihub_api.find_active_mirror()
        print(f"✅ Sci-Hub integration ready (Mirror: {scihub_api.active_mirror})")
    except:
        print("⚠️  Sci-Hub integration may be limited")
    
    app.run(host='0.0.0.0', debug=True, port=port)
