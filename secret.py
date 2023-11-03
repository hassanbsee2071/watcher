
from kubernetes import client, config, watch
config.load_kube_config()
v1 = client.CoreV1Api()
count = 10
w = watch.Watch()
for event in w.stream(v1.list_secret_for_all_namespaces, _request_timeout=60):
    print("Event: %s %s" % (event['type'], event['object'].metadata.name))
    #count -= 1
    #if not count:
    #  w.stop()
#print("Ended.")
