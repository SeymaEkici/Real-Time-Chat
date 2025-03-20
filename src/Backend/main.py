from fastapi import FastAPI, WebSocket
from typing import List

app = FastAPI()

# Bağlantıları tutan sözlük
clients = {}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    # Bağlantıyı kabul et
    await websocket.accept()
    
    # Yeni istemciyi client_id ile kaydediyoruz
    clients[client_id] = websocket
    
    try:
        while True:
            # İstemciden gelen mesajı al
            data = await websocket.receive_text()
            
            # Bu mesajı tüm bağlı istemcilere gönder
            for client in clients.values():
                if client != websocket:
                    await client.send_text(f"Client {client_id}: {data}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Bağlantıyı kapatırken istemciyi listeden çıkar
        del clients[client_id]
        await websocket.close()
