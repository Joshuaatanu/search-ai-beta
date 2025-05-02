#!/usr/bin/env python3
"""
Methodology Analyzer for Academic Papers
This module provides functions to detect and classify research methodologies in academic papers.
"""
import re
import json
from typing import Dict, List, Tuple, Optional, Any, Union
import nltk
from nltk.tokenize import sent_tokenize
from collections import Counter

# Download required NLTK data (uncomment if not already downloaded)
# nltk.download('punkt')

class MethodologyAnalyzer:
    """Class for analyzing methodology sections in academic papers."""
    
    METHODOLOGY_TYPES = {
        "qualitative": [
            "interview", "focus group", "ethnography", "observation", 
            "case study", "narrative", "thematic analysis", "grounded theory",
            "phenomenological", "content analysis", "discourse analysis"
        ],
        "quantitative": [
            "survey", "questionnaire", "statistical", "regression", 
            "correlation", "experiment", "control group", "anova", "t-test",
            "chi-square", "factor analysis", "cluster analysis", "sample size"
        ],
        "mixed_methods": [
            "mixed method", "multi-method", "triangulation", "sequential",
            "concurrent", "embedded design", "explanatory", "exploratory"
        ],
        "experimental": [
            "controlled experiment", "randomized control", "between subjects",
            "within subjects", "factorial design", "repeated measures",
            "manipulation", "intervention"
        ],
        "computational": [
            "algorithm", "simulation", "machine learning", "deep learning",
            "neural network", "data mining", "computational model",
            "natural language processing", "computer vision"
        ],
        "review": [
            "systematic review", "meta-analysis", "literature review",
            "scoping review", "narrative review", "evidence synthesis"
        ]
    }

    @staticmethod
    def extract_methodology_section(text: str) -> str:
        """
        Extract the methodology section from an academic paper.
        
        Args:
            text: The full text of the academic paper
            
        Returns:
            The extracted methodology section or the entire text if no clear section is found
        """
        # Common section headers for methodology
        section_patterns = [
            r'(?i)(?:^|\n)(?:3\.|III\.?\s*)?methods?(?:\s+and\s+materials)?.*?(?=\n(?:\d+\.|[IV]+\.|\S+:|\Z))',
            r'(?i)(?:^|\n)(?:3\.|III\.?\s*)?methodology.*?(?=\n(?:\d+\.|[IV]+\.|\S+:|\Z))',
            r'(?i)(?:^|\n)(?:3\.|III\.?\s*)?research\s+design.*?(?=\n(?:\d+\.|[IV]+\.|\S+:|\Z))',
            r'(?i)(?:^|\n)(?:3\.|III\.?\s*)?experimental\s+design.*?(?=\n(?:\d+\.|[IV]+\.|\S+:|\Z))',
            r'(?i)(?:^|\n)(?:3\.|III\.?\s*)?research\s+methods?.*?(?=\n(?:\d+\.|[IV]+\.|\S+:|\Z))',
            r'(?i)(?:^|\n)(?:3\.|III\.?\s*)?study\s+design.*?(?=\n(?:\d+\.|[IV]+\.|\S+:|\Z))'
        ]
        
        # Try to find the methodology section using patterns
        for pattern in section_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(0).strip()
        
        # If no methodology section is found, search for paragraphs with 
        # methodology keywords
        methodology_keywords = sum(MethodologyAnalyzer.METHODOLOGY_TYPES.values(), [])
        relevant_paragraphs = []
        
        paragraphs = re.split(r'\n\s*\n', text)
        for paragraph in paragraphs:
            keyword_count = sum(1 for keyword in methodology_keywords 
                               if re.search(r'\b' + re.escape(keyword) + r'\b', 
                                           paragraph.lower()))
            if keyword_count >= 2:
                relevant_paragraphs.append(paragraph)
        
        if relevant_paragraphs:
            return '\n\n'.join(relevant_paragraphs)
        
        # If still nothing found, return the full text
        return text

    @staticmethod
    def classify_methodology(text: str) -> Dict[str, Any]:
        """
        Classify the methodology of a paper based on keyword frequency.
        
        Args:
            text: The methodology section or full text of the paper
            
        Returns:
            A dictionary with the classification results
        """
        text_lower = text.lower()
        
        # Count occurrences of keywords for each methodology type
        type_counts = {}
        type_keywords_found = {}
        
        for method_type, keywords in MethodologyAnalyzer.METHODOLOGY_TYPES.items():
            type_counts[method_type] = 0
            type_keywords_found[method_type] = []
            
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, text_lower)
                if matches:
                    type_counts[method_type] += len(matches)
                    type_keywords_found[method_type].append({
                        "keyword": keyword,
                        "count": len(matches)
                    })
        
        # Get total keyword count
        total_count = sum(type_counts.values())
        
        # Calculate confidence scores
        confidence_scores = {}
        if total_count > 0:
            for method_type, count in type_counts.items():
                confidence_scores[method_type] = round((count / total_count) * 100, 2)
        else:
            # Default equal probability if no keywords found
            for method_type in MethodologyAnalyzer.METHODOLOGY_TYPES:
                confidence_scores[method_type] = round(100 / len(MethodologyAnalyzer.METHODOLOGY_TYPES), 2)
        
        # Determine primary methodology
        primary_methodology = max(confidence_scores.items(), key=lambda x: x[1])[0]
        
        # Determine if mixed methodology is likely
        is_mixed = False
        sorted_scores = sorted(confidence_scores.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_scores) >= 2:
            top_score = sorted_scores[0][1]
            second_score = sorted_scores[1][1]
            if second_score > 30 and top_score < 60:
                is_mixed = True
                primary_methodology = "mixed_methods"
        
        return {
            "primary_methodology": primary_methodology,
            "confidence_scores": confidence_scores,
            "is_mixed": is_mixed,
            "keywords_found": type_keywords_found,
            "total_keyword_count": total_count
        }
