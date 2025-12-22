from google.genai import Client
from google.genai.types import UserContent, ModelContent, Part
from models import Message
from google.genai import types
from db import SessionLocal
from math import *

def show_history_pairs(session, room_id, pairs):
    msgs = (
        session.query(Message)
        .filter_by(room_id=room_id)
        .order_by(Message.created_at.asc())
        .all()
    )
    pairs_list = []
    i = 0
    while i < len(msgs) - 1:
        if msgs[i].role == "user" and msgs[i + 1].role == "model":
            pairs_list.append((msgs[i], msgs[i + 1]))
            i += 2
        else:
            i += 1
    pairs_list = pairs_list[-pairs:]
    for user_msg, model_msg in pairs_list:
        print(f"[user] {user_msg.content}")
        print(f"[model] {model_msg.content}")
def mul(a: float, b: float) -> float: 
    """
    Returns a * b
    Rules:
    - ONLY use math tools when the user explicitly asks for a calculation.
    """
    return a * b

def add(a: float, b: float) -> float:
    """
    Returns a + b
    Rules:
    - ONLY use math tools when the user explicitly asks for a calculation.
    """
    return a + b

def subtract(a: float, b: float) -> float:
    """
    Returns a - b
    Rules:
    - ONLY use math tools when the user explicitly asks for a calculation.
    """
    return a - b

def divide(a: float, b: float):
    """
    Returns a / b 
    Rules:
    - ONLY use math tools when the user explicitly asks for a calculation.
    """
    if b == 0:
        return "Cannot divide by zero."
    return a / b
def count_factors(n: int) -> int:
    """
    Rules:
    - ONLY use math tools when the user explicitly asks for a calculation.
    - ONLY find the divisors of number when it is asked otherwise don't please!!!
    Calculates the total number of divisors (factors) for a given integer n.

    Args:
        n (int): The positive integer to be analyzed.

    Returns:
        int: The total count of factors, including 1 and the number itself.
    """
    if n <= 0: return 0
    if n == 1: return 1
    k = 1
    i = 2
    a = n
    while i * i <= n:
        if a % i == 0:
            e = 0
            while a % i == 0:
                e += 1
                a //= i
            k *= (e + 1)
        i += 1
    if a > 1: k *= 2
    return k

config = types.GenerateContentConfig(
    tools=[mul,add,subtract,divide,count_factors],
)

class Agent:
    def __init__(self, room_id):
        self.session = SessionLocal()
        self.room_id = room_id
        self.client = Client()
        history = self._load_history()

        self.chat = self.client.chats.create(
            model="gemini-2.5-flash-lite",
            history=history,
            config=config
        )
    def _load_history(self):
        msgs = (
            self.session.query(Message)
            .filter_by(room_id=self.room_id)
            .order_by(Message.created_at.desc())
            .all()
        )
        msgs.reverse()

        history = []
        for m in msgs:
            if m.role == "user":
                history.append(
                    UserContent(parts=[Part(text=m.content)])
                )
            else:
                history.append(
                    ModelContent(parts=[Part(text=m.content)])
                )
        return history


    def ask(self, text):
        response = self.chat.send_message(text)
        candidate = response.candidates[0]
        content = candidate.content
        if content and content.parts and content.parts[0].function_call:
            part = content.parts[0]
            name = part.function_call.name
            args = part.function_call.args
            if name == "add":
                result = add(**args)
            elif name == "mul":
                result = mul(**args)
            elif name == "subtract":
                result = subtract(**args)
            elif name == "divide":
                result = divide(**args)
            elif name == "count_factors":
                result = count_factors(**args)
            else:
                result = ""

            tool_response = self.chat.send_message(str(result))
            reply = tool_response.candidates[0].content.parts[0].text
        else:
            reply = response.text

        self.session.add_all([
            Message(room_id=self.room_id, role="user", content=text),
            Message(room_id=self.room_id, role="model", content=reply),
        ])
        self.session.commit()

        return reply

