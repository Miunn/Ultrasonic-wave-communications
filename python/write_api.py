from modulation_to_pitaya import Write_Pitaya
from signal_processing.psk_modulation import psk_modulation

class Write_Api:
    def __init__(self, ip):
        self.pitayaWriter = Write_Pitaya(ip)

    def write(self, message, freq, cyc):
        bits = [int(i) for i in message]
        mod = psk_modulation(bits, cyc)
        self.pitayaWriter.write(mod, len(bits), channel=self.config.get('channel'), wave_form='arbitrary', freq=freq, burst=True)
