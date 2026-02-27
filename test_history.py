import sys
import os
sys.path.append(os.getcwd())
try:
    from backend.agents.state_manager import session_store, analyze_kroger_intent
    # Mocking the session history
    session_store["test_session"] = [
        {"role": "user", "content": "do you have tomatoes"},
        {"role": "assistant", "content": "Of course! May I ask what you're planning to make with the tomatoes? I can also help you make Tomato Sauce, Pasta, Tacos if you're interested! 😊"},
    ]
    res = analyze_kroger_intent("test_session", "I would like to make a tomato salad bowl with some crunchy snacks")
    print(res)
except Exception as e:
    print(e)
