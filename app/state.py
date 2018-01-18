import json

from config import Config


class State:
    def __init__(self):
        self.file = Config.FILE

    def get(self):
        try:
            with open(self.file, 'r') as file:
                res = json.load(file)
            return res
        except BaseException:
            return False

    def set(self, data):
        try:
            with open(self.file, 'w') as f:
                f.write(json.dumps(data, ensure_ascii=False))
            return True
        except BaseException:
            return False
