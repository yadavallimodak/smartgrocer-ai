import os
import json
import time
from google import genai
from google.genai import types

# Simple in-memory session store for the prototype.
# In a real app, this would be Redis or a database.
session_store = {}

# gemini-2.5-flash: the only model confirmed to work with this API key + SDK
MODEL_NAME = "gemini-2.5-flash"

# Store identity — set via STORE_ID env var in start_all.sh
STORE_ID = os.environ.get("STORE_ID", "01400943")

# ---------------------------------------------------------------------------
# Rule-based intent engine — used when Gemini is unavailable (quota / error)
# ---------------------------------------------------------------------------

# Track per-session state for rule-based followup
rule_session_store = {}

# Known recipes with their canonical ingredients and instructions
RECIPE_DB = {
    "tomato sauce": {
        "ingredients": ["tomatoes", "olive oil", "garlic", "onion", "basil", "oregano", "salt", "black pepper"],
        "instructions": (
            "1. Heat olive oil in a saucepan over medium heat.\n"
            "2. Sauté diced onion and minced garlic until softened (~3 min).\n"
            "3. Add crushed tomatoes. Stir well.\n"
            "4. Season with oregano, basil, salt, and black pepper.\n"
            "5. Simmer on low heat for 20–25 minutes, stirring occasionally.\n"
            "6. Adjust seasoning and serve over pasta or pizza."
        ),
    },
    "pasta": {
        "ingredients": ["pasta", "tomatoes", "garlic", "olive oil", "parmesan cheese", "basil", "salt"],
        "instructions": (
            "1. Boil salted water and cook pasta al dente per package directions.\n"
            "2. In a pan, sauté garlic in olive oil.\n"
            "3. Add diced tomatoes and simmer 10 minutes.\n"
            "4. Toss drained pasta into the sauce. Mix well.\n"
            "5. Top with fresh basil and parmesan. Serve immediately."
        ),
    },
    "lasagna": {
        "ingredients": ["lasagna noodles", "ground beef", "tomato sauce", "ricotta cheese",
                        "mozzarella cheese", "parmesan cheese", "onion", "garlic", "eggs",
                        "olive oil", "salt", "black pepper"],
        "instructions": (
            "1. Preheat oven to 375°F. Cook noodles; drain.\n"
            "2. Brown beef with onion and garlic. Drain fat.\n"
            "3. Stir tomato sauce into beef. Simmer 10 min.\n"
            "4. Mix ricotta, egg, salt, and pepper.\n"
            "5. Layer: sauce → noodles → ricotta → mozzarella. Repeat.\n"
            "6. Top with remaining sauce and parmesan.\n"
            "7. Cover with foil; bake 45 min. Uncover last 15 min."
        ),
    },
    "tacos": {
        "ingredients": ["taco shells", "ground beef", "taco seasoning", "cheddar cheese",
                        "lettuce", "tomatoes", "sour cream", "salsa", "onion"],
        "instructions": (
            "1. Brown ground beef in a skillet. Drain fat.\n"
            "2. Add taco seasoning and ¼ cup water. Stir and simmer 5 min.\n"
            "3. Warm taco shells per package directions.\n"
            "4. Fill shells with beef, then top with cheese, lettuce, tomato, sour cream, and salsa."
        ),
    },
    "chicken soup": {
        "ingredients": ["chicken breast", "chicken broth", "carrots", "celery", "onion",
                        "garlic", "egg noodles", "salt", "black pepper", "parsley"],
        "instructions": (
            "1. Simmer chicken in broth 20 min until cooked. Shred.\n"
            "2. Sauté carrots, celery, and onion in a pot until softened.\n"
            "3. Add broth, chicken, and garlic. Bring to a boil.\n"
            "4. Add noodles; cook 8–10 min. Season with salt and pepper.\n"
            "5. Garnish with fresh parsley."
        ),
    },
    "omelette": {
        "ingredients": ["eggs", "butter", "milk", "cheddar cheese", "onion", "bell pepper",
                        "salt", "black pepper"],
        "instructions": (
            "1. Beat eggs with a splash of milk, salt, and pepper.\n"
            "2. Melt butter in a non-stick pan over medium heat.\n"
            "3. Pour in eggs. Tilt pan so edges cook.\n"
            "4. When mostly set, add cheese and vegetables on one half.\n"
            "5. Fold omelette in half and slide onto plate."
        ),
    },
    "guacamole": {
        "ingredients": ["avocados", "lime", "onion", "tomatoes", "cilantro", "jalapeno",
                        "garlic", "salt"],
        "instructions": (
            "1. Halve and pit avocados; scoop into a bowl.\n"
            "2. Mash with a fork to desired texture.\n"
            "3. Stir in diced onion, tomato, cilantro, and jalapeno.\n"
            "4. Squeeze in lime juice. Add minced garlic and salt.\n"
            "5. Mix well. Taste and adjust seasoning."
        ),
    },
    "cilantro chutney": {
        "ingredients": ["cilantro", "mint leaves", "green chilies", "garlic", "ginger",
                        "lemon", "onion", "salt", "cumin"],
        "instructions": (
            "1. Wash and roughly chop cilantro and mint leaves.\n"
            "2. Blend cilantro, mint, green chilies, garlic, and ginger together.\n"
            "3. Add diced onion, lemon juice, cumin, and salt.\n"
            "4. Blend until smooth, adding a little water if needed.\n"
            "5. Taste and adjust seasoning. Serve as a dip or condiment."
        ),
    },
    "salsa": {
        "ingredients": ["tomatoes", "onion", "cilantro", "jalapeno", "lime", "garlic", "salt"],
        "instructions": (
            "1. Dice tomatoes, onion, jalapeno, and garlic finely.\n"
            "2. Chop cilantro.\n"
            "3. Combine all in a bowl. Squeeze lime juice over the top.\n"
            "4. Season with salt. Mix well and let rest 10 min for flavors to meld.\n"
            "5. Serve with tortilla chips or as a topping."
        ),
    },
    "chicken curry": {
        "ingredients": ["chicken breast", "onion", "garlic", "ginger", "tomatoes",
                        "curry powder", "coconut milk", "olive oil", "salt", "cilantro"],
        "instructions": (
            "1. Heat oil; sauté onion until golden. Add garlic and ginger.\n"
            "2. Add curry powder; stir 1 min.\n"
            "3. Add diced chicken; cook until sealed.\n"
            "4. Pour in tomatoes and coconut milk. Bring to a boil.\n"
            "5. Simmer 20 min until chicken is cooked through.\n"
            "6. Garnish with fresh cilantro. Serve with rice."
        ),
    },
    "stir fry": {
        "ingredients": ["chicken breast", "bell pepper", "broccoli", "carrots", "soy sauce",
                        "garlic", "ginger", "sesame oil", "onion", "cornstarch", "rice"],
        "instructions": (
            "1. Slice chicken and vegetables into bite-sized pieces.\n"
            "2. Mix soy sauce, sesame oil, cornstarch, and ginger for sauce.\n"
            "3. Heat oil in a wok on high heat. Stir-fry chicken until cooked.\n"
            "4. Add vegetables; stir-fry 3–4 min until tender-crisp.\n"
            "5. Pour sauce over. Toss everything together for 1 min.\n"
            "6. Serve immediately over steamed rice."
        ),
    },
    "pizza": {
        "ingredients": ["pizza dough", "tomato sauce", "mozzarella cheese", "olive oil",
                        "basil", "garlic", "pepperoni", "bell pepper", "onion", "salt"],
        "instructions": (
            "1. Preheat oven to 450°F. Roll out pizza dough.\n"
            "2. Brush dough with olive oil and garlic.\n"
            "3. Spread tomato sauce evenly, leaving a border.\n"
            "4. Top with mozzarella and your chosen toppings.\n"
            "5. Bake 12–15 min until crust is golden and cheese bubbles.\n"
            "6. Top with fresh basil and slice."
        ),
    },
    "burger": {
        "ingredients": ["ground beef", "burger buns", "cheddar cheese", "lettuce",
                        "tomatoes", "onion", "pickles", "ketchup", "mustard", "mayonnaise",
                        "salt", "black pepper"],
        "instructions": (
            "1. Season ground beef with salt and pepper. Form into patties.\n"
            "2. Grill or pan-fry patties 3–4 min per side for medium doneness.\n"
            "3. Add cheese in the last minute; cover to melt.\n"
            "4. Toast buns lightly.\n"
            "5. Assemble: spread condiments, add patty, then lettuce, tomato, onion, and pickles."
        ),
    },
    "fried rice": {
        "ingredients": ["rice", "eggs", "onion", "garlic", "peas", "carrots",
                        "soy sauce", "sesame oil", "butter", "salt", "black pepper"],
        "instructions": (
            "1. Cook rice ahead and let cool (day-old rice works best).\n"
            "2. Scramble eggs in butter; set aside.\n"
            "3. Sauté garlic, onion, carrots, and peas in oil.\n"
            "4. Add rice; stir-fry on high heat 3 min.\n"
            "5. Add soy sauce and sesame oil; toss well.\n"
            "6. Fold in scrambled eggs. Season and serve hot."
        ),
    },
    "pancakes": {
        "ingredients": ["flour", "eggs", "milk", "butter", "sugar", "baking powder",
                        "salt", "maple syrup"],
        "instructions": (
            "1. Whisk together flour, sugar, baking powder, and salt.\n"
            "2. In separate bowl, whisk eggs, milk, and melted butter.\n"
            "3. Combine wet and dry ingredients; don't overmix (lumps are OK).\n"
            "4. Heat a non-stick pan over medium heat. Grease lightly.\n"
            "5. Pour ¼ cup batter per pancake; flip when bubbles form.\n"
            "6. Serve with maple syrup and butter."
        ),
    },
}

