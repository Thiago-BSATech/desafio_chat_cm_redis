from fastapi import WebSocket
import json

async def history_message(list_of_all_messages, ws):
    try:
        for msg in list_of_all_messages:

            data = json.loads(msg)

            formatted = f"[{data['time']}] {data['user']}: {data['text']}"
            await ws.send_text(formatted)

    except Exception as e:
        print("Erro carregando histórico:", e)

async def redis_pusher(db, chat_key, pubsub_key, data):
    # rpush vai criar/adicionar uma/numa lista um dado (mensagem)
    await db.rpush(chat_key, data)
    #  o ltrim limita o tamanho da lista (mantém apenas as ultimas 100 mensagens)
    await db.ltrim(chat_key, -100, -1)
    # publicar no pub/sub
    await db.publish(pubsub_key, data)