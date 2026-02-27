import sys
import os
sys.path.append(os.getcwd())
try:
    from backend.agents.state_manager import analyze_kroger_intent
    res = analyze_kroger_intent("session99", "i want to make coleslaw salad")
    print(res)
    res2 = analyze_kroger_intent("session99", "I want the recipe to make paneer butter masala")
    print(res2)
except Exception as e:
    print(e)
