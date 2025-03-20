import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..models import User
from ..schemas.token import Token, TokenData
from ..schemas.user import UserCreate
from ..models.user import verify_password

# JWT geçerlilik süresi
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Şifreleme işlemleri için CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# SECRET_KEY ve ALGORITHM'ı buraya ekleyebilirsin
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, db: Session, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    return token_data

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user