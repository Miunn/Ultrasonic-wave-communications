from signal_processing.modulation_utils import psk_modulation

class ModulationApi:
    def modulate(self, bits, cyc, mode=1):
        if len(bits) == 0:
            print("[*] Skip empty message")
            return 1

        return psk_modulation(bits, cyc, mode)