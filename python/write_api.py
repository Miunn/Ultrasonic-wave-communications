from conf import Configuration
from modulation_to_pitaya import Write_Pitaya
from signal_processing.psk_modulation import psk_modulation

class Write_Api:
    def __init__(self, config_file):
        self.config = Configuration(config_file)
        self.config.load()

        if not self.config.check_all(['ip', 'channel', 'frequency', 'cyc']):
            raise ValueError("Configuration file must contain 'ip', 'channel', 'frequency' and 'cyc' keys")

        self.pitayaWriter = Write_Pitaya(ip=self.config.get('ip'))

    def write(self, message):
        bits = [int(i) for i in message]
        mod = psk_modulation(bits, freq=5)
        self.pitayaWriter.write(mod, len(bits), channel=self.config.get('channel'), wave_form='arbitrary', freq=self.config.get('frequency'), burst=True)
