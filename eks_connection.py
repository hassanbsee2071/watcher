import eks_token
import boto3
import tempfile
import base64
import kubernetes



def k8s_api_client(endpoint: str, token: str, cafile: str) -> kubernetes.client.CoreV1Api:
    kconfig = kubernetes.config.kube_config.Configuration(
        host=endpoint,
        api_key={'authorization': 'Bearer ' + token}
    )
    kconfig.ssl_ca_cert = cafile
    kclient = kubernetes.client.ApiClient(configuration=kconfig)
    return kubernetes.client.CoreV1Api(api_client=kclient)


def _write_cafile(data: str) -> tempfile.NamedTemporaryFile:
    # protect yourself from automatic deletion
    cafile = tempfile.NamedTemporaryFile(delete=False)
    cadata_b64 = data
    cadata = base64.b64decode(cadata_b64)
    cafile.write(cadata)
    cafile.flush()
    return cafile


cluster_name = 'tajawal-dev'
my_token = eks_token.get_token(cluster_name)

bclient = boto3.client('eks', region_name='eu-west-1')
cluster_data = bclient.describe_cluster(name=cluster_name)['cluster']
my_cafile = _write_cafile(cluster_data['certificateAuthority']['data'])


api_client = k8s_api_client(
    endpoint=cluster_data['endpoint'],
    token=my_token['status']['token'],
    cafile=my_cafile.name
)
api_client.list_namespace()




#####################################

import kubernetes.client
from kubernetes import config
import eks_token
# Assuming you have a function like eks_token.get_token that returns the token
cluster_name = 'tajawal-dev'
my_token = eks_token.get_token(cluster_name)
print(my_token)

# Assuming you have the Kubernetes API token
ApiToken = "k8s-aws-v1.aHR0cHM6Ly9zdHMuYW1hem9uYXdzLmNvbS8_QWN0aW9uPUdldENhbGxlcklkZW50aXR5JlZlcnNpb249MjAxMS0wNi0xNSZYLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFTSUEzVEVZVURFWjVMNUJTSDQzJTJGMjAyMzEwMzElMkZ1cy1lYXN0LTElMkZzdHMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDIzMTAzMVQwOTE0MzdaJlgtQW16LUV4cGlyZXM9NjAmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JTNCeC1rOHMtYXdzLWlkJlgtQW16LVNlY3VyaXR5LVRva2VuPUlRb0piM0pwWjJsdVgyVmpFTUglMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkZ3RWFDV1YxTFhkbGMzUXRNU0pITUVVQ0lRQzQlMkIxMWt6R2MlMkJEZHhpdFJBJTJCbHU4T21JYWt5QzdjNTVLaTd5TUdvb0tYY2dJZ1o3ZDc1UVZNbiUyQlpmeDlNUTFXVmV3TTRPVFYlMkZSUkklMkJ0JTJGczZKem9aTVBQZ3F4Z1VJNnYlMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkYlMkZBUkFFR2d3M09UY3dNelkxTVRjMk9ETWlESyUyQk1xU1VCQ054cXg2RSUyQkpDcWFCZm5zZEJLN1dOREVsTUptME5GcHVZV1JCQUVyOUdHTUNSTk1GRGNybEtQSkdPOW1FNHolMkZDbFI4QTgzSjZxVzFLcFAxRTNSWDNaNkRKMW03WHdiQjdtYU5FUU5nMXR2anFHNk8lMkZHUk13MDdMZnBLVkI4NEZFVkxNVCUyQnowdUFVdVVCakF6cVhOZmo3eDVsd2oxMzkyM1RQakVMT1lDTEZ1c3ZONnJCV0hHYk8lMkZYcFJUU0ltYjBVam8yUjdyamVMWGlucHZsdWQxOVhPVWZybmEweEVUeHhoNzVLUkFjTGhHN3M1RDJVNXQxaiUyRmR6TXQwNyUyQnNwc2ljZ2tTbVFxaDFMOTgzaDZpdjJhV0lGc0hzYzJvQmRFUERyNzNPbTZkS0JFaTRZTkRzMHhWS0RCQSUyRnVvbFpjTUc3WG9lS2glMkJVejlpWWJmNGx4YnlJNmdKTnVFWiUyRk5iMnBETSUyRnNWdE4wTkh6QjBkM2NFa2NqU2dremo2bzYzUVdJRUl4dmwlMkYyMWI0JTJCWEx1aDRIelp6b2tNNURGU3o1NUFUcUdNNSUyRnpwanJvTnRZVGZDZ2Nxb20yeU5qTDUzaDZVb1pNY2xqRmZQYlpxR1lFRlYlMkJOSXBPViUyRmhGb1hkeEdrQWV5UWUyN1gwMVllTDJuV2RSQ0FiSVhFQ0I0U0dXaHNDbWx2VnZKSlNVWmJHVjI5ZVlKRSUyQmM4TmVCazhxYjBvMGtNVndrejl2dSUyRllaeTRTOU5UTmtycXRWa1ZvNGpqMTVjcEZLS1ljUnplQnNWRUxINFI2JTJCcnlMSUZ2cWRza2Nxd0kzRVN5T0cyazBvJTJCQm1LUjNDYm5UMWlEaUkyUWtwU25UWWllY3ZINkZUb0QyRTVXM0lSWUtuJTJCUGFvVjVZOFhvSUlxb0gxemkwZWFoVTNmRHN5WlhWNFRCVXZ2bktQVkJpZnFWaDBGU0RRQnFOcGVXT0tqVnRXb0xlOWxxY2EyeWwxVkxoQ0glMkY5VjAwOU5NZVAlMkZISGZGZDR4eXg1N0dGUlBBWklQbXZuZCUyQmNPOHhFdDFhYm9qJTJGV01paXNabldtTUZ0d2cxQUZ5bldPWlBmTlF2dmNXY0pFSjlSS0lSWjVCZHBuOURjOEdzOWVxZ014dk9JYjlWQm5aQUhQcCUyRlJkckg3SGZneTNLckV2NGx2NjdvVXZQNUZSeDlYMXA1RW0lMkZicmpET2hJT3FCanF4QVhPM052WGVvUTY0SHo4QVZnaUYlMkJkVUpXRkFTWm5scVg5ZFI5UG5WTnhuVWhDUlhOWWE2d01OR1lTVEFKczZxWjBPZjBNbmdXbVdMRVRwRmlRVzIwdU0lMkY0bE50cWNJUmlNM2JDOENBdUpHTUxrT2hIeHV6c0lTaXpHZVllbFhKenJQJTJGMTBSYVlOaFhRU29KcVNnNDVscHFXYnBKMnA3cFQ5SzElMkJ6SFFSR3MlMkI0Z2xTSEZpZ2NSWjFmOEVLcUY2MVF6dFg5VDJ1YzFNNFVyV1ZOUlVNc3Y1ZVh6U3ZBc2N1a2Fkb1BTT1ZvSTZpVUElM0QlM0QmWC1BbXotU2lnbmF0dXJlPWQ5ZWQ2ZjRmYWYzNDhhNjY2M2UxNDM5ZDc1MmViYjRkNzE4YmMxMTEyNjk5MjBhM2FkMWMxYzkzMTVjOTUzZTY"