# Ingredient → list of recipes that feature it (for suggestions)
INGREDIENT_TO_RECIPES = {}
for _rname, _rdata in RECIPE_DB.items():
    for _ing in _rdata["ingredients"]:
        _key = _ing.lower().split()[0]  # first word acts as the key, e.g. "chicken" from "chicken breast"
        INGREDIENT_TO_RECIPES.setdefault(_key, []).append(_rname)
        INGREDIENT_TO_RECIPES.setdefault(_ing.lower(), []).append(_rname)

# Phrases that clearly signal a recipe intent
RECIPE_TRIGGERS = ["make", "cook", "recipe", "how to", "ingredients for",
                   "want to make", "how do i", "preparing", "i want to prepare"]

# Phrases that signal the user wants recipe suggestions
SUGGEST_TRIGGERS = ["what can i make", "suggest", "what recipes", "what should i make",
                    "what can you make", "what do i make", "any recipe", "what can i cook"]

# Keywords that mean "show me nearby Kroger stores" — checked BEFORE location triggers
NEARBY_STORE_PHRASE_TRIGGERS = [
    "nearby kroger", "closest kroger", "nearest kroger", "other kroger",
    "kroger locations", "kroger stores near", "other locations",
    "all kroger", "find kroger", "other stores near",
    "kroger close", "kroger near me",
    "locations of kroger", "kroger store locations", "all locations",
    "all stores", "list of kroger", "where are the kroger",
    "where are kroger", "show me kroger",
    # Natural-language variants
    "near me", "near you", "close to me", "close to you",
    "locations near", "stores near", "stores nearby",
    "what locations are", "which locations are",
]

