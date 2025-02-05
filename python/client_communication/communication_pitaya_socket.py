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
        new_data = self.socketApi.write("fetch-new-compared-data", {})
        return

    def requestGraph(self):
        return self.socketApi.write("request-graph", {})

    def changeParameter(self, parameters):
        received = self.socketApi.write("change-parameters", {"data": parameters})

        return received == 0

    def emit(self, message, freq, cyc, mode=1):
        try:
            return self.socketApi.write(
                "write",
                {"message": message.tolist(), "freq": freq, "cyc": cyc, "mode": mode},
            )
        except Exception as e:
            print("Error", e)
            return 1, f"Error {e}"

    def startListening(
        self,
        freq,
        cyc,
        decimation,
        sig_trig,
        dec_trig,
        dec_thresh,
        mode=1,
    ):
        return self.socketApi.write(
            "start-listening",
            {
                "freq": freq,
                "cyc": cyc,
                "decimation": decimation,
                "sig_trig": sig_trig,
                "dec_trig": dec_trig,
                "dec_thresh": dec_thresh,
                "mode": mode,
            },
        )