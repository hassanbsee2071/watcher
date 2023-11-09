from kubernetes import client, config, watch
import re
import json
import os
import subprocess
import redis
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from kubernetes.client.rest import ApiException
import json
import datetime
import threading
import time
import sys
from library.redis import RedisConnector

redis_connector = RedisConnector()

class RestartResources:
    def notify_message(self, sealed_secret, namespace):
        print ("Sealed Secret:", sealed_secret, "has been modified in namespace:", namespace)
        print ("Now watching for the relevant secret to be updated. Then rollout restart will take place....")
        redis_connector.unlock_resource(sealed_secret)

    def restart_statefulset(self, v1_apps, stateful, namespace, resource):
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
            print ("Rolling out Restart StatefulSet:", stateful)
            v1_apps.patch_namespaced_stateful_set(stateful, namespace, body, pretty='true')
            redis_connector.unlock_resource(resource)
        except ApiException as e:
            print("Exception when calling AppsV1Api->read_namespaced_stateful_set_status: %s\n" % e)



    def restart_daemonset(self, v1_apps, daemonset, namespace,resource):
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
            print ("Rolling out Restart Daemonset:", daemonset)
            v1_apps.patch_namespaced_daemon_set(daemonset, namespace, body, pretty='true')
            #unlock_resource(resource)
            redis_connector.unlock_resource(resource)
        except ApiException as e:
            print("Exception when calling AppsV1Api->read_namespaced_daemon_set_status: %s\n" % e)

    def restart_deployment(self, v1_apps, deployment, namespace,resource):
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
            print ("Rolling out Restart Deployment:", deployment)
            v1_apps.patch_namespaced_deployment(deployment, namespace, body, pretty='true')
            redis_connector.unlock_resource(resource)
        except ApiException as e:
            print("Exception when calling AppsV1Api->read_namespaced_deployment_status: %s\n" % e)
