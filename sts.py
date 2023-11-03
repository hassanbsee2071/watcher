from kubernetes import client, config, watch
import re
import json
import os
import subprocess
import redis
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from kubernetes.client.rest import ApiException
import datetime

def restart_deployment(v1_apps, deployment_name, namespace):
    now = datetime.datetime.utcnow()
    now = str(now.isoformat("T") + "Z")
    body = {
        'spec': {
            'template':{
                'metadata': {
                    'annotations': {
                        'kubectl.kubernetes.io/restartedAt': now
                    }
                }
            }
        }
    }
    for deployment in deployment_name:
        try:
            print ("Rolling out Restart Deployment:", deployment)
            v1_apps.patch_namespaced_stateful_set(deployment, namespace, body, pretty='true')
        except ApiException as e:
            print("Exception when calling AppsV1Api->read_namespaced_deployment_status: %s\n" % e)



config.load_kube_config()
# REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_HOST = "tajawal-dev-cms-core.hnk4p0.ng.0001.euw1.cache.amazonaws.com"
REDIS_PORT = 6379
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
LOCK_EXPIRATION_TIME = 300  # 5 minutes
#deployment_name=[]
v1 = client.CoreV1Api()
deployment = client.AppsV1Api()

namespace="devops"
deployment_name=["dev-zookeeper","rabbitmq-test"]


deployments = deployment.list_namespaced_stateful_set(namespace=namespace)
print(deployments)
restart_deployment(deployment, deployment_name, namespace)
