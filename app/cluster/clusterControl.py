from cluster import Cluster

class clusterControl():

    def __init__(self,state):
        self.cluster = Cluster(state)
        self.check(self.cluster)

    def check(self,cluster):
        state = cluster.cluster_show()
        if not state:
            return False
        for name, server in state.iteritems():
            if server['role'] == 'master' and server.get('failed',0) >= 3:
                return 'Server %s has failed, switched to new master: %s' % (name , self.cluster.failover())
            else:
                return False
