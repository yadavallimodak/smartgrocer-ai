from backend.agents.sql_agent import exact_item_lookup, _CATEGORY_AISLE

print("Dict has Pantry?", "Pantry" in _CATEGORY_AISLE)
print("Pantry value:", _CATEGORY_AISLE.get("Pantry"))

res = exact_item_lookup("1/2 Cup Salsa")
for idx, data in enumerate(res.get("data", [])):
    print(f"Item:", data["name"])
    print(f"Category:", data["category"])
    print(f"Aisle:", data["aisle"])
    print("-----")
