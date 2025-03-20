from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .user import User
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="messages")