from kubernetes import client,config,watch
import time

#config.load_kube_config(context='my-eks-context')
config.load_kube_config()
v1 = client.CoreV1Api()
watcher = watch.Watch()


namespace = 'kube-system'
last_resource_version=0
base_delay=1
retry = 4

def watch_secrets():
    namespace = 'kube-system'
    last_resource_version=0
    base_delay=1
    retry = 2
    try:
    # this watch will timeout in 5s to have a fast way to simulate a watch that need to be retried 
        for i in  watcher.stream(v1.list_namespaced_pod, namespace, resource_version=last_resource_version, timeout_seconds=5):
            print(i['object'].metadata.resource_version)
            last_resource_version = i['object'].metadata.resource_version


        # we retry the watch starting from the last resource version known
        # but this ALWAYS raises ApiException: (410) Reason: Expired: too old resource version: 379140622 (380367990) for me
        for i in  watcher.stream(v1.list_namespaced_pod, namespace, resource_version=last_resource_version, timeout_seconds=5):
            print('second loop', i['object'].metadata.resource_version)
            last_resource_version = i['object'].metadata.resource_version
    except client.exceptions.ApiException as e:
        if e.status == 410:
            print(f"Received 'Expired: too old resource version' error. Retrying (attempt {retry + 1})...")
            time.sleep(base_delay * 2**retry)
        else:
            raise


def watch():
    while True:
        try:
            watch_secrets()
        except Exception as e:
            print(f"An error occurred: {e}. Retrying...")
            time.sleep(1)

watch()