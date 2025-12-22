from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    
    rooms = relationship("ChatRoom", back_populates="owner")


class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="rooms")
    messages = relationship("Message", back_populates="room")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"))
    role = Column(String(10))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

    room = relationship("ChatRoom", back_populates="messages")
