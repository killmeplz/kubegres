from Queue import Queue
from threading import Thread, Lock
from clusterControl import clusterControl
import psycopg2, time

class HealthCheck(Thread):

    def __init__(self,state,config):
        Thread.__init__(self)
        self.stateClass = state
        self.config = config

    def load_state(self):
        self.state = self.stateClass.get()

    def fill_queue(self,queue):
        for key, _ in self.state.iteritems():
            queue.put(key)
        return queue

    def run(self):
        while True:
            time.sleep(5)
            self.load_state()
            if not self.state:
                print 'No servers'
                continue
            queue = Queue()
            th = [None] * len(self.state)
            state_lock = Lock()
            for i in range(len(th)):
                th[i] = Checker(queue, self, state_lock)
                th[i].setDaemon(True)
                th[i].start()
            self.fill_queue(queue)
            queue.join()
            res = clusterControl(self.stateClass)
            if res:
                print res
            print self.state


class Checker(Thread):

    def __init__(self, queue, parent, lock):
        Thread.__init__(self)
        self.lock = lock
        self.parentClass = parent
        self.queue = queue


    def run(self):
        server = self.queue.get()
        serv_state = self.connect(server, self.parentClass.state)
        self.queue.task_done()
        self.commit_changes(server,serv_state)

    def connect(self,server,data):
        server_data = data[server]
        if not server_data.get('failed'):
            server_data.update({'failed': 0})
        try:
            connect = psycopg2.connect(
                user=self.parentClass.config.USERNAME,
                password=self.parentClass.config.PASSWD,
                host=server
            )
            cursor = connect.cursor()
            if server_data['role'] == 'master':
                cursor.execute('select state from pg_stat_replication;')
                master_state = cursor.fetchone()[0]
                if master_state:
                    server_data.update({'master_state': master_state})
                else:
                    server_data.update({'master_state': 'not_streaming'})
            else:
                cursor.execute('select pg_is_in_recovery();')
                recovery_mode = cursor.fetchone()[0]
                if recovery_mode:
                    server_data.update({'slave_delay': recovery_mode})
                else:
                    server_data.update({'slave_delay': False})
            cursor.close()
            connect.close()
            server_data.pop('failed', None)
            return server_data

        except Exception:
            server_data['failed'] += 1
            return server_data

    def commit_changes(self,server,data):
        self.lock.acquire(1)
        self.parentClass.state.update({server:data})
        self.parentClass.stateClass.set(self.parentClass.state)
        self.lock.release()