from kubernetes import client, config

config.load_kube_config()
namespace="hotels"
apis_api = client.AppsV1Api()

resp = apis_api.list_namespaced_deployment(namespace=namespace)
search_string = "hotels-api-cli-configmap"
v1 = client.CoreV1Api()

for deployment in resp.items:
    deployment_name = deployment.metadata.name
    pods = v1.list_namespaced_pod(namespace)

    for pod in pods.items:
        for container in pod.spec.containers:
            for env_var in container.env:
                #print (env_var)
                if env_var.name == search_string:
                    print(f"Found in Deployment: {deployment_name}, Pod: {pod.metadata.name}, Container: {container.name}")

