from fastapi import FastAPI


app = FastAPI(title='DESAFIO CHAT COM REDIS')


# app.include_router(ChatPrivate)
# app.include_router(ChatPublic)

print('listening to port 8000')