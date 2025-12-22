import redis

client = None

def get_db():

    global client

    if client is None:
        try:
            client = redis.Redis(
                host='localhost', 
                port=6379, 
                decode_responses=True
            )

            print("Conectado com Redis")

            return client
            
        except Exception as e:
            raise Exception('AN ERROR HAS OCURRED', e)
        

# test = get_db()

# test.set('foo', 'test----test')