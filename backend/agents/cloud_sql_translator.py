import os
import requests

# Mocking the LLM Text-to-SQL for the prototype since we don't have a real API key
# In a real scenario, this would call OpenAI, Anthropic, or Gemini's API.

SCHEMA_CONTEXT = """
Table: inventory
Columns: id (INTEGER), name (TEXT), category (TEXT), aisle (INTEGER), stock (INTEGER), price (REAL)
"""

def generate_sql_from_text(user_query: str) -> str:
    """
    Sends natural language to a Cloud LLM to generate a SQL string.
    Using a deterministic mock for safety and demonstration.
    """
    query_lower = user_query.lower()
    
    if "vegan" in query_lower and "under" in query_lower:
        # e.g., "vegan options under 5 dollars"
        return "SELECT * FROM inventory WHERE name LIKE '%Vegan%' AND price < 5.0"
    
    if "dairy" in query_lower:
        return "SELECT * FROM inventory WHERE category = 'Dairy'"
        
    if "bakery" in query_lower:
        return "SELECT * FROM inventory WHERE category = 'Bakery'"
        
    # Default fallback - very simple heuristic mock
    return "SELECT * FROM inventory LIMIT 5"
