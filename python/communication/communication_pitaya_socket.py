from python.communication.pitaya_socket_client_api import Client_Pitaya_Socket
from gui.communication_interface import CommunicationInterface


class CommunicationPitayaSocket(CommunicationInterface):    
    def __init__(self, addr):
        super().__init__(addr)

        self.socketApi = Client_Pitaya_Socket(addr)

    def fetchNewComparedData(self):
        return super().fetchNewComparedData()
    
    def requestGraph(self):
        return super().requestGraph()
    
    def changeParameter(self, parameters):
        return super().changeParameter(parameters)