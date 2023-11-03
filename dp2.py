# get deployment by namespace
from kubernetes import client,config
import re
import json

import os
import subprocess

config.load_kube_config()
namespace="hotels"
apis_api = client.AppsV1Api()
resp = apis_api.list_namespaced_deployment(namespace=namespace)

file_path = "output_file.txt"
search_string = "BAVEL_CERT_PASSWORD_PRO"
#with open(file_path, "w") as file:


for i in resp.items:
    print("Hello")
    with open(file_path, "w") as file:
       file.write(str(i))
    file.close()
    grep_command = f"grep -i '{search_string}' {file_path}"
    try:
        grep_output = subprocess.check_output(grep_command, shell=True, text=True)
        #print(grep_output)
        print(i.metadata.name)
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            print("String not found in the file.")
        else:
            print(f"Error running grep: {e}")


    #grep_command = f"grep -i '{search_string}' {file_path}"
    #grep_output = subprocess.check_output(grep_command, shell=True, text=True)
    #print(grep_output)



    #containers = i.spec.template.spec.containers
    #for dic in containers:
    #    print(dic.env)
    #    envs = dic.env
    #    for e in envs:
    #       print(e.value_from)
