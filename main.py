#!/usr/bin/python
import os,subprocess,requests,socket


class Starter:

    pg_dir = '/var/lib/postgresql/9.6/main/'
    recovery_file = 'recovery.conf'
    rep_passwd = 'password'
    server_addr = 'http://10.126.8.137:5000'

    #####
    #Init file for configuring cluster
    #####

    def connect(self, method, url):
        if method == 'GET':
            r = requests.get(self.server_addr + url)
            return r.json()
        elif method == 'POST':
            data = {'hostname':socket.gethostname()}
            r =requests.post(self.server_addr + url, json=data)
            return r.json()

    def __init__(self):

        res = self.connect('POST','/cluster/check')
        if res['response'] == 0:
            self.create_cluster()
        elif res['response'] == 1:
            self.start_slave_pg()
        elif res['response'] == 2:
            self.start_postgres()

    def start_slave_pg(self):

        ip = self.connect('GET', '/master/show')
        if not ip:
            return False
        self.sysexec('rm -Rf ' + self.pg_dir + '*')
        self.sysexec('su postgres -c "pg_basebackup -h ' + str(ip[0]) + ' -D '+ self.pg_dir + ' -P -U replication --xlog-method=stream"')
        self.slave_cfg_gen(ip[0])
        self.connect('POST','/slave/add')
        self.start_postgres()

    def create_cluster(self):
        if self.connect('POST','/cluster/create') == 1:
            return False
        self.sysexec('rm -Rf '+ self.pg_dir + '*')
        env = {
            'PATH':'/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
            'PGDATA':self.pg_dir,
            'POSTGRES_DB':'hyperion',
            'POSTGRES_PASSWORD':'password',
            'POSTGRES_USER': 'hyperion'
        }
        args = ['postgres','-c','config_file=/etc/postgresql/postgresql.conf']
        os.execve('/usr/local/bin/docker-entrypoint.sh', args , env)

    def slave_cfg_gen(self, ip):

        f = open(self.pg_dir + self.recovery_file, 'w')
        config = [
            'standby_mode = \'on\'',
            'primary_conninfo = \'host=' + ip + ' port=5432 user=replication password=' + self.rep_passwd + '\'',
            'trigger_file = \'' + self.pg_dir + 'postgresql.trigger\''
        ]
        for line in config:
            f.write(line + '\n')
        f.close()

    def start_postgres(self):
        env = {
            'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
        }
        #os.execve('/bin/su',['postgres','-c',"postgres -c config_file=/etc/postgresql/postgresql.conf"],env)
        subprocess.Popen('su postgres -c "postgres -c config_file=/etc/postgresql/postgresql.conf"', shell=True)
        #os.system('su postgres -c postgres -c config_file=/etc/postgresql/postgresql.conf')
        return True

    def sysexec(self,cmd):
        """Attached cmd wrapper"""
        res = subprocess.check_output(cmd, shell=True).strip()
        return res


if __name__ == '__main__':
    pg = Starter()