#some sts like dev-zookeeper in devops cannot rollout restart both via kubectl command or python ####
# this code is appending which means when ever a new deployment compes up old will also restrated## Deployment Append: ['activity-post-order-deployment', 'activity-cart-service-deployment']
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
stateful_name=[]
daemonset_name=[]
v1 = client.CoreV1Api()
k8s_resources = client.AppsV1Api()


def lock_resource(resource: str) -> None:

    key = f"resource:{resource}"
    acquired = redis_client.set(key, "locked", ex=LOCK_EXPIRATION_TIME, nx=True)
    if not acquired:
        raise HTTPException(status_code=409, detail="resource already locked")
    
def unlock_resource(resource: str) -> None:
    key = f"resource:{resource}"
    delete_lock = redis_client.delete(key)
    print ("Now Unlocking the Resource", resource)
    if not delete_lock:
        raise HTTPException(status_code=409, detail="Lock Not deleted")


def restart_statefulset(v1_apps, stateful_name, namespace, configmap):
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
    for stateful in stateful_name:
        try:
            print ("Rolling out Restart StatefulSet:", stateful)
            v1_apps.patch_namespaced_stateful_set(stateful, namespace, body, pretty='true')
            unlock_resource(configmap)
        except ApiException as e:
            print("Exception when calling AppsV1Api->read_namespaced_stateful_set_status: %s\n" % e)



def restart_daemonset(v1_apps, daemonset_name, namespace,configmap):
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
    for daemonset in daemonset_name:
        try:
            print ("Rolling out Restart Daemonset:", daemonset)
            v1_apps.patch_namespaced_daemon_set(daemonset, namespace, body, pretty='true')
            unlock_resource(configmap)
        except ApiException as e:
            print("Exception when calling AppsV1Api->read_namespaced_daemon_set_status: %s\n" % e)

def restart_deployment(v1_apps, deployment_name, namespace,configmap):
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
            unlock_resource(configmap)
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
            try:
                lock_resource(configmap)
                deployments = k8s_resources.list_namespaced_deployment(namespace=namespace)
                statefulset = k8s_resources.list_namespaced_stateful_set(namespace=namespace)
                daemonset   = k8s_resources.list_namespaced_daemon_set(namespace=namespace)

                for item in deployments.items:
                    if re.search(configmap, str(item)):
                        print("Deployment Name is:", item.metadata.name)
                        deployment_name.append(item.metadata.name)
                        # kind_array = json.loads(item.metadata.annotations['kubectl.kubernetes.io/last-applied-configuration']) #re.search("kind", str(item))
                        # kind=kind_array['kind']
                        print ("Deployment Append:", deployment_name)
                        restart_deployment(k8s_resources, deployment_name, namespace,configmap)
                        #unlock_resource(configmap)

                for item in statefulset.items:
                    if re.search(configmap, str(item)):
                        print("StatefulSet Name is:", item.metadata.name)
                        stateful_name.append(item.metadata.name)
                        # kind_array = json.loads(item.metadata.annotations['kubectl.kubernetes.io/last-applied-configuration']) #re.search("kind", str(item))
                        # kind=kind_array['kind']
                        restart_statefulset(k8s_resources, stateful_name, namespace,configmap)

                for item in daemonset.items:
                    if re.search(configmap, str(item)):
                        print("DaemonSet Name is:", item.metadata.name)
                        daemonset_name.append(item.metadata.name)
                        # kind_array = json.loads(item.metadata.annotations['kubectl.kubernetes.io/last-applied-configuration']) #re.search("kind", str(item))
                        # kind=kind_array['kind']
                        restart_daemonset(k8s_resources, daemonset_name, namespace,configmap)


            except HTTPException as e:
                print(f"Exception caught outside the function: {e}")