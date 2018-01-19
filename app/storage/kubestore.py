from __future__ import print_function
import ast
import os

import kubernetes
from kubernetes import config, client
from kubernetes.client.rest import ApiException


class KubeState:


    def __init__(self):
        config.load_incluster_config()
        self.namespace = os.getenv('NAMESPACE', 'ott')
        self.cname = 'postgres-cluster-state'

    def get(self):
        api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient())
        try:
            api_response = api_instance.read_namespaced_config_map(
                self.cname,
                self.namespace,
                pretty='true',
                exact=True,
                export=True
            )
            return self.make_json(api_response.data)
        except ApiException as e:
            #print("Exception when calling CoreV1Api->read_namespaced_config_map: %s\n" % e)
            return False

    def make_json(self,response):
        for key, value in response.items():
            response[key] = ast.literal_eval(value)
        return response

    def make_string(self,request):
        for key, value in request.items():
            request[key] = str(value)
        return request

    def set(self,data):
        if self.get():
            return self.update_configmap(data)
        else:
            return self.create_configmap(data)

    def update_configmap(self,data):
        api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient())
        cmap = client.V1ConfigMap(metadata=client.V1ObjectMeta(name=self.cname), data=self.make_string(data))
        try:
            api_instance.patch_namespaced_config_map(self.cname, self.namespace, body=cmap, pretty='true')
            return True
        except ApiException as e:
            print("Exception when calling CoreV1Api->patch_namespaced_config_map: %s\n" % e)
            return False

    def create_configmap(self,data):
        api_instance = client.CoreV1Api()
        cmap = client.V1ConfigMap(metadata=client.V1ObjectMeta(name=self.cname),data=self.make_string(data))
        try:
            api_instance.create_namespaced_config_map(namespace=self.namespace,body=cmap)
            return True
        except ApiException as e:
            print("Exception when calling CoreV1Api->create_namespaced_config_map: %s\n" % e)
            return False