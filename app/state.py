from config import Config
from storage.kubestore import KubeState
from storage.filestore import FileState

if Config.STORAGETYPE == 'kube':
    class State(KubeState): pass
elif Config.STORAGETYPE == 'file':
    class State(FileState): pass
