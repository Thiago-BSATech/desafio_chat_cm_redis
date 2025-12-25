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