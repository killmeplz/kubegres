import app.state
from app.config import Config
import psycopg2

config = Config

#data = app.state.State().get()

def add_args(option):
    def decorator(func):
        def wrapped():
            return func(option)
        return wrapped
    return decorator


@add_args(2)
def test(name=0):
    print str(name)


test()

data = {
    '172.17.0.5':
        {
            'role':'slave',
            'state':'ready',
            'failed':0
        }
}



def check_server(server, data):
    server_data = data[server]
    if not server_data.get('failed'):
        server_data.update({'failed':0})
    try:
        connect = psycopg2.connect(
            user=config.USERNAME,
            password=config.PASSWD,
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
                server_data.update({'slave_delay':recovery_mode})
            else:
                server_data.update({'slave_delay': False})
        cursor.close()
        connect.close()
        server_data.pop('failed',None)
        return server_data

    except Exception:
        server_data['failed'] += 1
        return server_data

#curs = check_server(data.items()[0][0],data)
#print curs
#print curs.description[0]

