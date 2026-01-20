import datetime
import json
import asyncio

from fastapi import APIRouter, WebSocket

from app.dtos import ChatDTO
from app.utils import history_message, redirect, redis_pusher


ChatRoute = APIRouter()

@ChatRoute.websocket("/ws")
async def chat_ws(ws: WebSocket):
    try:
        await ws.accept()

        username = ws.query_params.get("username")
        if not username:
            raise Exception("informe o destinatário nos parametros")

        db = ws.app.state.redis
        pubsub = db.pubsub()

        while True:

            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.01)

            if message:
                
                chat_enviado = message['data']['CHAT']

                if not chat_enviado:
                    
                    re = redirect(chat_enviado, username)

                    # vai pegar o range de cada mensagem (as 50 ultimas) e guardar na variavel
                    history = await db.lrange(re, -50, -1)
                    await history_message(history, ws)
                    # inscreve este usuario no canal chat_global do Redis.
                    await pubsub.subscribe(re)

                # verificação de comando e retornar o evento:
    
                # await ws.send_json({"event": 1, "message": message["data"]})


            try:
                # tenta ler uma mensagem do webSocket sem travar num loop.
                text = await asyncio.wait_for(ws.receive_json(), timeout=0.01)
            except asyncio.TimeoutError:
                # Nenhuma mensagem do usuário, segue o loop até ter
                continue

            data = json.dumps({
                "user": username,
                "text": text,
                "time": datetime.datetime.utcnow().strftime("%H:%M")
            })
            
            await redis_pusher(db, re, re, data)

    except Exception as e:
        await ws.close()
        print(e)
    finally:
        try:
            await pubsub.unsubscribe(re)
            await pubsub.close()
        except Exception as e:
            print("erro no pubsub: ", e)