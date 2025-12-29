import datetime
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.utils import history_message, redis_pusher


ChatRoute = APIRouter()

responses = ["/global", "/private", "/group"]

@ChatRoute.websocket("/ws")
async def chat_ws(ws: WebSocket):

    await ws.accept()

    username = ws.query_params.get("username")
    if not username:
        raise Exception("informe o destinatário nos parametros")

    try:
        no_response = True
        
        await ws.send_text(f"ESCOLHA UM CHAT PARA ENTRAR: {responses}")
        await ws.send_text(
            """
                parametros: username(obrigatório para todos os chats), 
                group: indique o grupo no qual quer se juntar (apenas para o group),
                target: indique a pessoa na qual você quer conversar(apenas para o private)
            """
        )
        

        while no_response:
            response = await ws.receive_text()

            if response not in responses:
                ws.send_text(f"mande uma resposta valida!!: {responses}")
                continue
            else:
                no_response = False
                
    except WebSocketDisconnect:
        pass

    db = ws.app.state.redis
    pubsub = db.pubsub()

    try:
        if response == "/global":

            chat_key = "global_chat_key"
            pub_key = "global_chat_pb"

            # vai pegar o range de cada mensagem (as 50 ultimas) e guardar na variavel
            history = await db.lrange(chat_key, -50, -1)
            await history_message(history, ws)
            # inscreve este usuario no canal chat_global do Redis.
            await pubsub.subscribe(pub_key)

            while True:
                
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.01)

                if message:
                    await ws.send_text(message["data"])

                try:
                    # tenta ler uma mensagem do webSocket sem travar num loop.
                    text = await asyncio.wait_for(ws.receive_text(), timeout=0.01)
                except asyncio.TimeoutError:
                    # Nenhuma mensagem do usuário, segue o loop até ter
                    continue

                data = json.dumps({
                    "user": username,
                    "text": text,
                    "time": datetime.datetime.utcnow().strftime("%H:%M")
                })
                
                await redis_pusher(db, chat_key, pub_key, data)

        elif response == "/private":
    
            target = ws.query_params.get("target")

            if not target:
                raise Exception("informe o destinatário nos parametros")

            # Chave entre os dois usuários
            users = sorted([username, target])

            chat_key = f"private:{users[0]}-{users[1]}_key"
            pub_key = f"private:{users[0]}-{users[1]}_pb"

            history = await db.lrange(chat_key, -50, -1)
            await history_message(history, ws)

            await pubsub.subscribe(pub_key)

            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.01)

                if message:
                    await ws.send_text(message["data"])

                try:
                    text = await asyncio.wait_for(ws.receive_text(), timeout=0.01)
                except asyncio.TimeoutError:
                    continue

                data = json.dumps({
                    "user": username,
                    "text": text,
                    "time": datetime.datetime.utcnow().strftime("%H:%M")
                })

                await redis_pusher(db, chat_key, pub_key, data)

        elif response == "/group":
        
            group = ws.query_params.get("group")
            if not group:
                raise Exception("informe o group nos parametros")

            chat_key = f"group_chat_keys:{group}"
            pub_key = f"group_chat_pb:{group}"

            history = await db.lrange(chat_key, -50, -1)
            await history_message(history, ws)

            await pubsub.subscribe(pub_key)

            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.01)

                if message:
                    await ws.send_text(message["data"])

                try:
                    text = await asyncio.wait_for(ws.receive_text(), timeout=0.01)
                except asyncio.TimeoutError:
                    continue

                data = json.dumps({
                    "user": username,
                    "text": text,
                    "time": datetime.datetime.utcnow().strftime("%H:%M")
                })

                await redis_pusher(db, chat_key, pub_key, data)
                    
    except Exception:
        await ws.close()
    finally:
        try:
            await pubsub.unsubscribe(pub_key)
            await pubsub.close()
        except Exception as e:
            print("erro no pubsub: ", e)