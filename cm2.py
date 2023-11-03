#from kubernetes import client, config
#from kubernetes.client.rest import ApiException
#from pprint import pprint

#config.load_kube_config()
#pretty = 'pretty_example' 
#api_instance = client.CoreV1Api()
##api_response = api_instance.list_namespaced_config_map(namespace="devops", pretty=pretty)
#api_response = api_instance.list_config_map_for_all_namespaces(watch=True)
#for i in api_response.items:
#  print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
##pprint(api_response)


from kubernetes import client, config, watch
# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()
v1 = client.CoreV1Api()
count = 10

w = watch.Watch()
k8s_resources = client.AppsV1Api()
import re

version = v1.list_config_map_for_all_namespaces().metadata.resource_version
#version = v1.list_config_map_for_all_namespaces()
print ("Version is:", version)
# #for event in w.stream(v1.list_config_map_for_all_namespaces, _request_timeout=60):
# ignore_namespace = ['ingress-aws-lb-controller', 'istio-system', 'karpenter', 'kube-system', 'kubesphere-system']
# for event in w.stream(v1.list_config_map_for_all_namespaces, allow_watch_bookmarks=True):
#  if event["type"] == "MODIFIED":
#     if event['object'].metadata.namespace not in ignore_namespace:
      
#      print("Event: %s %s %s" % (event['type'], event['object'].metadata.name, event['object'].metadata.namespace))
#      namespace = event['object'].metadata.namespace
#      configmap = event['object'].metadata.name
#      deployments = k8s_resources.list_namespaced_deployment(namespace=namespace)
#      for item in deployments.items:
#          require_restart = item.metadata.annotations.get("require-restart")
#          print ("Require Restart is:", require_restart)
#          #print(item.metadata.annotations["require-restart"])
#          print("Annotations Are:", item.metadata.annotations)
#          #if re.search(configmap, str(item)):
#             #print("Annotations Are:", item.metadata.annotations)
#             #require_restart = item.metadata.annotations.get("require-restart")
#             #print ("Require Restart is:", require_restart)


      #deployment = v1.read_namespaced_deployment(namespace="event['object'].metadata.namespace")
      #count -= 1
      #if not count:
      #  w.stop()
#print("Ended.")
