# watcher
At **Almosafer** we always try to automate things and to solve complex problems using a combination of open source, paid and custom built solutions.

We have encountered a situation where we need a controller that can watch all configmaps, secrets in a cluster and when they update then all the deployments, statefulsets and daemonsets consuming this configmap or secret automatically restart. 

This controller has the following features.

1. You can deploy multiple replicas of this controller as it is using distributed locking using redis. One event is processed by one replica. Events cannot be duplicated. 
1. You can pass namespace names as environment if you want to ignore  that namespace to be watched for configmap.
1. You can pass namespace names as environment if you want to ignore  that namespace to be watched for secrets.
1. You can annotate any deployment, statefulset or demonset if you do not want it to be restarted. 
1. This will give information about sealed secret updates in the cluster if you are using sealed secrets in your cluster.




Title: Automating Kubernetes Workloads: The Almosafer Controller


At **Almosafer**, our commitment to innovation drives us to explore and implement cutting-edge solutions to streamline operations. Our infrastructure is a sophisticated amalgamation of various tools, comprising a mix of open source, paid, and custom-built solutions. This diverse toolkit empowers us to meet the unique challenges of our industry while fostering adaptability and scalability.

In the realm of Kubernetes orchestration, we encountered a small challenge. To address this, we developed a custom controller, to watch and respond to changes in configmaps and secrets across a Kubernetes cluster.

In contrast to the existing solution that I found, my preference led me to develop the controller in Python. My approach is to design a controller that operates without the need for explicit annotations on deployments, statefulsets, or daemonsets to trigger restarts upon secret or configmap modifications. By default, the controller watches all configmaps and secrets across the entire cluster. For added flexibility, users can define exclusions by incorporating annotations as needed. 



**Key Features:**

**Automated Restart of Workloads:**

The primary objective of the Controller is to automatically restart deployments, statefulsets, and daemonsets whenever the associated configmaps or secrets are updated. This ensures that our applications seamlessly adapt to configuration changes, minimizing downtime and enhancing overall system reliability.

**Distributed Locking with Redis:**

The controller leverages distributed locking through Redis, allowing the deployment of multiple replicas. This design ensures that each event is processed by a single replica, preventing duplication of events. The use of Redis enhances scalability and resilience, making our solution suitable for dynamic and large-scale Kubernetes environments.

**Namespace Filtering:**

Flexibility is a key feature of the Almosafer Controller. Users can specify namespaces to be ignored for configmap and secret monitoring by passing them as environment variables. This fine-grained control enables organizations to tailor the controller's behavior to their specific requirements.

**Annotation-Based Exclusion:**

Not every workload needs to restart upon configmap or secret updates. The Controller introduces annotation support for deployments, statefulsets, and daemonsets. Users can annotate specific workloads to exempt them from automatic restarts, providing a nuanced approach to configuration management.

**Sealed Secrets Integration:**

We leverage a Jenkins job to facilitate the creation, updating, and deletion of sealed secrets. This, in turn, orchestrates the corresponding operations on the relevant secrets. The controller  captures the details of each modification made to sealed secrets.



![](Aspose.Words.8038039b-4ed1-405d-9551-1c8d5fa9a1d3.001.png)



|**Key** |**Description**|**Defaut**|
| :- | :- | :- |
|REDIS\_HOST|Redis Host|“redis-stack-0.redis-service.watcher.svc.cluster.local”|
|REDIS\_PORT|Redis port to connect|“6379”|
|REDIS\_SOCKET\_TIMEOUT|Specify connection timeout In seconds.|“5”|
|LOCK\_EXPIRATION\_TIME|How long the key will be locked in redis. This will prevent another replica from processing the event. Key will be unlocked after processing by the controller at the end.|“300”|
|DB|Database number of redis.|“0”|
|IGNORE\_CONFIGMAP\_NAMESPACES|Namespaces to ignored for configmaps.|"ingress-aws-lb-controller,istio-system,karpenter,kube-system,kubesphere-system"|
|IGNORE\_SECRET\_NAMESPACES|Namespaces to ignored for secrets.|"ingress-aws-lb-controller,istio-system,karpenter,kube-system,kubesphere-system"|
|ANNOTATION|Annotation that should apply to deployments, statefulset or daemonset to exclude from restart.|"require-restart"|
|PRINT\_TIME|Print time in seconds for the function that will print the namespace names that are ignored. |“100”|
|LOCAL\_CONFIG|In cluster config or local kubeconfig file|“False|
|USERNAME|Username to connect to redis|“”|
|PASSWORD|Password to connect to redis|“”|

