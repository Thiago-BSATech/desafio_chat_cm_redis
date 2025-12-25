from fastapi import FastAPI

from app.db import get_db
from app.chats_ws import ChatRoute

app = FastAPI(title='DESAFIO CHAT COM REDIS')

app.include_router(ChatRoute)


@app.on_event("startup")
async def startup():
    app.state.redis = get_db()

@app.on_event("shutdown")
async def shutdown():
    await app.state.redis.close()


print('listening to port 8000')