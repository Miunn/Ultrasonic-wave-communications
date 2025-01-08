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

    def emit(self, message, freq, cyc):
        self.write_api.write(message, freq, cyc)
        return 0

    def startListening(self, freq, cyc, decimation, sig_trig, dec_trig, dec_thesh):
        voltage, demod, lpf, bits = self.read_api.startListening(
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
        ]

    def emergencyStop(self):
        return super().emergencyStop()


if __name__ == "__main__":
    g = Gui(CommunicationPitaya("10.42.0.125"))
    # g = Gui()
    g.mainloop()
