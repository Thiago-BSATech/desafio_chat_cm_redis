import datetime
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.utils import history_message


ChatPublic = APIRouter()

@ChatPublic.websocket("/ws")
async def chat_ws(ws: WebSocket):
    await ws.accept()

    username = ws.query_params.get("username")
    if not username:
        await ws.close(code=1008)
        return
    

    db = ws.app.state.redis
    # vai pegar o range de cada mensagem (as 50 ultimas) e guardar na variavel
    history = await db.lrange("global_chat_c", -50, -1)

    await history_message(history, ws)

    pubsub = db.pubsub()
    # inscreve este usuario no canal chat_global do Redis.
    await pubsub.subscribe("global_chat_pb")

    try:
        while True:
            
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.01)

            if message:
                await ws.send_text(message["data"])

            try:
                # tenta ler uma mensagem do webSocket sem travar num loop.
                text = await asyncio.wait_for(ws.receive_text(), timeout=0.01)
            except asyncio.TimeoutError:
                continue

            data = json.dumps({
                "user": username,
                "text": text,
                "time": datetime.datetime.utcnow().strftime("%H:%M")
            })
            
            # rpush vai criar/adicionar uma/numa lista um dado (mensagem)
            await db.rpush("global_chat_c", data)
            # # - o ltrim limita o tamanho da lista (mantém apenas as ultimas 100 mensagens)
            await db.ltrim("global_chat_c", -100, -1)
            # publicar no pub/sub
            await db.publish("global_chat_pb", data)

    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe("global_chat_pb")
        await pubsub.close()