from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Configuration
SECRET_KEY = "your_secret_key"  # Change this in production and use environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2PasswordBearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    password: str

# Mock database - Replace with actual database
users_db = {
    "testuser": {
        "username": "testuser",
        "password": "testpassword"  # In production, use hashed passwords
    }
}

# Connected WebSocket clients
active_connections: Dict[str, WebSocket] = {}

# Authentication functions
def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if not user:
        return False
    if user["password"] != password:  # In production, use password hashing
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

# Routes
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            message = f"Client {client_id}: {data}"
            
            # Broadcast the message to all connected clients
            for connection in active_connections.values():
                if connection != websocket:  # Don't send back to the sender
                    await connection.send_text(message)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if client_id in active_connections:
            del active_connections[client_id]

# Secured WebSocket endpoint (requires authentication)
@app.websocket("/secured-ws/{client_id}")
async def secured_websocket_endpoint(websocket: WebSocket, client_id: str, token: str = None):
    # Extract token from query parameters
    await websocket.accept()
    
    # Verify token
    try:
        if not token:
            await websocket.send_text("Authentication required")
            await websocket.close()
            return
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            await websocket.send_text("Invalid authentication token")
            await websocket.close()
            return
    except JWTError:
        await websocket.send_text("Invalid authentication token")
        await websocket.close()
        return
    
    active_connections[client_id] = websocket
    
    try:
        # Send a welcome message
        await websocket.send_text(f"Welcome {username}!")
        
        while True:
            data = await websocket.receive_text()
            message = f"User {username} (Client {client_id}): {data}"
            
            # Broadcast the message
            for connection in active_connections.values():
                if connection != websocket:
                    await connection.send_text(message)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if client_id in active_connections:
            del active_connections[client_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)