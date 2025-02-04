from communication.read_pitaya_scpi_api import Read_Pitaya_SCPI
from communication.write_pitaya_scpi_api import Write_Pitaya_SCPI
from gui.communication_interface import CommunicationInterface
from signal_processing.demodulation_api import DemodulationApi
from signal_processing.modulation_api import ModulationApi

from enum import StrEnum

class CommunicationMode(StrEnum):
    SCPI = "scpi"                   # Use distant RedPitaya server to send and receive signals
    STANDALONE = "standalone"       # Run on local RedPitaya without gui
    DEFAULT = "default"             # Connect to distant standalone instance

class CommunicationPitaya(CommunicationInterface):
    def __init__(self, mode: CommunicationMode, addr):
        super().__init__(addr)

        if (mode == CommunicationMode.STANDALONE):
            return
        elif (mode == CommunicationMode.SCPI):
            self.readPitayaApi = Read_Pitaya_SCPI(addr)
            self.writePitayaApi = Write_Pitaya_SCPI(addr)
        elif (mode == CommunicationMode.DEFAULT):
            return
        else:
            raise ValueError("Invalid mode")

        self.demodulationApi = DemodulationApi()
        self.modulationApi = ModulationApi()

    def toggleMode(self, current):
        return super().toggleMode(current)

    def connect(self, ip):
        print("Trying to connect apis to pitaya")
        self.readPitayaApi.IP = ip
        self.writePitayaApi.IP = ip
        return self.readPitayaApi.connect() and self.writePitayaApi.connect()

    def emit(self, message, freq, cyc, mode=1):
        mod = self.modulationApi.modulate(message, cyc, mode=mode)
        self.writePitayaApi.write(mod, len(message), cyc, channel=1, wave_form='arbitrary', freq=freq, burst=True)
        return 0

    def startListening(self, freq, cyc, decimation, sig_trig, dec_trig, dec_thresh, mode=1):
        data = self.readPitayaApi.read(decimation, sig_trig)
        signal, square_correlation, bits = self.demodulationApi.readData(data, freq, cyc, decimation, dec_thresh, sig_trig)

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
        return self.demodulationApi.readFromSignal(signal, freq, cyc, decimation, sig_trig)

    def emergencyStop(self):
        return super().emergencyStop()
