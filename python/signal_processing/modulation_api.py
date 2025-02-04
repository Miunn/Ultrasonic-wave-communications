from python.communication.write_pitaya_api import Write_Pitaya
from python.signal_processing.modulation_utils import psk_modulation

class ModulationApi:
    def __init__(self, ip):
        self.pitayaWriter = Write_Pitaya(ip)

    def connect(self):
        return self.pitayaWriter.connect()

    def modulate(self, bits, cyc, mode=1):
        if len(bits) == 0:
            print("[*] Skip empty message")
            return 1

        return psk_modulation(bits, cyc)