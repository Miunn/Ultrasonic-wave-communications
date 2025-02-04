from gui.communication_interface import CommunicationInterface
from client_communication.pitaya_socket_client_api import Client_Pitaya_Socket


class CommunicationPitayaSocket(CommunicationInterface):    
    def __init__(self, addr):
        super().__init__(addr)

        self.socketApi = Client_Pitaya_Socket(addr)

    def connect(self):
        self.socketApi.IP = self.addr
        return self.socketApi.connect()

    def fetchNewComparedData(self):
        new_data = self.socketApi.write('fetch-new-compared-data', {})
        return
    
    def requestGraph(self):
        return self.socketApi.write('request-graph', {})
    
    def changeParameter(self, parameters):
        received = self.socketApi.write('change-parameters', { "data": parameters})
        
        if received != "OK":
            return False
        return True