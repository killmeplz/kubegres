import os

class Config:
    FILE = '/tmp/state.json'
    USERNAME = 'hyperion'
    PASSWD = 'password'
    API_ADDR = 'localhost:5000'
    STORAGETYPE = 'kube'
    NAMESPACE = os.getenv('NAMESPACE', 'default')
