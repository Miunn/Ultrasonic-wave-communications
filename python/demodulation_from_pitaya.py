#!/usr/bin/env python3

import sys
import pitaya.redpitaya_scpi as scpi
import matplotlib.pyplot as plot
import struct
from signal_processing.psk_modulation import bpsk_demodulation, butter_lowpass_filter, decision

class Read_Pitaya:
    IP = '169.254.67.34'
    DEC = 1
    TRIG_LVL = 0.6

    def __init__(self, ip='169.254.67.34', dec=1, trig_lvl=0.6):
        self.IP = ip
        self.DEC = dec
        self.TRIG_LVL = trig_lvl

        self.rp_s = scpi.scpi(self.IP)

    def close(self):
        self.rp_s.close()

    def tx_txt(self, txt):
        self.rp_s.tx_txt(txt)

    def rx_txt(self):
        return self.rp_s.rx_txt()
    
    def acq_set(self, dec, trig_lvl, units='volts', sample_format='bin', trig_delay=8000):
        self.rp_s.acq_set(dec, trig_lvl, units=units, sample_format=sample_format, trig_delay=trig_delay)

    def acq_data(self, channel, binary=True, convert=True):
        return self.rp_s.acq_data(channel, binary=binary, convert=convert)

    def read(self, out='signal.bin'):
        self.tx_txt('ACQ:RST')
        self.acq_set(self.DEC, self.TRIG_LVL, units='volts', sample_format='bin', trig_delay=8000)
        self.tx_txt('ACQ:START')
        self.tx_txt('ACQ:TRig CH1_PE')

        while 1:
            self.tx_txt('ACQ:TRig:STAT?')
            if self.rx_txt() == 'TD':
                break

        while 1:
            self.tx_txt('ACQ:TRig:FILL?')
            if self.rx_txt() == '1':
                break

        buff = self.acq_data(1, binary=True, convert=True)

        with open(out, 'w') as f:
            f.write(' '.join([str(f) for f in buff]))

        return buff




if __name__ == "__main__":
    if len(sys.argv) >= 2:
        with open(sys.argv[1], 'r') as f:
            buff = [float(s) for s in f.readline().split()]
        
        data_lpf = butter_lowpass_filter(buff, 2, 1000, order=3)
        print("Max data_lpf:", max(data_lpf))

        plot.plot(buff)
        plot.plot(data_lpf)
    else:
        rp = Read_Pitaya(ip='10.42.0.125', dec=16)
        signal_acquired = False
        n = 0
        buff = rp.read(out='signal-dec-16-ok.bin')
            
        data_lpf = butter_lowpass_filter(buff, 2, 1000, order=3)

        plot.plot(buff)
        plot.plot(data_lpf)
        plot.ylabel('Voltage')
        plot.title('Signal')

    plot.show()