from kubernetes import client, config
from kubernetes.client.rest import ApiException
from pprint import pprint

config.load_kube_config()
pretty = 'pretty_example' 
api_instance = client.CoreV1Api()
#api_response = api_instance.list_namespaced_config_map(namespace="devops", pretty=pretty)
api_response = api_instance.list_config_map_for_all_namespaces(watch=True)
for i in api_response.items:
  print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
#pprint(api_response)
