import redis.asyncio as redis

client = None

def get_db():
    global client

    if client is None:
        client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        print("Conectado com Redis")

    return client