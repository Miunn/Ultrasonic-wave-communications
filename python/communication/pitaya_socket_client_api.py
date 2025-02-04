import socketio

class Client_Pitaya_Socket:
    IP = '10.42.0.125'
    
    def __init__(self, ip='10.42.0.125'):
        self.sio = socketio.SimpleClient()

    def connect(self):
        try:
            self.sio.connect(f'http://{self.ip}')
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def write(self, event, args):
        self.sio.emit(event, args)