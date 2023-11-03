from kubernetes import client, config, watch
import re
import json
import os
import subprocess
import redis
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from kubernetes.client.rest import ApiException
import json
import datetime
import threading
import time
import sys


config.load_kube_config()
# REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_HOST = "tajawal-dev-cms-core.hnk4p0.ng.0001.euw1.cache.amazonaws.com"
REDIS_PORT = 6379
while True:
 try:
       redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_timeout=1)
       connection=redis_client.ping()
       print(connection)

 except Exception as e:
      print(f"Exception occurred. Cannot connect to redis host {REDIS_HOST} {REDIS_PORT}: {e}")
      exit(1)
