import datetime
from fastapi import APIRouter, WebSocket
from app.db import get_db
from app.dtos import ChatPublicRequest 

ChatPublic = APIRouter()
db = get_db()

@ChatPublic.websocket('/ws')
async def chat_public_ws(ws: WebSocket, body: ChatPublicRequest):
    
    await ws.accept()

    try:
        while True:
            text = await ws.receive_text()
            if len(text) > 150:
                text = "..."
                return "Payload too large"
                
            time = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M")

            final_message = f"[{time}] {body.username}: {text}"

            # set into db redis final message -->

    except Exception as e:
        raise Exception('AN ERROR HAS OCURRED', e)