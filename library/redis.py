import redis
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import time
import sys
load_dotenv()

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = int(os.getenv('REDIS_PORT'))
REDIS_SOCKET_TIMEOUT = int(os.getenv('REDIS_SOCKET_TIMEOUT'))
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
LOCK_EXPIRATION_TIME = int(os.getenv('LOCK_EXPIRATION_TIME'))
DB = int(os.getenv('DB'))

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_timeout=REDIS_SOCKET_TIMEOUT, username=USERNAME, password=PASSWORD, db=DB ,decode_responses=True)

class RedisConnector:
    def redis_connectivity(self):
        try:
            redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_timeout=REDIS_SOCKET_TIMEOUT, username=USERNAME, password=PASSWORD, db=DB ,decode_responses=True)
            connection=redis_client.ping()
            print(f"Connection to redis {REDIS_HOST} {REDIS_PORT} on DB {DB} successfully established.")

        except Exception as e:
            print(f"Exception occurred. Cannot connect to redis host {REDIS_HOST} {REDIS_PORT}: {e}")
            exit(1)


    def lock_resource(self, resource: str) -> None:

            key = f"resource:{resource}"
            acquired = redis_client.set(key, "locked", ex=LOCK_EXPIRATION_TIME, nx=True)
            if not acquired:
                raise HTTPException(status_code=409, detail="resource already locked")
            
    def unlock_resource(self, resource: str) -> None:
            key = f"resource:{resource}"
            delete_lock = redis_client.delete(key)
            print ("Now Unlocking the Resource", resource)
            if not delete_lock:
                raise HTTPException(status_code=409, detail="Lock Not deleted")
            
    # def redis_connectivity_checker(self):
    #     while True:
    #         try:
    #             redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_timeout=REDIS_SOCKET_TIMEOUT, username=USERNAME, password=PASSWORD, db=DB, decode_responses=True)
    #             connection = redis_client.ping()
    #             #print(f"Connection to redis {REDIS_HOST}:{REDIS_PORT} on DB {DB} successfully established.")
    #             time.sleep(100)
    #         except Exception as e:
    #             print(f"Exception occurred. Cannot connect to Redis host {REDIS_HOST}:{REDIS_PORT}: {e}")
    #             os.execv(sys.executable, ['python3'] + sys.argv)