import socketio

from signal_processing.modulation_api import ModulationApi
from signal_processing.demodulation_api import DemodulationApi


class RedPitaya_Standalone:
    def __init__(self):
        self.server = socketio.Server()
        self.events()
        
        self.modulationApi = ModulationApi()
        self.demodulationApi = DemodulationApi()
    
    def getServerApp(self):
        return socketio.WSGIApp(self.server)
    
    def events(self):
        @self.server.event
        def connect(sid, environ, auth):
            print('connect ', sid)

        @self.server.event
        def disconnect(sid, reason):
            print('disconnect ', sid, reason)