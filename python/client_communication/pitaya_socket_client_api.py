import socketio

class Client_Pitaya_Socket:
    IP = '10.42.0.125'
    
    def __init__(self, ip='10.42.0.125'):
        self.IP = ip
        self.sio = socketio.SimpleClient()

    def connect(self):
        print(f"[*] Client socket trying to connect to {self.IP}")
        try:
            self.sio.connect(f'http://{self.IP}', wait_timeout=5)
            return True
        except Exception as e:
            print("Exception connecting to socket")
            print(f"Error: {e}")
            return False
    
    def write(self, event, args):
        if not self.sio.connected:
            raise Exception("Socket not connected")
        
        self.sio.emit(event, args)