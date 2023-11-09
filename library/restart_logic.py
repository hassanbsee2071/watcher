from kubernetes import client, config, watch
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from kubernetes.client.rest import ApiException
from library.redis import RedisConnector
from library.restart_resources import RestartResources
import re
from dotenv import load_dotenv
import os
load_dotenv()



LOCAL_CONFIG = os.getenv("LOCAL_CONFIG")

if LOCAL_CONFIG == "True":
    config.load_kube_config()
elif LOCAL_CONFIG == "False":
    config.load_incluster_config()

v1 = client.CoreV1Api()
k8s_resources = client.AppsV1Api()
cusotom_resource = client.CustomObjectsApi()
ANNOTATION = os.getenv('ANNOTATION')

v1 = client.CoreV1Api()
k8s_resources = client.AppsV1Api()
cusotom_resource = client.CustomObjectsApi()

redis_connector = RedisConnector()
restart_resources = RestartResources()


class RestartLogic():
    def deployment_logic(self, all_deployments, resource, namespace):
        global DEPLOYMENT_FLAG
        count = 0
        total_item = 0
        for item in all_deployments.items:
            total_item = total_item + 1
            try: 
                require_restart = item.metadata.annotations.get(ANNOTATION)
                
                if require_restart != "false":
                    if re.search(resource, str(item)):
                        print("Deployment Name is:", item.metadata.name)
                        
                        DEPLOYMENT_FLAG = "True"
                        deployment=item.metadata.name
                        restart_resources.restart_deployment(k8s_resources, deployment, namespace,resource)
                    elif not re.search(resource, str(item)):
                    
                        count = count + 1
                if require_restart == "false":
                    DEPLOYMENT_FLAG = "IGNORED"
                    print("RESOURCE: %s, NAME: %s, NAMESPACE: %s, REQUIRE_RESTART: %s" % ("DEPLOYMENT", item.metadata.name, namespace, "FALSE"))
                    print("RESOURCE: %s, NAME: %s, NAMESPACE: %s, STATUS: %s" % ("DEPLOYMENT", item.metadata.name, namespace, "IGNORED"))
                    
            except Exception as e:
                print(f"Exception occurred: {e}")
                print("Could Not Find Annotations......")
        if count == total_item:
            print (f"Resource {resource} Does Not Exist In Any Deployment In {namespace} Namespace")

            DEPLOYMENT_FLAG = "False"

    def statefulset_logic(self, all_statefulset, resource, namespace):
        global STATEFULSET_FLAG
        count = 0
        total_item = 0
        for item in all_statefulset.items:
            total_item = total_item + 1
            try: 
                require_restart = item.metadata.annotations.get(ANNOTATION)
                if require_restart != "false":
                    if re.search(resource, str(item)):
            
                        STATEFULSET_FLAG = "True"
                        print("StatefulSet Name is:", item.metadata.name)
                        stateful = item.metadata.name
                        restart_resources.restart_statefulset(k8s_resources, stateful, namespace,resource)
                    elif not re.search(resource, str(item)):
        
                        count = count + 1
                if require_restart == "false":
                    STATEFULSET_FLAG = "IGNORED"
                    print("RESOURCE: %s, NAME: %s, NAMESPACE: %s, REQUIRE_RESTART: %s" % ("STATEFULSET", item.metadata.name, namespace, "FALSE"))
                    print("RESOURCE: %s, NAME: %s, NAMESPACE: %s, STATUS: %s" % ("STATEFULSET", item.metadata.name, namespace, "IGNORED"))
            except Exception as e:
                print(f"Exception occurred: {e}")
                print("Could Not Find Annotaions......")
        if count == total_item:
            print (f"Resource {resource} Does Not Exist In Any StateFulset In {namespace} Namespace")

            STATEFULSET_FLAG = "False"
    
    def daemonset_logic(self, all_daemonset, resource, namespace):
        global DAEMONSET_FLAG
        count = 0
        total_item = 0
        for item in all_daemonset.items:
            total_item = total_item + 1
            try: 
                require_restart = item.metadata.annotations.get(ANNOTATION)
                if require_restart != "false":

                    if re.search(resource, str(item)):
                   
                        DAEMONSET_FLAG = "True"
                        print("DaemonSet Name is:", item.metadata.name)
                        daemonset = item.metadata.name
                        restart_resources.restart_daemonset(k8s_resources, daemonset, namespace,resource)
                    elif not re.search(resource, str(item)):
                    
                        count = count + 1
                if require_restart == "false":
                    DAEMONSET_FLAG = "IGNORED"
                    print("RESOURCE: %s, NAME: %s, NAMESPACE: %s, REQUIRE_RESTART: %s" % ("DAEMONSET", item.metadata.name, namespace, "FALSE"))
                    print("RESOURCE: %s, NAME: %s, NAMESPACE: %s, STATUS: %s" % ("DAEMONSET", item.metadata.name, namespace, "IGNORED"))
            except Exception as e:
                print(f"Exception occurred: {e}")
                print("Could Not Find Annotaions......")
        if count == total_item:
            print (f"Resource {resource} Does Not Exist In Any DaemonSet In {namespace} Namespace")
            DAEMONSET_FLAG = "False"

    def resource_unlocking(self,resource):
       
            if DEPLOYMENT_FLAG == "False" and STATEFULSET_FLAG == "False" and DAEMONSET_FLAG == "False":
              print("DEPLOYMENT_FLAG: %s, STATEFULSET_FLAG: %s, DAEMONSET_FLAG: %s" % (DEPLOYMENT_FLAG, STATEFULSET_FLAG, DAEMONSET_FLAG))
              redis_connector.unlock_resource(resource)
            
            elif DEPLOYMENT_FLAG == "True" or STATEFULSET_FLAG == "True" or DAEMONSET_FLAG == "True":
               print("DEPLOYMENT_FLAG: %s, STATEFULSET_FLAG: %s, DAEMONSET_FLAG: %s" % (DEPLOYMENT_FLAG, STATEFULSET_FLAG, DAEMONSET_FLAG))
            
            elif DEPLOYMENT_FLAG == "IGNORED" or STATEFULSET_FLAG == "IGNORED" or DAEMONSET_FLAG == "IGNORED":
               print("DEPLOYMENT_FLAG: %s, STATEFULSET_FLAG: %s, DAEMONSET_FLAG: %s" % (DEPLOYMENT_FLAG, STATEFULSET_FLAG, DAEMONSET_FLAG))
                        
            else:
                print ("Something Went Wrong")
                