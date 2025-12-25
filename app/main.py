from fastapi import FastAPI

from app.db import get_db
from app.websockets.chat_private_ws import ChatPrivate
from app.websockets.chat_public_ws import ChatPublic

app = FastAPI(title='DESAFIO CHAT COM REDIS')

app.include_router(ChatPublic)
app.include_router(ChatPrivate)


@app.on_event("startup")
async def startup():
    app.state.redis = get_db()

@app.on_event("shutdown")
async def shutdown():
    await app.state.redis.close()


print('listening to port 8000')