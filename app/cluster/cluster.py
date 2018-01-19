from kubefailover import KubeFailOver

class Cluster:
    def __init__(self, state):
        self.s = state

    def cluster_create(self, master_hostname):
        if not self.check_cluster_exists():
            data = {
                master_hostname: {
                    'state': 'ready',
                    'role': 'master'
                }
            }
            list = {}
            list.update(data)
            KubeFailOver().add_master_label(master_hostname)
            return self.s.set(list)
        else:
            return False

    def cluster_show(self):
        return self.s.get()

    def check_cluster_exists(self):
        if self.s.get():
            return True
        else:
            return False

    def check_master(self, hostname):
        state = self.s.get()
        if state[hostname]['role'] == 'master':
            return True
        else:
            return False

    def master_demote(self):
        new_master = self.master_elect()
        if not new_master:
            return False
        else:
            state = self.s.get()
            for master in self.master_show():
                state[master]['role'] = 'slave'
            self.s.set(state)
            return True

    def master_show(self):
        cluster = self.s.get()
        list = []
        for key, value in cluster.iteritems():
            if value['role'] == 'master' and value['state'] == 'ready':
                list.append(key)
        return list

    def slave_show(self):
        cluster = self.s.get()
        list = []
        for key, value in cluster.iteritems():
            if value['role'] == 'slave' and value['state'] == 'ready':
                list.append(key)
        return list

    def master_elect(self):
        slaves = self.slave_show()
        if slaves:
            return slaves[0]
        else:
            return False

    def slave_add(self, hostname):
        data = {
            hostname: {
                'state': 'ready',
                'role': 'slave'
            }
        }
        list = self.s.get()
        if list:
            list.update(data)
            return self.s.set(list)
        else:
            return False

    def server_delete(self, server):
        state = self.s.get()
        if not state.pop(server, False):
            return self.s.set(state)
        else:
            return False

    def slave_promote(self, slave):
        state = self.s.get()
        state[slave]['role'] = 'master' if KubeFailOver().slave_promote(slave) else False
        return self.s.set(state)

    def failover(self):
        new_master = self.master_elect()
        old_master = self.master_show()
        if self.master_demote():
            self.slave_promote(new_master)
            KubeFailOver().master_demote(old_master[0])
            return True
        else:
            return False
