import json

class Configuration:

    config: dict

    def __init__(self, file):
        self.filename = file

    def load(self):
        with open(self.filename, 'r') as f:
            self.config = json.load(f)
    
    def check(self, key):
        return key in self.config
    
    def check_all(self, keys):
        return all([self.check(key) for key in keys])

    def get(self, key):
        return self.config[key]
    
    def set(self, key, value):
        self.config[key] = value

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.config, f, indent=4)