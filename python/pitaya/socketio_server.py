import socketio

class SocketIOServer:
    server: socketio.Server
    
    def __init__(self):
        self.server = socketio.Server()
    
        
        
def app():
    serv = SocketIOServer()
    return socketio.WSGIApp(serv.server)