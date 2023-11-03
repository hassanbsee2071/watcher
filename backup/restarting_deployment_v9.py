#some sts like dev-zookeeper in devops cannot rollout restart both via kubectl command or python ####
# this removes append loop
# added annotation and redis connection function
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


#tajawal-dev-cms-core.hnk4p0.ng.0001.euw1.cache.amazonaws.com 6379
config.load_kube_config()
# REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_HOST = "tajawal-dev-cms-core.hnk4p0.ng.0001.euw1.cache.amazonaws.com"
REDIS_PORT = 6379
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_timeout=1)
LOCK_EXPIRATION_TIME = 300  # 5 minutes
deployment_name=[]
stateful_name=[]
daemonset_name=[]
v1 = client.CoreV1Api()
k8s_resources = client.AppsV1Api()
cusotom_resource = client.CustomObjectsApi()
ignore_namespace = ['ingress-aws-lb-controller', 'istio-system', 'karpenter', 'kube-system', 'kubesphere-system']
ignore_namespace_secret = ['ingress-aws-lb-controller', 'istio-system', 'karpenter', 'kube-system', 'kubesphere-system']
ignore_namespace_sealed_secret = ['ingress-aws-lb-controller', 'istio-system', 'karpenter', 'kube-system', 'kubesphere-system']

def redis_connectivity():
    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_timeout=1)
        connection=redis_client.ping()
        print(f"Connection to redis {REDIS_HOST} {REDIS_PORT} successfully established.")

    except Exception as e:
        print(f"Exception occurred. Cannot connect to redis host {REDIS_HOST} {REDIS_PORT}: {e}")
        exit(1)


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


def notify_message(sealed_secret, namespace):
    print ("Sealed Secret:", sealed_secret, "has been modified in namespace:", namespace)
    print ("Now watching for the relevant secret to be updated. Then rollout restart will take place....")
    unlock_resource(sealed_secret)

def restart_statefulset(v1_apps, stateful, namespace, resource):
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

    try:
        print ("Rolling out Restart StatefulSet:", stateful)
        v1_apps.patch_namespaced_stateful_set(stateful, namespace, body, pretty='true')
        unlock_resource(resource)
    except ApiException as e:
        print("Exception when calling AppsV1Api->read_namespaced_stateful_set_status: %s\n" % e)



def restart_daemonset(v1_apps, daemonset, namespace,resource):
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

    try:
        print ("Rolling out Restart Daemonset:", daemonset)
        v1_apps.patch_namespaced_daemon_set(daemonset, namespace, body, pretty='true')
        unlock_resource(resource)
    except ApiException as e:
        print("Exception when calling AppsV1Api->read_namespaced_daemon_set_status: %s\n" % e)

def restart_deployment(v1_apps, deployment, namespace,resource):
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
    try:
        print ("Rolling out Restart Deployment:", deployment)
        v1_apps.patch_namespaced_deployment(deployment, namespace, body, pretty='true')
        unlock_resource(resource)
    except ApiException as e:
        print("Exception when calling AppsV1Api->read_namespaced_deployment_status: %s\n" % e)


def watch_configmap():
 try:
    w = watch.Watch()
    print ("Started Listening For Configmaps....")
    
    for event in w.stream(v1.list_config_map_for_all_namespaces):
        if event["type"] == "MODIFIED":
            if event['object'].metadata.namespace in ignore_namespace:
                print("RESOURCE: %s, EVENT: %s, NAME: %s, NAMESPACE: %s, STATUS: %s" % ("CONFIGMAP", event['type'], event['object'].metadata.name, event['object'].metadata.namespace, "IGNORED"))
                # time.sleep(2)
                # raise Exception("Oh oh, this script just died")
            if event['object'].metadata.namespace not in ignore_namespace:
                print("RESOURCE: %s, EVENT: %s, NAME: %s, NAMESPACE: %s, STATUS: %s" % ("CONFIGMAP", event['type'], event['object'].metadata.name, event['object'].metadata.namespace, "PROCESSING"))
                namespace = event['object'].metadata.namespace
                configmap = event['object'].metadata.name
                kind = event['object'].kind
                try:
                    lock_resource(configmap)
                    deployments = k8s_resources.list_namespaced_deployment(namespace=namespace)
                    statefulset = k8s_resources.list_namespaced_stateful_set(namespace=namespace)
                    daemonset   = k8s_resources.list_namespaced_daemon_set(namespace=namespace)

                    for item in deployments.items:
                        try: 
                            require_restart = item.metadata.annotations.get("require-restart")
                            print ("Require Restart:",require_restart )
                            if require_restart != "false":
                                if re.search(configmap, str(item)):
                                    print("Deployment Name is:", item.metadata.name)
                                    deployment=item.metadata.name
                                    #print ("Deployment Append:", deployment)
                                    restart_deployment(k8s_resources, deployment, namespace,configmap)
                            if require_restart == "false":
                                print("RESOURCE: %s, NAME: %s, NAMESPACE: %s, STATUS: %s" % ("DEPLOYMENT", item.metadata.name, namespace, "IGNORED"))
                        except Exception as e:
                            print(f"Exception occurred: {e}")
                            print("Could Not Find Annotaions......")
                    for item in statefulset.items:
                        if re.search(configmap, str(item)):
                            print("StatefulSet Name is:", item.metadata.name)
                            stateful = item.metadata.name
                            restart_statefulset(k8s_resources, stateful, namespace,configmap)

                    for item in daemonset.items:
                        if re.search(configmap, str(item)):
                            print("DaemonSet Name is:", item.metadata.name)
                            daemonset = item.metadata.name
                            restart_daemonset(k8s_resources, daemonset, namespace,configmap)

                except HTTPException as e:
                    print(f"Exception caught outside the function: {e}")

 except Exception as e:
    print(f"Exception occurred: {e}")
    # Optionally, you can add a delay before restarting
    time.sleep(1)  # Adjust the delay as needed
    # Restart the program by calling it again
    os.execv(sys.executable, ['python3'] + sys.argv)