# Analyze the methodology of a given text.
def analyze_methodology(text: str) -> Dict[str, Any]:
    """
    Analyze the methodology of a given text.
    
    Args:
        text: The text to analyze for methodology
        
    Returns:
        A dictionary with the methodology analysis results
    """
    analyzer = MethodologyAnalyzer()
    methodology_section = analyzer.extract_methodology_section(text)
    classification = analyzer.classify_methodology(methodology_section)
    
    return {
        "methodology_section": methodology_section[:1000] + "..." if len(methodology_section) > 1000 else methodology_section,
        "classification": classification,
        "methodology_types": {k: {"name": k.replace("_", " ").title(), 
                                 "keywords": v} 
                             for k, v in MethodologyAnalyzer.METHODOLOGY_TYPES.items()}
    }

def analyze_paper_methodology(paper_text: str) -> Dict[str, Any]:
    """Legacy function for API compatibility"""
    return analyze_methodology(paper_text)

def analyze_papers_methodologies(papers: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Analyze methodologies across multiple papers.
    
    Args:
        papers: List of paper dictionaries, each containing at least a 'text' field
        
    Returns:
        List of papers with added methodology analysis
    """
    results = []
    for paper in papers:
        if "text" in paper:
            analysis = analyze_methodology(paper["text"])
            paper_result = {**paper, "methodology_analysis": analysis}
            results.append(paper_result)
        else:
            results.append(paper)
    return results

def compare_methodologies(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare methodologies across multiple analyzed papers.
    
    Args:
        papers: List of papers with methodology_analysis field
        
    Returns:
        Dictionary with comparison results
    """
    methodology_counts = {}
    for method_type in MethodologyAnalyzer.METHODOLOGY_TYPES:
        methodology_counts[method_type] = 0
    
    keyword_frequencies = {}
    paper_methodologies = {}
    
    for i, paper in enumerate(papers):
        if "methodology_analysis" in paper and "classification" in paper["methodology_analysis"]:
            classification = paper["methodology_analysis"]["classification"]
            primary = classification["primary_methodology"]
            methodology_counts[primary] += 1
            paper_methodologies[f"Paper {i+1}"] = {
                "primary": primary,
                "scores": classification["confidence_scores"]
            }
            
            # Aggregate keyword frequencies
            for method_type, keywords in classification.get("keywords_found", {}).items():
                for keyword_info in keywords:
                    keyword = keyword_info["keyword"]
                    count = keyword_info["count"]
                    if keyword not in keyword_frequencies:
                        keyword_frequencies[keyword] = 0
                    keyword_frequencies[keyword] += count
    
    # Sort keywords by frequency
    sorted_keywords = sorted(keyword_frequencies.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "methodology_distribution": methodology_counts,
        "paper_methodologies": paper_methodologies,
        "common_keywords": dict(sorted_keywords[:15]) if sorted_keywords else {}
    }

if __name__ == "__main__":
    # Example usage
    sample_text = """
    3. Methodology
    
    In this study, we employed a mixed-methods approach to investigate the research question.
    We conducted a survey with 150 participants from different demographic backgrounds.
    The survey included both closed and open-ended questions about user preferences.
    
    Additionally, we performed statistical analysis on the collected data using SPSS software.
    For the qualitative part, we conducted 15 semi-structured interviews with experts in the field.
    """
    
    print(analyze_methodology(sample_text))
    print(analyze_methodology(sample_text)['primary_methodology']) 