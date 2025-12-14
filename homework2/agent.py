from google.genai import Client
from google.genai.types import UserContent, ModelContent
from models import Message
from db import SessionLocal

HISTORY_LIMIT = 10


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



class Agent:
    def __init__(self, room_id):
        self.session = SessionLocal()
        self.room_id = room_id
        self.client = Client()

        history = self._load_history()
        self.chat = self.client.chats.create(
            model="gemini-2.5-flash-lite",
            history=history
        )

    def _load_history(self):
        msgs = (
            self.session.query(Message)
            .filter_by(room_id=self.room_id)
            .order_by(Message.created_at.desc())
            .limit(HISTORY_LIMIT)
            .all()
        )
        msgs.reverse()

        history = []
        for m in msgs:
            if m.role == "user":
                history.append(UserContent(m.content))
            else:
                history.append(ModelContent(m.content))
        return history

    def ask(self, text):
        reply = self.chat.send_message(text).text

        self.session.add_all([
            Message(room_id=self.room_id, role="user", content=text),
            Message(room_id=self.room_id, role="model", content=reply),
        ])
        self.session.commit()

        return reply
