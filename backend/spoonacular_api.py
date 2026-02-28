import os
import re
import requests
from typing import Dict, Any, Optional

SPOONACULAR_API_KEY = os.environ.get("SPOONACULAR_API_KEY")
BASE_URL = "https://api.spoonacular.com/recipes"

# ── Indian dish name → English search-friendly equivalent ──────────────
# Spoonacular has terrible coverage of Hindi/Indian dish names but good
# coverage of their English equivalents.  This map lets us translate
# "paneer butter masala" → "paneer curry" so the API actually finds it.
RECIPE_TRANSLATIONS = {
    "channa masala": "chickpea curry",
    "chana masala": "chickpea curry",
    "chole": "chickpea curry",
    "paneer butter masala": "paneer curry",
    "paneer tikka masala": "paneer curry",
    "paneer makhani": "paneer curry",
    "shahi paneer": "paneer curry",
    "palak paneer": "spinach paneer",
    "saag paneer": "spinach paneer",
    "dal makhani": "lentil curry",
    "dal tadka": "lentil curry",
    "dal fry": "lentil curry",
    "rajma": "kidney bean curry",
    "rajma masala": "kidney bean curry",
    "aloo gobi": "potato cauliflower curry",
    "aloo matar": "potato pea curry",
    "malai kofta": "vegetable curry",
    "chicken tikka masala": "tikka masala",
    "chicken butter masala": "butter chicken",
    "murgh makhani": "butter chicken",
    "biryani": "chicken biryani",
    "chicken biryani": "chicken biryani",
    "lamb biryani": "lamb biryani",
    "goat curry": "goat curry",
    "keema": "ground meat curry",
    "samosa": "samosa",
    "gulab jamun": "gulab jamun",
    "naan": "naan bread",
    "roti": "flatbread",
    "dosa": "dosa crepe",
    "idli": "steamed rice cake",
    "rasam": "tomato soup indian",
    "korma": "chicken korma",
    "vindaloo": "chicken vindaloo",
    "tandoori chicken": "tandoori chicken",
    "fish curry": "fish curry",
}

# Words that Spoonacular sometimes embeds in ingredient names that are actually
# measurements/quantities, not part of the ingredient itself.
_MEASUREMENT_WORDS = {
    "spoon", "tablespoon", "teaspoon", "cup", "cups", "pinch", "dash",
    "handful", "bunch", "slice", "slices", "piece", "pieces", "clove",
    "cloves", "head", "stalk", "stalks", "sprig", "sprigs", "knob",
}

# Ingredients that are almost certainly wrong for savory main dishes.
_IRRELEVANT_INGREDIENTS = {
    "english muffin", "english muffins", "muffin", "muffins",
    "tortilla chips", "graham cracker", "marshmallow",
    "chocolate chips", "whipped cream", "ice cream",
}


def _clean_ingredient_name(raw: str) -> str:
    """Strips measurement words from ingredient names."""
    words = raw.strip().split()
    while words and words[0].lower() in _MEASUREMENT_WORDS:
        words.pop(0)
    cleaned = " ".join(words) if words else raw
    return cleaned.strip()


def _is_relevant_ingredient(name: str) -> bool:
    """Reject obviously wrong ingredients."""
    return name.lower().strip() not in _IRRELEVANT_INGREDIENTS


def _translate_recipe_name(query: str) -> str:
    """
    If the recipe name is in Indian/Hindi, translate to an English 
    equivalent that Spoonacular can actually find.
    """
    q = query.lower().strip()
    # Direct match
    if q in RECIPE_TRANSLATIONS:
        translated = RECIPE_TRANSLATIONS[q]
        print(f"Translated recipe: '{q}' -> '{translated}'")
        return translated
    # Partial match (e.g., "channa masala curry" contains "channa masala")
    for indian_name, english_name in RECIPE_TRANSLATIONS.items():
        if indian_name in q or q in indian_name:
            print(f"Translated recipe (partial): '{q}' -> '{english_name}'")
            return english_name
    return query


def search_recipe(query: str, exclude_ingredients: str = None, diet: str = None) -> Optional[Dict[str, Any]]:
    """
    Searches Spoonacular for a recipe matching the query.  Automatically
    translates Indian/Hindi dish names to English for better coverage.
    """
    if not SPOONACULAR_API_KEY:
        print("Warning: SPOONACULAR_API_KEY not set.")
        return None
        
    # Translate Indian dish names to English equivalents
    search_query = _translate_recipe_name(query)
    
    try:
        params = {
            "apiKey": SPOONACULAR_API_KEY,
            "query": search_query,
            "number": 5,
            "addRecipeInformation": "true",
            "fillIngredients": "true",
        }
        if exclude_ingredients:
            params["excludeIngredients"] = exclude_ingredients
        if diet:
            params["diet"] = diet
        
        # If it looks Indian, add cuisine hint
        if search_query != query:
            params["cuisine"] = "indian"
            
        response = requests.get(
            f"{BASE_URL}/complexSearch",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results")
            if not results:
                print(f"Spoonacular: 0 results for '{search_query}' (original: '{query}')")
                return None
                
            # Pick the best match
            best_match = results[0]  # Already sorted by relevance from API
            recipe = best_match
            
            # Extract clean ingredient names
            ingredients = []
            for ing in recipe.get("extendedIngredients", []):
                name = ing.get("nameClean") or ing.get("name")
                if name:
                    cleaned = _clean_ingredient_name(name)
                    if cleaned and _is_relevant_ingredient(cleaned):
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
                instructions_text = recipe.get("instructions") or "No detailed instructions available."
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
