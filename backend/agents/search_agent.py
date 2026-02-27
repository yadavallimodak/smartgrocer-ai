import time

def search_nearby_stores(item_name: str, radius_miles: int = 10) -> dict:
    """
    Mock integration for Google Search/Places API.
    Simulates finding the item at a competitor store within the radius.
    """
    # Simulate network latency
    time.sleep(1)
    
    mock_results = [
        {"store": "Whole Foods Market", "distance": "2.4 miles", "address": "123 Main St", "availability": "In Stock"},
        {"store": "Trader Joe's", "distance": "4.1 miles", "address": "456 Oak Ave", "availability": "Limited Stock"}
    ]
    
    return {
        "status": "success",
        "search_radius": f"{radius_miles} miles",
        "item": item_name,
        "alternatives": mock_results
    }

def search_web_for_general_query(query: str) -> str:
    """Uses Tavily API to grab a snippet from the web for out-of-domain questions."""
    import os
    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    if not tavily_api_key:
        return ""
    
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=tavily_api_key)
        response = client.search(query, search_depth="basic", max_results=1)
        if response and response.get("results"):
            return response["results"][0].get("content", "I found some results but couldn't read the content.")
    except Exception as e:
        print(f"Search error: {e}")
    return "I couldn't find a specific answer on the web for that."
