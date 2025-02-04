from python.communication.read_pitaya_api import Read_Pitaya
from python.communication.write_pitaya_api import Write_Pitaya
from python.gui.communication_interface import CommunicationInterface
from python.signal_processing.demodulation_api import DemodulationApi
from python.signal_processing.modulation_api import ModulationApi


class CommunicationPitaya(CommunicationInterface):
    def __init__(self, addr):
        super().__init__(addr)

        self.readPitayaApi = Read_Pitaya(addr)
        self.writePitayaApi = Write_Pitaya(addr)
        
        self.demodulationApi = DemodulationApi(addr)
        self.modulationApi = ModulationApi(addr)

    def connect(self):
        print("Trying to connect apis to pitaya")
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
