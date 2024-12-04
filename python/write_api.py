from modulation_to_pitaya import Write_Pitaya
from signal_processing.psk_modulation import psk_modulation
from matplotlib import pyplot as plt

class Write_Api:
    def __init__(self, ip):
        self.pitayaWriter = Write_Pitaya(ip)

    def write(self, bits, freq, cyc):
        if len(bits) == 0:
            print("[*] Skip empty message")
            return 1
        mod = psk_modulation(bits, cyc)
        
        self.pitayaWriter.write(mod, len(bits), cyc, channel=1, wave_form='arbitrary', freq=freq, burst=True)
        return 0