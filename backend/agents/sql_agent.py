from backend.database import get_db_connection
import os

_STORE_ID = os.environ.get("STORE_ID", "01400943")

# Category → typical grocery aisle mapping for display purposes
_CATEGORY_AISLE = {
    "Produce": "1",
    "Dairy": "9",
    "Bakery": "8",
    "Baking Goods": "7",
    "Meat": "12",
    "Seafood": "11",
    "Frozen": "15",
    "Beverages": "6",
    "Snacks": "5",
    "Cereal": "4",
    "Canned & Packaged": "3",
    "Pasta": "3",
    "Sauces": "3",
    "Condiments": "3",
    "Natural & Organic": "2",
    "Pantry": "7",
    "Deli": "10",
    "Personal Care": "16",
    "Baby": "17",
    "Household": "18",
}

# Store address lookup by locationId
_STORE_ADDRESSES = {
    "01400943": "5225 State Hwy 121, The Colony, TX",
    "01401234": "4709 W University Dr, Prosper, TX",
    "01401567": "2580 Dallas Pkwy, Frisco, TX",
    "01401890": "5901 Ohio Dr, Frisco, TX",
    "01402100": "2350 Lake Vista Dr, Lewisville, TX",
    "01402350": "750 E Hebron Pkwy, Carrollton, TX",
}

from functools import lru_cache

# Categories that are cooking/food items — used to deprioritize supplements, health products
_COOKING_CATEGORIES = {
    "Produce", "Dairy", "Bakery", "Baking Goods", "Meat", "Seafood",
    "Frozen", "Beverages", "Snacks", "Cereal", "Canned & Packaged",
    "Pasta", "Sauces", "Condiments", "Pantry", "Deli", "Natural & Organic",
}

# Product name patterns that indicate supplements, NOT cooking ingredients
_SUPPLEMENT_KEYWORDS = [
    "immune support", "supplement", "vitamin", "emergen-c", "emergen c",
    "capsule", "tablet", "softgel", "gummies", "wellness",
    "probiotic", "multivitamin", "dietary", "health support",
]

@lru_cache(maxsize=128)
def exact_item_lookup(item_name: str, location_id: str = None, recipe_context: bool = False) -> dict:
    """Fast lookup using the live Kroger API (or mock wrapper) instead of local DB.
    
    When recipe_context=True, supplements/health products are filtered out
    so we only return actual cooking ingredients.
    """
    from backend.kroger_api import search_products
    
    target_store = location_id if location_id else _STORE_ID

    # Query the Kroger API using the configured (or overridden) store ID
    api_response = search_products(item_name, location_id=target_store)

    if not api_response.get("data"):
        return {"status": "not_found", "message": f"Could not find '{item_name}' in the Kroger Catalog."}

    # Map the Kroger OpenAPI response to our internal simple format for the frontend
    results = []
    for item in api_response["data"]:
        # ── Name ────────────────────────────────────────────────────────────
        name = item.get("description") or item.get("name") or "Grocery Item"

        # ── Relevance Filter ────────────────────────────────────────────────
        # Prevent Kroger's aggressive stemming from returning Frying Pans for "Paneer"
        term_lower = item_name.lower()
        name_lower = name.lower()
        if term_lower not in name_lower:
            # If the exact phrase isn't there, require at least one >2 char word to match
            words = [w for w in term_lower.replace('-', ' ').split() if len(w) > 2]
            # Some queries like "2%" might be short, so only enforce if we have words
            if words and not any(w in name_lower for w in words):
                continue

        # ── Price & Stock (from items[] array, NOT locations[]) ─────────────
        item_detail = (item.get("items") or [{}])[0]
        price_obj   = item_detail.get("price") or {}
        price       = price_obj.get("promo") or price_obj.get("regular") or 0.0
        size        = item_detail.get("size", "")

        stock_level = item_detail.get("inventory", {}).get("stockLevel", "")
        if stock_level in ["HIGH", "MEDIUM", "LOW"]:
            stock_count = 50
        elif stock_level == "TEMPORARILY_OUT_OF_STOCK":
            stock_count = 0
        else:
            # No stock info returned — product exists in catalog, assume in-store
            stock_count = 50

        # ── Category ────────────────────────────────────────────────────────
        raw_cats  = item.get("categories") or []
        first_cat = raw_cats[0] if raw_cats else "Grocery"
        cat       = first_cat if isinstance(first_cat, str) else first_cat.get("name", "Grocery")

        # ── Aisle ───────────────────────────────────────────────────────────
        aisle = "TBD"
        locations = item.get("locations") or []
        if locations:
            aisle_locs = locations[0].get("aisleLocations") or []
            if aisle_locs:
                loc = aisle_locs[0]
                # Real API uses 'number' or 'description', mock uses 'aisle'
                aisle = loc.get("number") or loc.get("description") or loc.get("bayNumber") or loc.get("aisle", "TBD")
        
        # Fallback to category estimate only if API truly misses it
        if aisle == "TBD":
            aisle = _CATEGORY_AISLE.get(cat, "TBD")

        # ── Store address ────────────────────────────────────────────────────
        store_address = _STORE_ADDRESSES.get(_STORE_ID, f"Store #{_STORE_ID}")

        # ── Best product image ───────────────────────────────────────────────
        image = None
        images = item.get("images") or []
        if images:
            sizes = images[0].get("sizes") or []
            xlarge = next((s["url"] for s in sizes if s.get("size") == "xlarge"), None)
            image  = xlarge or (sizes[0].get("url") if sizes else None)

        # ── Recipe context filtering ─────────────────────────────────────────
        # When searching for recipe ingredients, skip supplements & health products
        if recipe_context:
            if any(kw in name_lower for kw in _SUPPLEMENT_KEYWORDS):
                continue

        results.append({
            "id":            item.get("upc"),
            "name":          name,
            "size":          size,
            "category":      cat,
            "aisle":         aisle,
            "location_id":   _STORE_ID,
            "store_address": store_address,
            "stock":         stock_count,
            "price":         price,
            "image":         image,
        })

    return {"status": "success", "data": results}

def execute_safe_sql(sql_query: str) -> dict:
    """Executes a READ-ONLY SQL query generated by the Cloud LLM."""
    if "DROP" in sql_query.upper() or "UPDATE" in sql_query.upper() or "INSERT" in sql_query.upper() or "DELETE" in sql_query.upper():
        return {"status": "error", "message": "Unsafe SQL operation blocked."}
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        # Limit results for safety
        results = [dict(row) for row in cursor.fetchmany(10)]
        conn.close()
        return {"status": "success", "data": results}
    except Exception as e:
        return {"status": "error", "message": f"SQL Error: {str(e)}"}
