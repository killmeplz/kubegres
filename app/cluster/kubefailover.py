import kubernetes
from kubernetes import config
from kubernetes.client.apis import core_v1_api
from kubernetes.stream import stream
from kubernetes.client.rest import ApiException

class KubeFailOver():

    def __init__(self):
        config.load_incluster_config()
        self.api = core_v1_api.CoreV1Api()

    def slave_promote(self,slave_name):
        exec_command = ['touch','/var/lib/postgresql/9.6/main/postgresql.trigger']
        self.pod_exec(slave_name,exec_command)
        self.add_master_label(slave_name)
        return True

    def add_master_label(self,pod):
        body = [
            {
                "op": "add", "path": "/metadata/labels/pg_master", "value": "true"
            }
        ]
        return self.label_manage(pod,body)

    def remove_master_label(self,pod):
        body = [
            {
                "op": "remove", "path": "/metadata/labels/pg_master"
            }
        ]
        return self.label_manage(pod,body)

    def label_manage(self,pod,body):
        api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient())
        try:
            api_instance.patch_namespaced_pod(pod, 'ott', body, pretty='true')
            return True
        except ApiException as e:
            print("Exception when calling CoreV1Api->patch_namespaced_pod: %s\n" % e)
            return False

    def master_demote(self,master_name):
        exec_command = [ 'kill' , '-9' , '1' ]
        self.pod_exec(master_name, exec_command)
        self.add_master_label(master_name)
        return True


    def pod_exec(self,pod,command):
        resp = stream(self.api.connect_get_namespaced_pod_exec, pod, 'ott',
                      command=command,
                      stderr=True, stdin=False,
                      stdout=True, tty=False)
        return True if resp else False

