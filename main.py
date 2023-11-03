from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
import threading
from library.redis import RedisConnector
from library.watch_k8s_resorces import WatchResources


cusotom_resource = client.CustomObjectsApi()


redis_connector = RedisConnector()
watch_respurces = WatchResources()


redis_connector.redis_connectivity()

config_map_thread = threading.Thread(target=watch_respurces.watch_configmap)
config_map_thread.start()


secrets_thread = threading.Thread(target=watch_respurces.watch_secrets)
secrets_thread.start()

try:
  sealed_existence = cusotom_resource.list_cluster_custom_object(group="bitnami.com",version="v1alpha1",plural="sealedsecrets")   
  sealed_secret_existence="True"
except ApiException as e:
    if e.status == 404:
     sealed_secret_existence="False"
        
print(sealed_secret_existence)

if sealed_secret_existence == "True":
    sealed_secrets_thread = threading.Thread(target=watch_respurces.watch_sealed_secrets)
    sealed_secrets_thread.start()
else:
   print ("Sealed Secret Does Not Exists")



print_ignored_namespace_thread = threading.Thread(target=watch_respurces.print_ignore_namespace)
print_ignored_namespace_thread.start()