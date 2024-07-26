from kubernetes import client, config
from kubernetes.client.rest import ApiException

def create_pod(pod_name, image_name):
    
    config.load_kube_config()

    v1 = client.CoreV1Api()

    pod = client.V1Pod(
        metadata=client.V1ObjectMeta(name=pod_name),
        spec=client.V1PodSpec(
            containers=[client.V1Container(
                name=pod_name,
                image=image_name,
                resources=client.V1ResourceRequirements(
                    requests={"cpu": "100m", "memory": "200Mi"},
                    limits={"cpu": "500m", "memory": "500Mi"},
                ),
                command=['sleep','6000']
            )],
            restart_policy="Never",
        )
    )

    try:
       
        api_response = v1.create_namespaced_pod(namespace="default", body=pod)
        print("Pod created. status='%s'" % str(api_response.status.phase))
    except ApiException as e:
        print("Exception when calling CoreV1Api->create_namespaced_pod: %s\n" % e)

def delete_pod(pod_name):
    config.load_kube_config()

    v1 = client.CoreV1Api()

    try:
        api_response = v1.delete_namespaced_pod(name=pod_name, namespace="default", body=client.V1DeleteOptions())
        print("Pod deleted. status='%s'" % str(api_response.status))
    except ApiException as e:
        print("Exception deleting the pod %s\n" % e)

image_name = "ubuntu"