# Phrases for location questions (current store only)
LOCATION_TRIGGERS = ["which kroger", "what kroger", "what store", "which store",
                     "where am i", "where is this", "what location", "this location"]


# Out-of-domain triggers
OOD_TRIGGERS = ["trump", "biden", "politics", "code", "program", "hack",
                "weather", "sports", "stock", "bitcoin", "movie", "music"]

# General browse / inventory questions — answer with a friendly category list
BROWSE_TRIGGERS = [
    "what do you have", "what do you carry", "what do you sell", "what do you stock",
    "what groceries", "what items", "what products", "what food", "what can i buy",
    "what is available", "what's available", "what are you selling", "show me your",
    "what kind of", "what types of", "tell me what you have", "what are your products",
    "what all do you", "what all can", "what all items", "items in stock",
    "in stock", "items you have", "items you carry", "items you sell",
    "do you carry", "do you sell", "do you stock",
]

# Common non-grocery single words to ignore for ingredient detection
NON_FOOD_WORDS = {"the", "a", "an", "please", "hi", "hello", "yes", "no",
                  "ok", "thanks", "thank", "you", "i", "me", "my", "we",
                  "what", "which", "how", "any", "some", "your", "our"}


def _looks_like_ingredient(text: str) -> bool:
    """Heuristic: short phrase that isn't a common non-food word."""
    words = text.split()
    if len(words) > 3:
        return False
    if all(w in NON_FOOD_WORDS for w in words):
        return False
    return True


