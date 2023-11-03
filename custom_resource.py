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
custom_resource = client.CustomObjectsApi()
#resource=v1.list_cluster_custom_object(group="SealedSecret", version="bitnami.com/v1alpha1")
#resource=client.CustomObjectsApi().list_namespaced_custom_object(group="bitnami.com", version="v1alpha1", plural="SealedSecrets", namespace="activity")
#resource=client.CustomObjectsApi().list_namespaced_custom_object(group="bitnami.com", version="v1alpha1", plural="SealedSecrets",namespace="activity")
#resource=client.CustomObjectsApi().list_namespaced_custom_object_for_all_namespaces(group="bitnami.com", version="v1alpha1", plural="SealedSecrets")
#resource=client.CustomObjectsApi().list_custom_object_for_all_namespaces(group="bitnami.com", version="v1alpha1", plural="SealedSecrets")

## working ####
#resource=client.CustomObjectsApi().list_namespaced_custom_object(group="bitnami.com",version="v1alpha1",plural="sealedsecrets", namespace="")
#resource = client.CustomObjectsApi().list_namespaced_custom_object(group="metrics.k8s.io",version="v1beta1", namespace="default", plural="pods")
w = watch.Watch()

## working ####
resource=client.CustomObjectsApi().list_cluster_custom_object(group="bitnami.com",version="v1alpha1",plural="sealedsecrets")

#for event in w.stream(client.CustomObjectsApi().list_cluster_custom_object(group="bitnami.com",version="v1alpha1",plural="sealedsecrets")):
# for event in w.stream(client.CustomObjectsApi().list_namespaced_custom_object(group="bitnami.com",version="v1alpha1",plural="sealedsecrets", namespace="")):

#   print("Event: %s %s %s" % (event['type'], event['object'].metadata.name, event['object'].metadata.namespace))
#  #print(resource)


#for event in w.stream(client.CustomObjectsApi().list_namespaced_custom_object,'bitnami.com','v1alpha1','""','sealedsecrets'):


## working ####
#for event in w.stream(client.CustomObjectsApi().list_namespaced_custom_object, group="bitnami.com",version="v1alpha1",plural="sealedsecrets", namespace=""):
#working ####
for event in w.stream(client.CustomObjectsApi().list_cluster_custom_object, group="bitnami.com",version="v1alpha1",plural="sealedsecrets"):
    
    #print("Event: %s %s %s" % (event['type'], event['object'].metadata.name, event['object'].metadata.namespace))
    print("Event: %s %s" % (event['type'], event['object']['metadata']['name']))
    #require_restart = item.metadata.annotations.get("require-restart")
    #print ("Require Restart is:", require_restart)
    print(event)
    print("Hello")
    main = event['object']
    #print("Event: %s %s" % (event['type'], event['object']['metadata']['annotations']['kubectl.kubernetes.io/last-applied-configuration']))
    try:
     print("Event: %s %s" % (event['type'], main.get('metadata').get('annotations').get('kubectl.kubernetes.io/last-applied-configuration')))
    except:
     print ("Annotations not Found")
    #print(dict.get('India').get('Batsman', 'Not Found')) 
    #print(d.get('sanie', 'Not found')) 