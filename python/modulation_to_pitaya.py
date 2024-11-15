#!/usr/bin/env python3

import sys
import pitaya.redpitaya_scpi as scpi
from signal_processing.psk_modulation import psk_modulation
import matplotlib.pyplot as plt

class Write_Pitaya:
    IP = '169.254.67.34'

    def __init__(self, ip='169.254.67.34'):
        self.IP = ip

        self.rp_s = scpi.scpi(self.IP)

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

    def write(self, data, channel=1, wave_form='arbitrary', freq=2000, volt=1, burst=True):
        self.rp_s.tx_txt('GEN:RST')
        self.rp_s.sour_set(channel, wave_form, volt, freq/(len(bits)*5), data=data, burst=burst)
        self.rp_s.tx_txt('OUTPUT1:STATE ON')
        self.rp_s.tx_txt('SOUR1:TRig:INT')
        
        self.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Provide a bit sequence as argument or sine to generate a sine wave")
        sys.exit(1)

    if sys.argv[1] == 'sine':
        wp = Write_Pitaya()
        wp.write([], channel=1, wave_form='sine', freq=250000, burst=False)
        sys.exit(0)
    
    bits = [int(i) for i in sys.argv[1]]
    mod = psk_modulation(bits, freq=5)
    wp = Write_Pitaya()
    wp.write(mod, channel=1, wave_form='arbitrary', freq=250000, burst=True)

    plt.plot(mod)
    plt.show()
    sys.exit(0)