def _rule_based_intent(session_id: str, query: str) -> dict:
    """
    Keyword-based fallback intent engine. Handles the full conversational flow
    without any LLM API call.
    """
    q = query.lower().strip().rstrip("?.,!")
    session = rule_session_store.get(session_id, {})

    # 0. Conversational Filler / Affirmations
    conversational_fillers = ["yes", "yes please", "no", "no thanks", "okay", "sure", "thanks", "thank you", "hello", "hi"]
    if q in conversational_fillers:
        return {
            "action": "general_chat",
            "message": "Alright! Let me know if you need help finding any specific products, recipes, or aisles today."
        }

    # 0. Nearby store search — check BEFORE location/OOD triggers
    if any(t in q for t in NEARBY_STORE_PHRASE_TRIGGERS):
        return {"action": "nearby_store_search"}

    # 0.5 General browse / inventory question
    if any(t in q for t in BROWSE_TRIGGERS):
        return {
            "action": "ask_followup",
            "message": (
                "Great question! We carry a wide selection of fresh groceries here at Kroger. "
                "Our main categories include:\n\n"
                "🥦 **Produce** — Fresh fruits and vegetables\n"
                "🥛 **Dairy** — Milk, cheese, eggs, yogurt\n"
                "🥩 **Meat & Seafood** — Chicken, beef, pork, fish\n"
                "🥖 **Bakery** — Breads, pastries, tortillas\n"
                "🥫 **Pantry** — Canned goods, pasta, sauces, spices\n"
                "🧊 **Frozen Foods** — Meals, ice cream, vegetables\n"
                "🥤 **Beverages** — Juice, soda, water, coffee\n\n"
                "What specific item or ingredient are you looking for? I can help you find it or even suggest a recipe! 😊"
            )
        }

    # 1. Out-of-domain
    if any(t in q for t in OOD_TRIGGERS):
        return {
            "action": "out_of_domain",
            "message": "I'm sorry, I'm a Kroger grocery assistant and can only help with grocery and recipe questions!"
        }

    # 2. Store location question (current store)
    if any(t in q for t in LOCATION_TRIGGERS):
        return {
            "action": "ask_followup",
            "message": f"You're currently at Kroger Store #{STORE_ID}. Is there anything I can help you find today?"
        }

    # 3. User explicitly asking for recipe suggestions (e.g. "what can I make with cilantro")
    if any(t in q for t in SUGGEST_TRIGGERS):
        # Try to extract the ingredient from the query
        candidate = q
        for phrase in SUGGEST_TRIGGERS + ["with", "using", "from", "what can i make"]:
            candidate = candidate.replace(phrase, "").strip()
        candidate = candidate.strip()
        # Find matching recipes
        matches = INGREDIENT_TO_RECIPES.get(candidate, []) or INGREDIENT_TO_RECIPES.get(candidate.rstrip("s"), [])
        if matches:
            unique = list(dict.fromkeys(matches))[:4]  # deduplicate, cap at 4
            names = ", ".join(r.title() for r in unique)
            return {
                "action": "ask_followup",
                "message": f"Great question! With {candidate or 'that'}, you could make: {names}. Which one sounds good to you?"
            }
        return {
            "action": "ask_followup",
            "message": f"I know recipes for: {', '.join(r.title() for r in list(RECIPE_DB.keys())[:8])}. Which one would you like to make?"
        }

    # 4. If we're waiting for a recipe answer from previous turn (ingredient follow-up)
    if session.get("awaiting_recipe_for"):
        item = session.pop("awaiting_recipe_for")
        rule_session_store[session_id] = session

        # Check if user is giving a recipe name directly from our known DB
        for recipe_name, recipe_data in RECIPE_DB.items():
            if recipe_name in q:
                return {
                    "action": "search_recipe",
                    "recipe_name": recipe_name.title(),
                    "message": f"Here is how to make {recipe_name.title()} and everything you'll need from our store!",
                    "ingredients": recipe_data["ingredients"],
                    "recipe_instructions": recipe_data["instructions"],
                }

        affirmatives = ["yes", "yep", "yeah", "sure", "of course", "please", "go ahead", "ok", "okay"]
        is_affirmative = any(a in q for a in affirmatives)
        is_negative = any(n in q for n in ["no", "nevermind", "never mind", "nah", "nope", "that's all", "thats all", "i'm good", "im good", "goodbye", "bye"])
        
        if is_negative:
            return {
                "action": "general_chat",
                "message": f"No worries! You'll find the {item} right where I showed you. If you need anything else, I'm here to help. Have a great shopping trip! 👋"
            }
        
        if is_affirmative:
            suggestions = INGREDIENT_TO_RECIPES.get(item, []) or INGREDIENT_TO_RECIPES.get(item.rstrip("s"), [])
            if suggestions:
                recipe_name = suggestions[0]
                return {
                    "action": "search_recipe",
                    "recipe_name": recipe_name.title(),
                    "message": f"Great! Let me pull up the {recipe_name.title()} recipe and find everything you need here!",
                    "ingredients": RECIPE_DB[recipe_name]["ingredients"],
                    "recipe_instructions": RECIPE_DB[recipe_name]["instructions"],
                }
            # No known recipe in DB, but let the orchestrator try Gemini/Spoonacular
            return {
                "action": "search_recipe",
                "recipe_name": item.title(),
                "message": f"Let me find some great recipes using {item}!",
                "ingredients": [],
                "recipe_instructions": ""
            }

        # Otherwise, treat whatever they typed as the recipe name!
        recipe_candidate = q
        for phrase in ["i would like to make", "i want to make", "how to make", "do you have a recipe for",
                       "recipe for", "how do i make", "can you give me a recipe for", "make", "cook"] + affirmatives:
            recipe_candidate = recipe_candidate.replace(phrase, "").strip()
            
        for prefix in ["the ", "a ", "an "]:
            if recipe_candidate.startswith(prefix):
                recipe_candidate = recipe_candidate[len(prefix):]
        recipe_candidate = recipe_candidate.strip()
        
        # We don't have it in our local DB, but route to search_recipe so spoonacular/orchestrator handles it!
        return {
            "action": "search_recipe",
            "recipe_name": recipe_candidate.title(),
            "message": f"I don't have the exact recipe for {recipe_candidate.title()} saved, but I'd be happy to help you find the ingredients if you know what you need!",
            "ingredients": [],
            "recipe_instructions": ""
        }

    # 4b. If we previously attempted a recipe and the user is confirming ("yes go ahead")
    if session.get("pending_recipe"):
        pending = session.pop("pending_recipe")
        rule_session_store[session_id] = session

        affirmatives = ["yes", "yep", "yeah", "sure", "of course", "please", "go ahead", "ok", "okay", "help"]
        is_affirmative = any(a in q for a in affirmatives)
        is_negative = any(n in q for n in ["no", "nevermind", "never mind", "nah", "nope"])

        if is_negative:
            return {
                "action": "general_chat",
                "message": "Alright! Let me know if there's anything else I can help you with. 😊"
            }

        if is_affirmative or not any(t in q for t in RECIPE_TRIGGERS):
            # User confirmed — retry the recipe search via Spoonacular
            return {
                "action": "search_recipe",
                "recipe_name": pending,
                "message": f"Absolutely! Let me find the full recipe and ingredients for {pending}.",
                "ingredients": [],
                "recipe_instructions": ""
            }

    # 5. Explicit recipe name in query
    for recipe_name, recipe_data in RECIPE_DB.items():
        if recipe_name in q:
            return {
                "action": "search_recipe",
                "recipe_name": recipe_name.title(),
                "message": f"Here is how to make {recipe_name.title()} and what you'll need from our store!",
                "ingredients": recipe_data["ingredients"],
                "recipe_instructions": recipe_data["instructions"],
            }

    # 6. Generic "make/cook/recipe" trigger → try to extract recipe name from query
    if any(t in q for t in RECIPE_TRIGGERS):
        recipe_candidate = q
        for phrase in ["i would like to make", "i want to make", "how to make", "do you have a recipe for",
                       "recipe for", "how do i make", "can you give me a recipe for", "make", "cook"]:
            recipe_candidate = recipe_candidate.replace(phrase, "").strip()
            
        for prefix in ["the ", "a ", "an ", "some ", "okay so ", "ok so ", "so ", "well ", "right ", "listen ", "please "]:
            if recipe_candidate.lower().startswith(prefix):
                recipe_candidate = recipe_candidate[len(prefix):]
                
        # Aggressively strip trailing conversational fluff by slicing on common delimiters
        for delimiter in [",", ".", "?", " what are", " suggest", " how to", " what is", " what do i", " and recipe", " recipe", " what do you", " please"]:
            if delimiter in recipe_candidate:
                recipe_candidate = recipe_candidate.split(delimiter)[0]
                
        recipe_candidate = recipe_candidate.strip()

        for recipe_name, recipe_data in RECIPE_DB.items():
            if recipe_name in recipe_candidate or recipe_candidate in recipe_name:
                return {
                    "action": "search_recipe",
                    "recipe_name": recipe_name.title(),
                    "message": f"Here is how to make {recipe_name.title()} and everything you'll need from our store!",
                    "ingredients": recipe_data["ingredients"],
                    "recipe_instructions": recipe_data["instructions"],
                }

        # Unknown recipe → we don't know the ingredients, but it's clearly a recipe request
        # Save the recipe name to session so the NEXT turn remembers context
        recipe_name = recipe_candidate.title() if recipe_candidate else "that dish"
        session["pending_recipe"] = recipe_name
        rule_session_store[session_id] = session
        return {
            "action": "search_recipe",
            "recipe_name": recipe_name,
            "message": f"I don't have the exact recipe for {recipe_name} saved, but I'd be happy to help you find the ingredients if you know what you need!",
            "ingredients": [],
            "recipe_instructions": ""
        }

    # 7. Single ingredient / short phrase → ask follow-up
    item = q
    for phrase in ["do you have", "where are", "where is", "where are the",
                   "i need", "looking for", "find me", "do you carry", "in stock",
                   "any", "some", "please", "thanks", "thank you"]:
        item = item.replace(phrase, "").strip()
    item = item.strip()

    if _looks_like_ingredient(item) and not any(t in item for t in RECIPE_TRIGGERS):
        session["awaiting_recipe_for"] = item
        rule_session_store[session_id] = session
        # Hint at recipes we know
        known = INGREDIENT_TO_RECIPES.get(item, []) or INGREDIENT_TO_RECIPES.get(item.rstrip("s"), [])
        hint = f" I can also help you make {', '.join(r.title() for r in list(dict.fromkeys(known))[:3])} if you're interested!" if known else ""
        return {
            "action": "ask_followup",
            "message": f"Of course! May I ask what you're planning to make with the {item}?{hint} 😊"
        }

    # 8. Fallthrough → direct lookup
    return {"action": "direct_lookup", "target_item": item or q}



