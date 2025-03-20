# database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

SQLALCHEMY_DATABASE_URL = "postgresql://chatuser:HappyCat@localhost/chatapp"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    messages = relationship("Message", back_populates="sender")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    sender_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    sender = relationship("User", back_populates="messages")
    room = relationship("Room", back_populates="messages")

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    messages = relationship("Message", back_populates="room")

# Create the tables
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()