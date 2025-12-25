import datetime
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.utils import history_message, redis_pusher


ChatRoute = APIRouter()

@ChatRoute.websocket("/ws")
async def chat_ws(ws: WebSocket):

    await ws.accept()

    username = ws.query_params.get("username")
    if not username:
        await ws.close(code=1008)
        return

    try:
        no_response = True
        responses = ["/global", "/private", "/group"]
        print("ESCOLHA UM CHAT PARA ENTRAR: ")
        print(responses)
        print(
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

    if response == "/global":
        try:
            # vai pegar o range de cada mensagem (as 50 ultimas) e guardar na variavel
            history = await db.lrange("global_chat_c", -50, -1)
            await history_message(history, ws)
            # inscreve este usuario no canal chat_global do Redis.
            await pubsub.subscribe("global_chat_pb")

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
                
                await redis_pusher(db, "global_chat_c", "global_chat_pb", data)

        except WebSocketDisconnect:
            pass
        finally:
            await pubsub.unsubscribe("global_chat_pb")
            await pubsub.close()

    elif response == "/private":
        try:
            target = ws.query_params.get("target")

            if not target:
                print("informe o destinatário nos parametros")
                await ws.close(code=1008)
                return

            # canal único e ordenado (evita duplicar conversa)
            users = sorted([username, target])

            chat_key = f"private:{users[0]}:{users[1]}:c"
            pub_key = f"private:{users[0]}:{users[1]}:pb"

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
                

        except WebSocketDisconnect:
            pass
        finally:
            await pubsub.unsubscribe(pub_key)
            await pubsub.close()


    elif response == "/group":
        try:

            group = ws.query_params.get("group")
            if not group:
                print("informe o group nos parametros")
                await ws.close(code=1008)
                return

            chat_key = f"group_chat_c:{group}"
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
                

        except WebSocketDisconnect:
            pass
        finally:
            await pubsub.unsubscribe(pub_key)
            await pubsub.close()