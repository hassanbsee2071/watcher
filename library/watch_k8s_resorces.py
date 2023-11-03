from kubernetes import client, config, watch
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from kubernetes.client.rest import ApiException
import time
import sys
from library.redis import RedisConnector
from library.restart_resources import RestartResources
from library.restart_logic import RestartLogic
from dotenv import load_dotenv
import os
load_dotenv()

config.load_kube_config()
v1 = client.CoreV1Api()
k8s_resources = client.AppsV1Api()
cusotom_resource = client.CustomObjectsApi()


ignore_configmap_namespace = os.getenv('IGNORE_CONFIGMAP_NAMESPACES')
IGNORE_CONFIGMAP_NAMESPACES = ignore_configmap_namespace.split(",")
ignore_secret_namespace = os.getenv('IGNORE_SECRET_NAMESPACES')
IGNORE_SECRET_NAMESPACES = ignore_secret_namespace.split(",")
PRINT_TIME = int(os.getenv('PRINT_TIME'))

redis_connector = RedisConnector()
restart_resources = RestartResources()
restart_logic = RestartLogic()

class WatchResources:
    def watch_configmap(self):
        try:
            w = watch.Watch()
            print ("Started Listening For Configmaps....")
            
            for event in w.stream(v1.list_config_map_for_all_namespaces):
                if event["type"] == "MODIFIED":
                    if event['object'].metadata.namespace in IGNORE_CONFIGMAP_NAMESPACES:
                        #print("RESOURCE: %s, EVENT: %s, NAME: %s, NAMESPACE: %s, STATUS: %s" % ("CONFIGMAP", event['type'], event['object'].metadata.name, event['object'].metadata.namespace, "IGNORED"))
                        pass
                        # time.sleep(2)
                        # raise Exception("Oh oh, this script just died")
                    if event['object'].metadata.namespace not in IGNORE_CONFIGMAP_NAMESPACES:
                        print("RESOURCE: %s, EVENT: %s, NAME: %s, NAMESPACE: %s, STATUS: %s" % ("CONFIGMAP", event['type'], event['object'].metadata.name, event['object'].metadata.namespace, "PROCESSING"))
                        namespace = event['object'].metadata.namespace
                        configmap = event['object'].metadata.name
                        kind = event['object'].kind
                        try:
                            redis_connector.lock_resource(configmap)
                            deployments = k8s_resources.list_namespaced_deployment(namespace=namespace)
                            statefulset = k8s_resources.list_namespaced_stateful_set(namespace=namespace)
                            daemonset   = k8s_resources.list_namespaced_daemon_set(namespace=namespace)
                            restart_logic.deployment_logic(deployments, configmap, namespace)
                            restart_logic.statefulset_logic(statefulset, configmap, namespace)
                            restart_logic.daemonset_logic(daemonset, configmap, namespace)
                            restart_logic.resource_unlocking(configmap)

                        except HTTPException as e:
                            print(f"Exception caught outside the function: {e}")

        except Exception as e:
            print(f"Exception occurred: {e}")
            time.sleep(1) 
            os.execv(sys.executable, ['python3'] + sys.argv)


    def watch_secrets(self):
        try:
            print ("Started Listening For Secrets....")
            w = watch.Watch()
            
            for event in w.stream(v1.list_secret_for_all_namespaces):
                if event["type"] == "MODIFIED":
                    if event['object'].metadata.namespace in IGNORE_SECRET_NAMESPACES:
                        #print("RESOURCE: %s, EVENT: %s, NAME: %s, NAMESPACE: %s, STATUS: %s" % ("SECRET", event['type'], event['object'].metadata.name, event['object'].metadata.namespace, "IGNORED"))
                        pass
                    if event['object'].metadata.namespace not in IGNORE_SECRET_NAMESPACES:
                        print("RESOURCE: %s, EVENT: %s, NAME: %s, NAMESPACE: %s, STATUS: %s" % ("SECRET", event['type'], event['object'].metadata.name, event['object'].metadata.namespace, "PROCESSING"))
                        namespace = event['object'].metadata.namespace
                        secret = event['object'].metadata.name
                        kind = event['object'].kind
                        try:
                            redis_connector.lock_resource(secret)
                            deployments = k8s_resources.list_namespaced_deployment(namespace=namespace)
                            statefulset = k8s_resources.list_namespaced_stateful_set(namespace=namespace)
                            daemonset   = k8s_resources.list_namespaced_daemon_set(namespace=namespace)
                            restart_logic.deployment_logic(deployments, secret, namespace)
                            restart_logic.statefulset_logic(statefulset, secret, namespace)
                            restart_logic.daemonset_logic(daemonset, secret, namespace)
                            restart_logic.resource_unlocking(secret)

                        except HTTPException as e:
                            print(f"Exception caught outside the function: {e}")

        except Exception as e:
            print(f"Exception occurred: {e}")
            time.sleep(1)
            os.execv(sys.executable, ['python3'] + sys.argv)


    def watch_sealed_secrets(self):
        try:
            print ("Started Listening For Sealed Secrets....")
            w = watch.Watch()
            
            for event in w.stream(cusotom_resource.list_cluster_custom_object, group="bitnami.com",version="v1alpha1",plural="sealedsecrets"):
                if event["type"] == "MODIFIED":
                    if event['object']['metadata']['namespace'] in IGNORE_SECRET_NAMESPACES:
                        print("RESOURCE: %s, EVENT: %s, NAME: %s, NAMESPACE: %s, STATUS: %s" % ("SEALEDSECRET", event['type'], event['object']['metadata']['name'], event['object']['metadata']['namespace'], "IGNORED"))
                    if event['object']['metadata']['namespace'] not in IGNORE_SECRET_NAMESPACES:
                        print("RESOURCE: %s, EVENT: %s, NAME: %s, NAMESPACE: %s, STATUS: %s" % ("SEALEDSECRET", event['type'], event['object']['metadata']['name'], event['object']['metadata']['namespace'], "PROCESSING"))
                        namespace = event['object']['metadata']['namespace']
                        sealed_secret = event['object']['metadata']['name']
                        try:
                            redis_connector.lock_resource(sealed_secret)
                            restart_resources.notify_message(sealed_secret, namespace)
                        except HTTPException as e:
                            print(f"Exception caught outside the function: {e}")
        except Exception as e:
            print(f"Exception occurred: {e}")
            time.sleep(1)
            os.execv(sys.executable, ['python3'] + sys.argv)



    def print_ignore_namespace(self):
        
        
        for namespace in IGNORE_CONFIGMAP_NAMESPACES:
            print("RESOURCE: %s, NAMESPACE: %s, STATUS: %s" % ("CONFIGMAP", namespace,"IGNORED"))
        for namespace in IGNORE_SECRET_NAMESPACES:
            print("RESOURCE: %s, NAMESPACE: %s, STATUS: %s" % ("SECRET", namespace,"IGNORED"))
        time.sleep(PRINT_TIME)