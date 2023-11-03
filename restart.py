from kubernetes import client, config
from kubernetes.client.rest import ApiException
import datetime

def restart_deployment(v1_apps, deployment, namespace):
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
        v1_apps.patch_namespaced_deployment(deployment, namespace, body, pretty='true')
    except ApiException as e:
        print("Exception when calling AppsV1Api->read_namespaced_deployment_status: %s\n" % e)


def main():
    config.load_kube_config()
    # Enter name of deployment and "namespace"
    deployment = "zipkin"
    namespace = "devops"
    v1_apps = client.AppsV1Api()
    restart_deployment(v1_apps, deployment, namespace)


if __name__ == '__main__':
    main()
