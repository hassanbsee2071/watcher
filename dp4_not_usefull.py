from kubernetes import client, config
import subprocess

config.load_kube_config()
namespace = "hotels"
output_file = "kubectl_output.txt"

# Run kubectl to get the Deployments in the specified namespace and save the output to a file
kubectl_command = f"kubectl get deployment -n {namespace} -o json > {output_file}"
subprocess.run(kubectl_command, shell=True)

search_string = "BAVEL_CERT_PASSWORD_PRO"

# Use grep to search for the specified string within the saved file
grep_command = f"grep -i '{search_string}' {output_file}"
grep_output = subprocess.check_output(grep_command, shell=True, text=True)

# Print or process the grep output as needed
print(grep_output)

