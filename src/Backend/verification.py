from fastapi import Depends, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

# Gizli anahtar
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2PasswordBearer'ı kimlik doğrulaması için kullanıyoruz
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Token doğrulama fonksiyonu
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)  # Token doğrulama
    await websocket.accept()
    
    # WebSocket bağlantısı ve JWT doğrulama sonrasında işlemler
    clients[client_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            
            for client in clients.values():
                if client != websocket:
                    await client.send_text(f"Client {client_id}: {data}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        del clients[client_id]
        await websocket.close()
