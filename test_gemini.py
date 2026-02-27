import os
from backend.agents.state_manager import analyze_kroger_intent
os.environ["GEMINI_API_KEY"] = "AIzaSyAbKwNZ2gkn3kbXdKW6zdVIdWcLfEzik80"

print("Testing Gemini directly...")
try:
    res = analyze_kroger_intent("test_session", "what all do you hawhat alvl do eyou have")
    print("Result:", res)
except Exception as e:
    print("Caught Exception:", e)
