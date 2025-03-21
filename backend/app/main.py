from fastapi import FastAPI, WebSocket, Depends, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from sqlalchemy.orm import Session
from app.db.database import get_db, User, Message, Room
from fastapi.responses import JSONResponse

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connected WebSocket clients
active_connections: Dict[str, WebSocket] = {}

# User routes
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        # Create new user if not exists (simple signup)
        user = User(username=username, password=password)
        db.add(user)
        db.commit()
        db.refresh(user)
    elif user.password != password:
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    return {"username": user.username, "user_id": user.id}

# Room routes
@app.get("/rooms")
async def get_rooms(db: Session = Depends(get_db)):
    rooms = db.query(Room).all()
    return [{"id": room.id, "name": room.name} for room in rooms]

@app.post("/rooms")
async def create_room(name: str = Form(...), db: Session = Depends(get_db)):
    room = Room(name=name)
    db.add(room)
    db.commit()
    db.refresh(room)
    return {"id": room.id, "name": room.name}

# Message routes
@app.get("/messages/{room_id}")
async def get_messages(room_id: int, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(Message.room_id == room_id).all()
    return [
        {
            "id": msg.id,
            "content": msg.content,
            "sender": msg.sender.username,
            "created_at": msg.created_at
        } 
        for msg in messages
    ]

# WebSocket endpoints
@app.websocket("/ws/{client_id}/{room_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str, room_id: int, db: Session = Depends(get_db)):
    await websocket.accept()
    
    # Store connection with room_id
    connection_key = f"{client_id}_{room_id}"
    active_connections[connection_key] = websocket
    
    try:
        while True:
            # Receive the data from websocket
            data = await websocket.receive_json()
            username = data.get("username")
            message_content = data.get("message")
            
            # Get user from database
            user = db.query(User).filter(User.username == username).first()
            if not user:
                continue
            
            # Save message to database
            message = Message(content=message_content, sender_id=user.id, room_id=room_id)
            db.add(message)
            db.commit()
            
            # Broadcast message to all clients in the same room
            formatted_message = {
                "sender": username,
                "content": message_content,
                "timestamp": message.created_at.isoformat()
            }
            
            # Send to all connections in the same room
            for connection_id, connection in active_connections.items():
                if connection_id.endswith(f"_{room_id}"):
                    await connection.send_json(formatted_message)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection_key in active_connections:
            del active_connections[connection_key]

# Create default room if none exists
@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    if db.query(Room).count() == 0:
        default_room = Room(name="General")
        db.add(default_room)
        db.commit()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)