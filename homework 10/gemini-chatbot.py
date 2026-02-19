from dotenv import load_dotenv
from google.genai import Client
load_dotenv()
client=Client()
history=[]
chat=client.chats.create(model="gemini-2.5-flash",history=history)
while True:
    user_input=input("User: ")
    if user_input.strip()=="/bye":
        break
    history.append({"author": "user", "content": user_input})
    ans = chat.send_message(user_input)
    print("Agent:",ans.text)
    history.append({"author": "assistant","content": ans})
