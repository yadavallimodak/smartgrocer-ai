from backend.agents.sql_agent import exact_item_lookup, execute_safe_sql
from backend.agents.cloud_sql_translator import generate_sql_from_text
from backend.agents.search_agent import search_nearby_stores, search_web_for_general_query
from backend.agents.analytics import log_search
from backend.agents.state_manager import analyze_kroger_intent, STORE_ID
from backend.kroger_api import find_nearby_stores
import os



def handle_user_query(query: str, session_id: str = "default_session",
                      user_lat: float = None, user_lon: float = None,
                      user_store_id: str = None) -> dict:
    """
    The orchestrator. Represents the Edge SLM processing logic.
    Decides how to route the intent based on keywords or basic NLP.
    """
    query_lower = query.lower()
    intent = "unknown"
    
    # NEW STEP: Intelligent Kroger Persona Analysis
    kroger_intent = analyze_kroger_intent(session_id, query, user_store_id=user_store_id)
    action = kroger_intent.get("action", "fallback_routing")
    
    if action == "out_of_domain":
        return {"type": "chat", "response": kroger_intent.get("message", "I can only help with grocery questions.")}
        
    if action == "general_chat":
        return {"type": "chat", "response": kroger_intent.get("message", "How can I help you today?")}

        
    if action == "ask_followup":
        return {"type": "chat", "response": kroger_intent.get("message", "Are you making a specific recipe?")}
        
    if action == "search_recipe":
        recipe = kroger_intent.get("recipe_name", "your recipe")
        ingredients = kroger_intent.get("ingredients", [])
        instructions = kroger_intent.get("recipe_instructions")
        exclude_ingredients = kroger_intent.get("exclude_ingredients")
        diet = kroger_intent.get("diet")
        
        # STEP 1: Try Spoonacular as the primary recipe data source
        try:
            from backend.spoonacular_api import search_recipe as spoonacular_search
            spoon_data = spoonacular_search(recipe, exclude_ingredients=exclude_ingredients, diet=diet)
            if spoon_data:
                recipe = spoon_data["recipe_name"]
                if spoon_data["ingredients"]:
                    ingredients = spoon_data["ingredients"]
                
                # Only override instructions if Spoonacular actually found them
                if "No detailed instructions available" not in spoon_data["instructions"]:
                    instructions = spoon_data["instructions"]
                    
                print(f"Loaded recipe from Spoonacular: {recipe}")
                
                # Fix the vague message from rule-based engine
                if "I don't have the exact recipe" in kroger_intent.get("message", ""):
                    kroger_intent["message"] = f"Great choice! {recipe} is delicious. Here's a recipe for you, including the ingredients and steps."
        except Exception as e:
            print(f"Spoonacular integration skipped/failed: {e}")
        
        # STEP 2: If STILL no ingredients (Spoonacular missed too), try a direct Gemini call
        if not ingredients:
            try:
                import json as _json
                api_key = os.environ.get("GEMINI_API_KEY")
                if api_key:
                    from google import genai
                    from google.genai import types
                    client = genai.Client(api_key=api_key)
                    recipe_prompt = f"List ONLY the ingredient names for {recipe}. Return a JSON array of strings. Example: [\"butter\", \"onion\", \"tomato\"]. No quantities, no instructions, just ingredient names."
                    config = types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.0
                    )
                    resp = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[recipe_prompt],
                        config=config
                    )
                    parsed = _json.loads(resp.text)
                    if isinstance(parsed, list) and parsed:
                        ingredients = [i.title() for i in parsed if isinstance(i, str)]
                        print(f"Loaded {len(ingredients)} ingredients from Gemini fallback for '{recipe}'")
                        kroger_intent["message"] = f"Great choice! {recipe} is delicious. Here's a recipe for you, including the ingredients and steps."
            except Exception as e:
                print(f"Gemini recipe fallback failed: {e}")
        
        # STEP 3: If STILL no instructions, try Gemini for that too
        if not instructions and ingredients:
            try:
                import json as _json
                api_key = os.environ.get("GEMINI_API_KEY")
                if api_key:
                    from google import genai
                    from google.genai import types
                    client = genai.Client(api_key=api_key)
                    instr_prompt = f"Give me step-by-step cooking instructions for {recipe}. Return as a single string with numbered steps like '1. Do this. 2. Do that.' Be concise but complete."
                    config = types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.0
                    )
                    resp = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[instr_prompt],
                        config=config
                    )
                    parsed = _json.loads(resp.text)
                    if isinstance(parsed, str):
                        instructions = parsed
                    elif isinstance(parsed, dict):
                        instructions = parsed.get("instructions") or parsed.get("steps") or str(parsed)
                    print(f"Loaded instructions from Gemini fallback for '{recipe}'")
            except Exception as e:
                print(f"Gemini instructions fallback failed: {e}")
        
        reply_message = kroger_intent.get("message", f"Let's get the ingredients for {recipe}.")
        
        if instructions:
            reply_message = f"{reply_message}\n\n**Here is how to make {recipe}:**\n\n{instructions}"
            
        # Look up each ingredient in the Kroger inventory
        found_locally = []
        missing = []
        
        for ing in ingredients:
            res = exact_item_lookup(ing)
            if res["status"] == "success" and res["data"] and any(i["stock"] > 0 for i in res["data"]):
                found_locally.extend([i for i in res["data"] if i["stock"] > 0][:1])
            else:
                missing.append(ing)
                
        # If missing ingredients, query nearby grocery stores within 10 miles
        missing_text = ""
        if missing:
            if user_lat is not None and user_lon is not None:
                nearby = find_nearby_stores(user_lat, user_lon, radius_miles=10)
                if nearby:
                    s = nearby[0]
                    missing_text = f"\n\nWe don't currently have {', '.join(missing)} in stock here, but I checked nearby and **{s['name']}** ({s['distance_miles']} miles away) may have them!"
            
            if not missing_text:
                missing_text = f"\n\nWe don't currently have {', '.join(missing)} in stock here."
                
        reply_message += missing_text
        
        return {
            "type": "inventory_list", 
            "response": {
                "message": reply_message,
                "data": found_locally
            }
        }

    if action == "nearby_store_search":
        if user_lat is not None and user_lon is not None:
            stores = find_nearby_stores(user_lat, user_lon, radius_miles=10)
            closest = stores[0]["name"] + " (" + str(stores[0]["distance_miles"]) + " mi)" if stores else ""
            msg = f"Here are the Kroger locations near you, sorted closest to farthest. The nearest is **{closest}**:" if closest else "Here are the Kroger locations near you:"
            return {
                "type": "store_list",
                "response": {
                    "message": msg,
                    "current_store_id": STORE_ID,
                    "stores": stores
                }
            }
        else:
            return {
                "type": "chat",
                "response": "I need your location to find nearby stores. Please allow location access in your browser and try again!"
            }

    if action == "nearest_store":
        if user_lat is not None and user_lon is not None:
            stores = find_nearby_stores(user_lat, user_lon, radius_miles=10)
            if stores:
                s = stores[0]
                return {
                    "type": "chat",
                    "response": f"The closest Kroger to you is **{s['name']}** at {s['distance_miles']} miles away — {s['address']}. You can reach them at {s['phone']}."
                }
        return {
            "type": "chat",
            "response": "I need your location to find the closest store. Please allow location access in your browser!"
        }

    # FALLBACK ROUTING (if Gemini fails or says "direct_lookup")

    # Handle Gemini Rate Limit Errors gracefully
    is_error = kroger_intent.get("is_error", False)
    if is_error:
        conversational_starters = ["who ", "when ", "why ", "how ", "which ", "recipe", "can you", "list "]
        if any(query_lower.startswith(word) for word in conversational_starters):
            return {"type": "chat", "response": "Sorry, my conversational AI brain is experiencing high volume right now. Could you just search for a simple product name like 'tomatoes' or 'milk' for a moment?"}
            
    # 1. Routing Logic: Is this a complex query requiring Cloud LLM?
    if action == "complex_search":
        intent = "complex_search"
        sql_query = generate_sql_from_text(query)
        result = execute_safe_sql(sql_query)
        log_search(query, intent, len(result.get("data", [])) > 0, False)
        return {"type": "inventory_list", "response": result}
        
    # 2. Routing Logic: Browse Inventory ("what do you have")
    if action == "browse_inventory":
        # Add artificial delay to simulate "checking"
        import time
        time.sleep(1.5)
        
        # Get 6 random items from the database
        res = execute_safe_sql("SELECT * FROM inventory WHERE stock > 0 ORDER BY RANDOM() LIMIT 6")
        return {
            "type": "inventory_list",
            "response": {
                "message": kroger_intent.get("message", "Here are some items we currently have in stock:"),
                "data": res.get("data", [])
            }
        }

    # 4. Routing Logic: Simple Item Lookup
    # Try to use the Gemini-extracted target first for conversational robustness
    raw_item = kroger_intent.get("target_item", "")
    
    # Just in case Gemini included conversational fluff, clean it
    _strip_phrases = [
        "okay how about ", "how about ", "what about ", "where are the ", "where are ",
        "where is the ", "where is ", "could you find ", "can you find ", "i need ",
        "looking for ", "find me ", "do you have ", "do you carry ", "in stock ",
        "any ", "some ", "please ", "just "
    ]
    cleaned = raw_item.lower()
    for phrase in _strip_phrases:
        cleaned = cleaned.replace(phrase, "")
    item_target = cleaned.strip().strip('?.,!')
    
    store_query = kroger_intent.get("target_store_query", "")

    if not item_target:
        return {"type": "chat", "response": kroger_intent.get("message") or "How can I help you find something in the grocery store today?"}

    intent = "simple_lookup"
    target_location_id = None
    target_store_msg = ""
    
    if store_query and user_lat is not None and user_lon is not None:
        stores = find_nearby_stores(user_lat, user_lon, radius_miles=50)
        sq = store_query.lower().replace("branch", "").replace("store", "").strip()
        for s in stores:
            if sq in s['name'].lower() or s['name'].lower() in sq:
                target_location_id = s['store_id']
                target_store_msg = f" at {s['name']}"
                break

    local_result = exact_item_lookup(item_target, location_id=target_location_id)
    
    if local_result["status"] == "success":
        # If the catalog returned absolutely nothing (or everything was filtered out)
        if not local_result["data"]:
            log_search(query, intent, False, True)
            fallback_msg = f"I couldn't find '{item_target}' in our catalog right now. What are you planning to make? I might be able to suggest a substitute!"
            return {"type": "chat", "response": fallback_msg}

        # Check stock level for items that DO exist in the catalog
        in_stock_items = [item for item in local_result["data"] if item["stock"] > 0]
        
        if in_stock_items:
            log_search(query, intent, True, False)
            msg = kroger_intent.get("message", "I found it!")
            if target_store_msg and "found" in msg.lower():
                msg = f"I found it{target_store_msg}!"
                
            return {
                "type": "inventory_item", 
                "response": {
                    "message": msg,
                    "data": in_stock_items[0]
                }
            }
        else:
            # Out of stock — suggest nearby Kroger stores instead of competitors
            log_search(query, intent, False, True)
            if user_lat is not None and user_lon is not None:
                nearby = find_nearby_stores(user_lat, user_lon, radius_miles=15)
                return {
                    "type": "store_list",
                    "response": {
                        "message": f"It looks like **{item_target}** is currently out of stock here. Check these nearby Kroger locations, or tell me what you're making and I can suggest a substitute:",
                        "current_store_id": STORE_ID,
                        "stores": nearby
                    }
                }
            return {"type": "chat", "response": f"We're currently out of {item_target} at this location. Enable location access and I can find you the nearest Kroger that may have it, or let me know what recipe you're cooking for alternative ideas!"}

    else:
        # Not found in Kroger catalog at all
        log_search(query, intent, False, True)
        fallback_msg = f"I couldn't find '{item_target}' in our Kroger catalog. What are you planning to make? I might be able to suggest a substitute or find the ingredients you need!"
        return {"type": "chat", "response": kroger_intent.get("message") or fallback_msg}
