from kubernetes import client, config, watch
import re
import json
import os
import subprocess
config.load_kube_config()
v1 = client.CoreV1Api()
deployment = client.AppsV1Api()
namespace = "velero"
deployments = deployment.list_namespaced_deployment(namespace=namespace)
print (deployments)
for item in deployments.items:
 print(item.metadata.name)
