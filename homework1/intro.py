import json
import os
from dotenv import load_dotenv
from google import genai
history_f = "chat_history.json"
def load_history():
    if os.path.exists(history_f):
        with open(history_f, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
def save_history(history):
    with open(history_f, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

load_dotenv('.env')
client = genai.Client()

print("Chat Started! Type 'quit' to exit.\nType 'clear' to delete chat history.")

history = load_history()
# if history:
#     print("Previous Chat Loaded:")
#     for msg in history:
#         print(f"{msg['role']}: {msg['text']}")
#     print()
while 1:
    user_input = input("User: ").strip()
    if user_input.lower() == "quit":
        print("Exiting… chat saved.")
        save_history(history)
        break
    if user_input.lower() == "clear":
        history = []
        save_history(history)
        print("Chat history cleared!")
        continue
    history+=[{"role": "user", "text": user_input}]
    full_conversation = "\n".join(
        f"{msg['role']}: {msg['text']}" for msg in history
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_conversation
    )
    AI_reply = response.text.strip()
    print("AI:", AI_reply)
    history+=[{"role": "AI", "text": AI_reply}]
    save_history(history)