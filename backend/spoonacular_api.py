import os
import re
import requests
from typing import Dict, Any, Optional

SPOONACULAR_API_KEY = os.environ.get("SPOONACULAR_API_KEY")
BASE_URL = "https://api.spoonacular.com/recipes"

# Words that Spoonacular sometimes embeds in ingredient names that are actually
# measurements/quantities, not part of the ingredient itself.
_MEASUREMENT_WORDS = {
    "spoon", "tablespoon", "teaspoon", "cup", "cups", "pinch", "dash",
    "handful", "bunch", "slice", "slices", "piece", "pieces", "clove",
    "cloves", "head", "stalk", "stalks", "sprig", "sprigs", "knob",
}


def _clean_ingredient_name(raw: str) -> str:
    """
    Strips measurement words that Spoonacular sometimes bakes into the
    nameClean field (e.g. 'spoon butter' -> 'butter', 'spoon salt' -> 'salt').
    """
    words = raw.strip().split()
    # Drop leading measurement words
    while words and words[0].lower() in _MEASUREMENT_WORDS:
        words.pop(0)
    cleaned = " ".join(words) if words else raw
    return cleaned.strip()


def search_recipe(query: str, exclude_ingredients: str = None, diet: str = None) -> Optional[Dict[str, Any]]:
    """
    Searches Spoonacular for a recipe matching the query and returns 
    the title, ingredients list, and formatted instructions.
    """
    if not SPOONACULAR_API_KEY:
        print("Warning: SPOONACULAR_API_KEY not set.")
        return None
        
    try:
        params = {
            "apiKey": SPOONACULAR_API_KEY,
            "query": query,
            "number": 5,
            "addRecipeInformation": "true",
            "fillIngredients": "true",
        }
        if exclude_ingredients:
            params["excludeIngredients"] = exclude_ingredients
        if diet:
            params["diet"] = diet
            
        response = requests.get(
            f"{BASE_URL}/complexSearch",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results")
            if not results:
                return None
                
            # Find the best match by checking if the query words appear in the title
            query_words = set(query.lower().split())
            best_match = results[0]
            max_overlap = 0
            
            for res in results:
                title_words = set(res.get("title", "").lower().split())
                overlap = len(query_words.intersection(title_words))
                # Perfect match check — exact substring
                if query.lower() in res.get("title", "").lower():
                    best_match = res
                    max_overlap = len(query_words)
                    break
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_match = res
                    
            if not best_match:
                return None
                
            # Accept the match if at least ONE meaningful word overlaps.
            # This allows "Palak Paneer" for "Paneer Butter Masala" (shares "paneer")
            # but still rejects completely unrelated recipes.
            if query.lower() not in best_match.get("title", "").lower():
                if max_overlap == 0:
                    print(f"Spoonacular rejected: no word overlap between '{best_match.get('title')}' and '{query}'")
                    return None
                    
            recipe = best_match
            
            # Extract clean ingredient names
            ingredients = []
            for ing in recipe.get("extendedIngredients", []):
                # Clean up the name to make it closer to what Kroger has
                name = ing.get("nameClean") or ing.get("name")
                if name:
                    cleaned = _clean_ingredient_name(name)
                    if cleaned:
                        ingredients.append(cleaned.title())
            
            # Remove duplicates while preserving order
            ingredients = list(dict.fromkeys(ingredients))
            
            # Extract step-by-step instructions
            instructions_text = ""
            analyzed = recipe.get("analyzedInstructions", [])
            if analyzed and analyzed[0].get("steps"):
                steps = analyzed[0]["steps"]
                instructions_text = "\n".join(f"{step['number']}. {step['step']}" for step in steps)
            else:
                # Fallback to plain string
                instructions_text = recipe.get("instructions") or "No detailed instructions available."
                # strip html tags if Spoonacular returned HTML
                instructions_text = re.sub(r'<[^>]+>', '', instructions_text)
            
            return {
                "recipe_name": recipe.get("title", query.title()),
                "ingredients": ingredients,
                "instructions": instructions_text
            }
        else:
            print(f"Spoonacular API Error ({response.status_code}): {response.text}")
            return None
            
    except Exception as e:
        print(f"Spoonacular API Exception: {e}")
        return None