# Set up the Kubernetes client configuration
configuration = kubernetes.client.Configuration()
configuration.host = 'https://A9EFEE8D4D43C721B85F1E7F588D1763.yl4.eu-west-1.eks.amazonaws.com'
configuration.verify_ssl = False
configuration.debug = True
configuration.api_key = {"authorization": "Bearer " + ApiToken}
kubernetes.client.Configuration.set_default(configuration)

# Load the in-cluster configuration (assuming you're running inside a pod)
config.load_incluster_config()

# Create the CoreV1Api client
v1 = kubernetes.client.CoreV1Api()

# Now, call the method to list namespaces and print the result
ret = v1.list_namespace()
print(ret)

#####################
def main():
    config.load_incluster_config()

    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print(f"{i.status.pod_ip}\t{i.metadata.namespace}\t{i.metadata.name}")


if __name__ == '__main__':
    main()



###############################

from kubernetes import client, config, watch
# Configs can be set in Configuration class directly or using helper utility
#config.load_kube_config()
config.load_incluster_config()
v1 = client.CoreV1Api()
count = 10
w = watch.Watch()
k8s_resources = client.AppsV1Api()
import re
#for event in w.stream(v1.list_config_map_for_all_namespaces, _request_timeout=60):
ignore_namespace = ['ingress-aws-lb-controller', 'istio-system', 'karpenter', 'kube-system', 'kubesphere-system']
for event in w.stream(v1.list_config_map_for_all_namespaces):
 if event["type"] == "MODIFIED":
    if event['object'].metadata.namespace not in ignore_namespace:

     print("Event: %s %s %s" % (event['type'], event['object'].metadata.name, event['object'].metadata.namespace))
     namespace = event['object'].metadata.namespace
     configmap = event['object'].metadata.name
     deployments = k8s_resources.list_namespaced_deployment(namespace=namespace)
     for item in deployments.items:
         require_restart = item.metadata.annotations.get("require-restart")
         print ("Require Restart is:", require_restart)
         print("Annotations Are:", item.metadata.annotations)

