from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import validates
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext

Base = declarative_base()

# Hashleme için passlib context oluşturuluyor
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    @validates("hashed_password")
    def validate_password(self, key, password):
        # Burada password'u hash'liyoruz
        return hash_password(password)