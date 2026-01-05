from datetime import time
from app.db import get_db


redis = get_db()



# Hash (tipo um dict no py)
def hash():
    redis.hset("user:1", mapping={
        "name": "Thiago",
        "email": "thiagop@email.com"
    })

    redis.hget("user:1", "name")



# list (FILA)
# IMPORTANTE: -- Filas FIFO (first in last out) -- Filas LIFO (last in first out) --
def list():
    # entra na fila pela esquerda (início da lista)
    redis.lpush("queue", "msg_na_esquerda")
    redis.lpush("queue", "msg_na_esquerda__2")
    # entra na fila pela direita (final da lista)
    redis.rpush("queue", "msg_na_direita")
    redis.rpush("queue", "msg_na_direita__2")

    # a lista está assim:
    # ["msg_na_esquerda__2", "msg_na_esquerda", "msg_na_direita", "msg_na_direita__2"]

    # -- consumidor de elementos --
 
    # LIFO - entra pelo fim, sai pelo fim 
    redis.rpop("queue")

    # ["msg_na_esquerda__2", "msg_na_esquerda", "msg_na_direita"]

    # ou
    # FIFO - entra pelo começo, sai pelo fim 
    redis.lpop("queue")
    # ["msg_na_esquerda", "msg_na_direita"]



# Set sem duplicar
def set_sem_duplicar():
    redis.sadd("online_users", "thiago")
    redis.smembers("online_users")



# TTL (expiração)
def ttl_expire():
# Os dados abaixo são temporários
# os dados são por segundos
# ele cria essa chave "token" já com tempo de vida 
# Após expirar, o Redis remove automaticamente essa chave

    redis.setex("token", 3600, "textotexto") # 3600 segundos = 1 hora
    # ou

    # Define um tempo de vida (TTL) para uma chave que ja existe
    # Aqui o valor do token NÃO muda, só o tempo de expiração
    # Após 60 segundos, a chave "token" será apagada do Redis

    redis.expire("token", 60) # 60 segundos = 1 minuto

# Rate Limit
def rate_limit():
    # ip do usuário
    # Exemplo: rate:192.168.0.10
    ip = 192168010
    # chave
    key = f"rate:{ip}"
    
    count = redis.incr(key)

    # Se for a PRIMEIRA requisição dentro da janela
    # Define um tempo de vida (TTL) para uma chave que ja existe
    if count == 1:
        redis.expire(key, 60) # 60 segundos = 1 minuto

    # Se ultrapassar o limite permitido dentro da janela
    if count >= 100:
        raise Exception("Too many requests")
    


# Lock Distribuído
def lock_distribuido():

    # O lock distribuído com nome "lock"
    # timeout = tempo máximo que o lock pode ficar preso

    lock = redis.lock("lock", timeout=10)

    # Tenta adquirir o lock
    # blocking=False → não espera, falha se alguém já tiver
    if lock.acquire(blocking=False):
        try:
            # Apenas UM processo entra aqui
            # processar_pagamento(), processar_jogo_c() etc...
            print("DENTRO DO TRY, LOCK AGORA FECHADO!!!!")

            time.sleep(20)
            
        finally:
            lock.release()
            print("LOCK AGORA ABERTO!!!!")
    else:
        # Outro processo já está executando
        print("o recurso já está em uso")




# add função acima para testar e ver funcionando no redis insight