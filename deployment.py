from kubernetes import client
from kubernetes import client, config
apis_api = client.AppsV1Api()
config.load_kube_config()
v1 = client.CoreV1Api()
#resp = apis_api.list_namespaced_deployment(namespace="velero")
resp = v1.read_namespaced_deployment(namespace="velero")
for i in resp.items:
    print(i)
