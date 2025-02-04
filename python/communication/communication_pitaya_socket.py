from communication.pitaya_socket_client_api import Client_Pitaya_Socket
from gui.communication_interface import CommunicationInterface


class CommunicationPitayaSocket(CommunicationInterface):    
    def __init__(self, addr):
        super().__init__(addr)

        self.socketApi = Client_Pitaya_Socket(addr)

    def connect(self):
        self.socketApi.IP = self.addr
        return self.socketApi.connect()

    def fetchNewComparedData(self):
        return super().fetchNewComparedData()
    
    def requestGraph(self):
        return super().requestGraph()
    
    def changeParameter(self, parameters):
        return super().changeParameter(parameters)