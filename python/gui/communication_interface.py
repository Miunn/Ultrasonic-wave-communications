from numpy import ndarray, zeros
import time


class CommunicationInterface:
    def emit(self, message: ndarray, freq: float, cyc: int) -> int:
        print(message, freq, cyc)
        time.sleep(2)
        return 0

    def startListening(
        self,
        freq: float,
        cyc: int,
        decimation: int,
        sig_trig: float,
        dec_trig: float,
        dec_thesh: float,
    ) -> tuple[int, ndarray, list[tuple[list[float], str, str]]]:
        time.sleep(5)
        return (0, zeros(2, int), [])

    def emergencyStop(self):
        return
