#!/usr/bin/env python3
import json
from duckduckgo_search import DDGS

def test_ddgs_searches():
    # Instantiate the DDGS class (you can also specify proxy, timeout, verify if needed)
    ddgs = DDGS()
    
    print("### Testing DuckDuckGo AI Chat ###")
    try:
        # AI chat example (choose a model; available options include "gpt-4o-mini", "claude-3-haiku", etc.)
        chat_result = ddgs.chat("Summarize Daniel Defoe's The Consolidator", model='claude-3-haiku')
        print("Chat result:")
        print(chat_result)
    except Exception as e:
        print("Error during AI chat:", e)

    print("\n### Testing Text Search ###")
    try:
        # Text search example: search for a historical event
        text_results = ddgs.text(
            keywords="Assyrian siege of Jerusalem", 
            region="wt-wt", 
            safesearch="moderate", 
            timelimit=None, 
            max_results=5
        )
        print("Text search results:")
        print(json.dumps(text_results, indent=2))
    except Exception as e:
        print("Error during text search:", e)

    print("\n### Testing Image Search ###")
    try:
        # Image search example: search for "butterfly" images with a monochrome filter
        image_results = ddgs.images(
            keywords="butterfly", 
            region="wt-wt", 
            safesearch="moderate", 
            timelimit=None, 
            size=None, 
            color="Monochrome", 
            type_image=None, 
            layout=None, 
            license_image=None, 
            max_results=5
        )
        print("Image search results:")
        print(json.dumps(image_results, indent=2))
    except Exception as e:
        print("Error during image search:", e)

    print("\n### Testing Video Search ###")
    try:
        # Video search example: search for "cars" videos with some filters
        video_results = ddgs.videos(
            keywords="cars", 
            region="wt-wt", 
            safesearch="moderate", 
            timelimit="w", 
            resolution="high", 
            duration="medium", 
            license_videos=None, 
            max_results=5
        )
        print("Video search results:")
        print(json.dumps(video_results, indent=2))
    except Exception as e:
        print("Error during video search:", e)

    print("\n### Testing News Search ###")
    try:
        # News search example: search for recent news about "sanctions"
        news_results = ddgs.news(
            keywords="sanctions", 
            region="wt-wt", 
            safesearch="moderate", 
            timelimit="m", 
            max_results=5
        )
        print("News search results:")
        print(json.dumps(news_results, indent=2))
    except Exception as e:
        print("Error during news search:", e)

if __name__ == "__main__":
    test_ddgs_searches()