def watch_secrets():
 try:
    print ("Started Listening For Secrets....")
    w = watch.Watch()
    
    for event in w.stream(v1.list_secret_for_all_namespaces):
        if event["type"] == "MODIFIED":
            if event['object'].metadata.namespace in ignore_namespace_secret:
                print("RESOURCE: %s, EVENT: %s, NAME: %s, NAMESPACE: %s, STATUS: %s" % ("SECRET", event['type'], event['object'].metadata.name, event['object'].metadata.namespace, "IGNORED"))
            if event['object'].metadata.namespace not in ignore_namespace_secret:
                print("RESOURCE: %s, EVENT: %s, NAME: %s, NAMESPACE: %s, STATUS: %s" % ("SECRET", event['type'], event['object'].metadata.name, event['object'].metadata.namespace, "PROCESSING"))
                namespace = event['object'].metadata.namespace
                secret = event['object'].metadata.name
                kind = event['object'].kind
                try:
                    lock_resource(secret)
                    deployments = k8s_resources.list_namespaced_deployment(namespace=namespace)
                    statefulset = k8s_resources.list_namespaced_stateful_set(namespace=namespace)
                    daemonset   = k8s_resources.list_namespaced_daemon_set(namespace=namespace)

                    for item in deployments.items:
                        if re.search(secret, str(item)):
                            print("Deployment Name is:", item.metadata.name)
                            deployment=item.metadata.name
                            #print ("Deployment Append:", deployment)
                            restart_deployment(k8s_resources, deployment, namespace,secret)

                    for item in statefulset.items:
                        if re.search(secret, str(item)):
                            print("StatefulSet Name is:", item.metadata.name)
                            stateful = item.metadata.name
                            restart_statefulset(k8s_resources, stateful, namespace,secret)

                    for item in daemonset.items:
                        if re.search(secret, str(item)):
                            print("DaemonSet Name is:", item.metadata.name)
                            daemonset = item.metadata.name

                            restart_daemonset(k8s_resources, daemonset, namespace,secret)


                except HTTPException as e:
                    print(f"Exception caught outside the function: {e}")

 except Exception as e:
    print(f"Exception occurred: {e}")
    # Optionally, you can add a delay before restarting
    time.sleep(1)  # Adjust the delay as needed
    # Restart the program by calling it again
    os.execv(sys.executable, ['python3'] + sys.argv)

def watch_sealed_secrets():
 try:
    print ("Started Listening For Sealed Secrets....")
    w = watch.Watch()
    
    for event in w.stream(cusotom_resource.list_cluster_custom_object, group="bitnami.com",version="v1alpha1",plural="sealedsecrets"):
        if event["type"] == "MODIFIED":
            if event['object']['metadata']['namespace'] in ignore_namespace_sealed_secret:
                print("RESOURCE: %s, EVENT: %s, NAME: %s, NAMESPACE: %s, STATUS: %s" % ("SEALEDSECRET", event['type'], event['object']['metadata']['name'], event['object']['metadata']['namespace'], "IGNORED"))
            if event['object']['metadata']['namespace'] not in ignore_namespace_sealed_secret:
                print("RESOURCE: %s, EVENT: %s, NAME: %s, NAMESPACE: %s, STATUS: %s" % ("SEALEDSECRET", event['type'], event['object']['metadata']['name'], event['object']['metadata']['namespace'], "PROCESSING"))
                namespace = event['object']['metadata']['namespace']
                sealed_secret = event['object']['metadata']['name']
                try:
                    lock_resource(sealed_secret)
                    notify_message(sealed_secret, namespace)
                except HTTPException as e:
                    print(f"Exception caught outside the function: {e}")
 except Exception as e:
    print(f"Exception occurred: {e}")
    # Optionally, you can add a delay before restarting
    time.sleep(1)  # Adjust the delay as needed
    # Restart the program by calling it again
    os.execv(sys.executable, ['python3'] + sys.argv)




redis_connectivity()

config_map_thread = threading.Thread(target=watch_configmap)
config_map_thread.start()


secrets_thread = threading.Thread(target=watch_secrets)
secrets_thread.start()

sealed_secrets_thread = threading.Thread(target=watch_sealed_secrets)
sealed_secrets_thread.start()