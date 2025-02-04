from gui.communication_interface import CommunicationInterface
from pitaya_communication.pitaya_socket_client_api import Client_Pitaya_Socket


class CommunicationPitayaSocket(CommunicationInterface):    
    def __init__(self, addr):
        super().__init__(addr)

        self.socketApi = Client_Pitaya_Socket(addr)

    def connect(self):
        self.socketApi.IP = self.addr
        return self.socketApi.connect()

    def fetchNewComparedData(self):
        self.socketApi.write('fetch-new-compared-data', {})
        
    
    def requestGraph(self):
        self.socketApi.write('request-graph', {})
        
    
    def changeParameter(self, parameters):
        self.socketApi.write('change-parameters', {})
        