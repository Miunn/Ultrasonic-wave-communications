#!/usr/bin/env python3

import sys
import pitaya.redpitaya_scpi as scpi
from signal_processing.psk_modulation import psk_modulation
import matplotlib.pyplot as plt
from utils import get_signal_frequency_from_sampling

class Write_Pitaya:
    IP = '10.42.0.125'
    rp_s: scpi.scpi

    def __init__(self, ip='10.42.0.125'):
        self.IP = ip

    def connect(self):
        try:
            self.rp_s = scpi.scpi(self.IP, timeout=10)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def close(self):
        self.rp_s.close()

    def tx_txt(self, txt):
        self.rp_s.tx_txt(txt)

    def rx_txt(self):
        return self.rp_s.rx_txt()
    
    def acq_set(self, dec, trig_lvl, units='volts', sample_format='bin', trig_delay=8192):
        self.rp_s.acq_set(dec, trig_lvl, units=units, sample_format=sample_format, trig_delay=trig_delay)

    def acq_data(self, channel, binary=True, convert=True):
        return self.rp_s.acq_data(channel, binary=binary, convert=convert)

    def write(self, data, len_data, cyc, channel=1, wave_form='arbitrary', freq=250000, volt=1, burst=True):
        self.rp_s.tx_txt('GEN:RST')
        if wave_form != 'arbitrary':
            self.rp_s.sour_set(channel, wave_form, volt, freq, burst=burst)
        else:
            self.rp_s.sour_set(channel, wave_form, volt, get_signal_frequency_from_sampling(freq, cyc, len_data), data=data, burst=burst)
        self.rp_s.tx_txt(f'OUTPUT{channel}:STATE ON')
        self.rp_s.tx_txt(f'SOUR{channel}:TRig:INT')
        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Provide a bit sequence as argument or sine to generate a sine wave")
        sys.exit(1)

    if sys.argv[1] == 'sine':
        wp = Write_Pitaya(ip='10.42.0.125')
        wp.write([], 1, 0, channel=1, wave_form='sine', freq=250000, burst=False)
        sys.exit(0)
    
    bits = [int(i) for i in sys.argv[1]]
    mod = psk_modulation(bits, cyc=3)
    plt.xlim(0, 16384)
    plt.plot(mod)
    #wp = Write_Pitaya(ip='10.42.0.125')
    #wp.write(mod, len(bits), 1, channel=1, wave_form='arbitrary', freq=200000, burst=True)

    plt.plot(mod)
    plt.show()
    sys.exit(0)