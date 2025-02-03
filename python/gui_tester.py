import threading
from gui.gui import Gui
from gui.communication_interface import CommunicationInterface
from read_api import Read_Api
from write_api import Write_Api


class CommunicationPitaya(CommunicationInterface):
    def __init__(self, addr):
        super().__init__(addr)

        self.read_api = Read_Api(addr)
        self.write_api = Write_Api(addr)

    def connect(self):
        print("Trying to connect apis to pitaya")
        return self.read_api.connect() and self.write_api.connect()

    def emit(self, message, freq, cyc, mode=1):
        self.write_api.write(message, freq, cyc, mode=mode)
        return 0

    def startListening(self, freq, cyc, decimation, sig_trig, dec_trig, dec_thesh, mode=1):
        """voltage, demod, lpf, bits = self.read_api.startListening(
            freq, cyc, decimation, sig_trig, dec_trig, dec_thesh
        )

        print(f"[*] Read : {bits}")
        return [
            0,
            bits,
            [
                (voltage, "#BBBBFF", "Voltage"),
                (demod, "#FFBB99", "Demodulated"),
                (lpf, "red", "Low-pass filtered"),
            ],
        ]"""
        signal, square_correlation, bits = self.read_api.startListening(freq, cyc, decimation, sig_trig, dec_trig, dec_thesh, mode=mode)
        return [
            0,
            bits,
            [
                (
                    signal,
                    "#BBBBFF",
                    "Signal"
                ),
                (
                    square_correlation,
                    "orange",
                    "Correlation"
                )
            ]
        ]
        
    def readFromSignal(self, signal, freq: int, cyc: int, decimation: int, sig_trig=0.2):
        return self.read_api.readFromSignal(signal, freq, cyc, decimation, sig_trig)

    def emergencyStop(self):
        return super().emergencyStop()


if __name__ == "__main__":
    g = Gui(CommunicationPitaya("10.42.0.125"))
    # g = Gui()
    g.mainloop()
