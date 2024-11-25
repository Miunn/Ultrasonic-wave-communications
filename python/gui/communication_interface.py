from numpy import ndarray


class CommunicationInterface:
    def emit(self, message: ndarray, freq: float, cyc: int):
        pass

    def startListening(
        self,
        freq: float,
        cyc: int,
        decimation: int,
        sig_trig: float,
        dec_trig: float,
        dec_thesh: float,
    ):
        pass

    def emergencyStop(self):
        pass