def analyze_kroger_intent(session_id: str, query: str, user_store_id: str = None) -> dict:
    """
    Primary intent analysis. Tries Gemini first; falls back to the local
    rule-based engine if the API is unavailable (quota, auth error, timeout).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not set. Using rule-based engine.")
        return _rule_based_intent(session_id, query)

    # Short-circuit Gemini for nearby-store queries — always use rule engine for this
    q_lower = query.lower()
    if any(t in q_lower for t in NEARBY_STORE_PHRASE_TRIGGERS):
        return _rule_based_intent(session_id, query)

    client = genai.Client(api_key=api_key)
    history = session_store.get(session_id, [])
    
    current_store = user_store_id if user_store_id else STORE_ID

    system_prompt = f"""
    You are a friendly, knowledgeable AI grocery assistant inside a Kroger store (Store ID: {current_store}).
    Your job is to understand what shoppers need and respond with a structured JSON object so the system can take the right action.

    ## ACTIONS — read carefully and pick the most appropriate one:

    - "general_chat" — shopper is just making conversation, saying hello, or talking about something grocery-related but NOT currently trying to search for a specific item (e.g. "hi there", "how are you today", "thanks for the help", "I love cooking").
    - "nearby_store_search" — shopper wants to know where nearby Kroger stores are (e.g. "find kroger locations", "show me other krogers", "kroger near me", "what are the kroger locations")
    - "nearest_store" — shopper wants to know which single Kroger is closest to them (e.g. "which store is closest", "which one is nearest", "closest kroger", "which one is close to me")
    - "direct_lookup" — shopper is asking if a SPECIFIC product/item is available, in stock, or where to find it (e.g. "do you have milk", "where is the bread", "does it have tomatoes", "okay how about cucumbers", "no just tell me where they are"). Extract ONLY the absolute core item noun into target_item. If they ask about a SPECIFIC different store (e.g. "in castle hills"), extract that into target_store_query.
    - "browse_inventory" — shopper is asking broadly what the store carries, without a specific item in mind (e.g. "what do you have", "what groceries do you sell", "what's in stock")
    - "complex_search" — shopper wants a filtered list of items (e.g. "show me items under 5 dollars", "what do you have that is healthy", "list all snacks")
    - "search_recipe" — shopper wants to cook something or asks for ingredients/instructions (e.g. "I want to make pasta", "how do I cook chicken", "what do I need for tacos"). Extract all ingredients and steps.
    - "ask_followup" — shopper asked about something vague, or you couldn't find what they need. BE PROACTIVE! Ask them what recipe they are making so you can suggest ingredients, or ask if they want you to check nearby Kroger locations. Never give a dead-end answer.
    - "out_of_domain" — clearly non-grocery topic (politics, celebrities, sports, math, coding, weather, etc.)

    ## RULES:
    - If the user's intent is to cook or prepare a dish (e.g., they say "how to make", "how do I cook", "i want to make", "recipe for"), you MUST rigidly classify the action as "search_recipe" and NOT "direct_lookup", even if the dish exists as a pre-packaged grocery item (like 'marinara sauce' or 'salad').
    - Use conversation history to understand context. If you offered to help with a recipe and the user replies with a dish name (e.g. "marinara sauce"), use "search_recipe" for that dish.
    - If the user specifies dietary restrictions (e.g., "vegetarian", "vegan") or says to exclude something (e.g., "no eggs", "without dairy"), capture them in "diet" and "exclude_ingredients" during a "search_recipe" action.
    - If the user ignores your recipe offer and just asks for an item (e.g. "how about tomatoes"), DO NOT assume they are answering the recipe question. Treat it as a "direct_lookup".
    - For "direct_lookup", you MUST extract ONLY the cleanest possible core product noun into target_item. Strip ALL conversational filler, adjectives, and verbs (e.g. for "okay how about cucumbers" extract "cucumbers". For "find me tomatoes" extract "tomatoes").
    - Conversational affirmations or rejections like "yes please", "sure", "no thanks", "okay", or "thank you" MUST be classified as "general_chat". DO NOT extract them as a target_item.
    - For "search_recipe", list ALL canonical grocery ingredients comprehensively.
    - If the user asks "which kroger is this" or "where am I", use "ask_followup" and tell them they are at Store {STORE_ID} in The Colony, TX.
    - NEVER use "out_of_domain" for anything grocery-related.

    ## RESPOND with ONE JSON object only (no markdown, no list):
    {{
        "action": "general_chat" | "nearby_store_search" | "nearest_store" | "direct_lookup" | "browse_inventory" | "complex_search" | "search_recipe" | "ask_followup" | "out_of_domain",
        "message": "Your warm, helpful reply to the shopper.",
        "target_item": "Exact item name for direct_lookup (omit or leave empty for other actions).",
        "target_store_query": "The specific remote store mentioned, if any (e.g. 'castle hills').",
        "recipe_name": "Name of the recipe (search_recipe only).",
        "ingredients": ["ingredient1", "ingredient2"],
        "exclude_ingredients": "Comma-separated string of ingredients to avoid, e.g. 'eggs, meat'. (search_recipe only)",
        "diet": "Dietary restriction e.g. 'vegetarian', 'vegan', 'gluten free' (search_recipe only).",
        "recipe_instructions": "Step by step as a single string (search_recipe only)."
    }}
    """

    formatted_history = "Conversation History:\n"
    for turn in history:
        formatted_history += f"{turn['role']}: {turn['content']}\n"
    formatted_history += f"User: {query}\n"

    def _call_gemini():
        import time
        from google.genai import types
        
        print(f"[{time.strftime('%H:%M:%S')}] STARTING Gemini API Call...")
        # Configure a strict timeout so the frontend doesn't hang for 20 seconds
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.0
        )
        
        t0 = time.time()
        try:
            # We can't easily pass timeout to high-level SDK, so we rely on the network wrapper or just measure it
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[system_prompt, formatted_history],
                config=config
            )
            print(f"[{time.strftime('%H:%M:%S')}] FINISHED Gemini API Call in {time.time() - t0:.2f}s")
            print("GEMINI OUTPUT:", response.text)
            return json.loads(response.text)
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] GEMINI API ERROR after {time.time() - t0:.2f}s: {e}")
            raise e

    try:
        result = _call_gemini()
        if isinstance(result, list):
            result = result[0] if result else {}
        # Guard: if Gemini returned a plain string instead of a JSON object, use rule engine
        if not isinstance(result, dict):
            print(f"Gemini returned non-dict ({type(result).__name__}). Using rule-based engine.")
            return _rule_based_intent(session_id, query)

        history.append({"role": "User", "content": query})
        history.append({"role": "Assistant", "content": json.dumps(result)})
        session_store[session_id] = history
        return result

    except Exception as e:
        err_str = str(e)
        print(f"Gemini unavailable ({err_str[:60]}…). Using rule-based engine.")
        # Use rule-based engine immediately — no 65s wait
        return _rule_based_intent(session_id, query)
