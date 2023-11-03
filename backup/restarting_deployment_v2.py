#some sts like dev-zookeeper in devops cannot rollout restart both via kubectl command or python ####
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

#tajawal-dev-cms-core.hnk4p0.ng.0001.euw1.cache.amazonaws.com 6379
config.load_kube_config()
# REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_HOST = "tajawal-dev-cms-core.hnk4p0.ng.0001.euw1.cache.amazonaws.com"
REDIS_PORT = 6379
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
LOCK_EXPIRATION_TIME = 300  # 5 minutes
deployment_name=[]
v1 = client.CoreV1Api()
deployment = client.AppsV1Api()


def lock_seat(resource: str) -> None:

    key = f"resource:{resource}"
    acquired = redis_client.set(key, "locked", ex=LOCK_EXPIRATION_TIME, nx=True)
    if not acquired:
        raise HTTPException(status_code=409, detail="resource already locked")
    
# def lock_seat(resource: str) -> None:
#     key = f"resource:{resource}"
#     acquired = redis_client.set(key, "locked", ex=LOCK_EXPIRATION_TIME, nx=True)
#     if not acquired:
#         # Instead of raising the exception directly, you can raise it and catch it
#         # to continue program execution.
#         try:
#             raise HTTPException(status_code=409, detail="Resource already locked")
#         except HTTPException as e:
#             # Handle the exception gracefully, e.g., log it or perform other actions.
#             print(f"Caught an exception: {e}")
    
#     # Continue with program execution after handling the exception (if necessary)
#     print("Resource locked successfully")

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
            v1_apps.patch_namespaced_deployment(deployment, namespace, body, pretty='true')
        except ApiException as e:
            print("Exception when calling AppsV1Api->read_namespaced_deployment_status: %s\n" % e)


w = watch.Watch()
file_path = "output_file.txt"
#for event in w.stream(v1.list_config_map_for_all_namespaces, _request_timeout=60):
ignore_namespace = ['ingress-aws-lb-controller', 'istio-system', 'karpenter', 'kube-system', 'kubesphere-system']
for event in w.stream(v1.list_config_map_for_all_namespaces):
    if event["type"] == "MODIFIED":
        #print("Event: %s %s %s" % (event['type'], event['object'].metadata.name, event['object'].metadata.namespace))
        if event['object'].metadata.namespace not in ignore_namespace:
            #print("Event: %s %s %s" % (event['type'], event['object'].metadata.name, event['object'].metadata.namespace))
            print ("Not excluded...")
            namespace = event['object'].metadata.namespace
            configmap = event['object'].metadata.name
            kind = event['object'].kind
            #print ("Kind is:", kind)
            #print ("Namespace Name:", namespace)
            #print ("Configmap Name:", configmap)
            try:
                lock_seat(configmap)
                #print (JSONResponse(status_code=200, content={"message": "Configmap locked"}))
                deployments = deployment.list_namespaced_deployment(namespace=namespace)
                #if re.search(configmap, str(deployments)):
                for item in deployments.items:
                    if re.search(configmap, str(item)):
                        print("Deployment Name is:", item.metadata.name)
                        deployment_name.append(item.metadata.name)
                        kind_array = json.loads(item.metadata.annotations['kubectl.kubernetes.io/last-applied-configuration']) #re.search("kind", str(item))
                        kind=kind_array['kind']
                        restart_deployment(deployment, deployment_name, namespace)
                
            #     with open(file_path, "w") as file:
            #         file.write(str(item))
            #     file.close()
            # grep_command = f"grep -i '{configmap}' {file_path}"
            # try:
            #     grep_output = subprocess.check_output(grep_command, shell=True, text=True)
            #     print("Deployment Name is:", item.metadata.name)
            # except subprocess.CalledProcessError as e:
            #     if e.returncode == 1:
            #         print("String not found in the file.")
            #     else:
            #         print(f"Error running grep: {e}")

            except HTTPException as e:
                print(f"Exception caught outside the function: {e}")