import numpy as np
import socketio

from pitaya_communication.read_pitaya_api import Read_Pitaya_API
from pitaya_communication.write_pitaya_api import Write_Pitaya_API
from signal_processing.modulation_api import ModulationApi
from signal_processing.demodulation_api import DemodulationApi


class RedPitaya_Standalone:
    
    unknownErrors: int = 0
    ioron_frame_errors: int = 0
    encapsulated_frame_errors: int = 0
    valid_data: int = 0
    
    last_graph: list[tuple[np.ndarray, str, str]] = []
    last_message: np.ndarray = np.array([])
    
    def __init__(self):
        self.server = socketio.Server()
        self.events()
        
        self.readPitayaApi = Read_Pitaya_API()
        self.writePitayaApi = Write_Pitaya_API()
        
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
    
        @self.server.on('fetch-new-compared-data')
        def onFetchNewComparedData(sid, data):
            print('Fetch new compared data')
            return (
                    self.unknownErrors,
                    self.ioron_frame_errors,
                    self.encapsulated_frame_errors,
                    self.valid_data
                )
            
        @self.server.on('request-graph')
        def onRequestGraph(sid, data):
            print('Request graph')
            
            # Map ndarray graph inside last_graph to a list
            serializable_graph = []
            
            for graph in self.last_graph:
                serializable_graph.append(
                    (
                        graph[0].tolist(),
                        graph[1],
                        graph[2]
                    )
                )
            
            return (
                self.last_message.tolist(),
                serializable_graph
            )
            
        @self.server.on('change-parameters')
        def onChangeParameters(sid, data):
            print('Change parameters')
            print(data)
            return "OK"
    
    def start_daemon():
        
        return