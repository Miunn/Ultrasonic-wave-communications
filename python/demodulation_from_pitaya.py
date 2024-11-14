#!/usr/bin/env python3

import sys
import pitaya.redpitaya_scpi as scpi
import matplotlib.pyplot as plot
from scipy.signal import butter, filtfilt, lfilter
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
    
    def acq_set(self, dec, trig_lvl, units='volts', sample_format='bin', trig_delay=8192):
        self.rp_s.acq_set(dec, trig_lvl, units=units, sample_format=sample_format, trig_delay=trig_delay)

    def acq_data(self, channel, binary=True, convert=True):
        return self.rp_s.acq_data(channel, binary=binary, convert=convert)

    def read(self, out='signal.bin'):
        self.tx_txt('ACQ:RST')
        self.acq_set(self.DEC, self.TRIG_LVL, units='volts', sample_format='bin', trig_delay=8100)
        self.tx_txt('ACQ:START')
        self.tx_txt('ACQ:TRig CH1_PE')
        print("[*] Acquisition params set, ready to acquire")

        while 1:
            self.tx_txt('ACQ:TRig:STAT?')
            if self.rx_txt() == 'TD':
                break

        while 1:
            self.tx_txt('ACQ:TRig:FILL?')
            if self.rx_txt() == '1':
                break

        print("[*] Triggered, acquire buffer")
        buff = self.acq_data(1, binary=True, convert=True)

        with open(out, 'w') as f:
            f.write(' '.join([str(f) for f in buff]))

        return buff


def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        with open(sys.argv[1], 'r') as f:
            buff = [float(s) for s in f.readline().split()]
        
        data_lpf = lfilter([1.0 / 15] * 15, 1, buff)
        demodulated = bpsk_demodulation(buff, freq=5)
        lpf = butter_lowpass_filter(demodulated, 3, 1000, order=3)
        bits = decision(lpf)
        print(''.join([str(i) for i in bits]))

        plot.plot(buff)
        plot.plot(demodulated)
        plot.plot(lpf)

    else:
        rp = Read_Pitaya(ip='10.42.0.125', dec=64)
        signal_acquired = False
        buff = rp.read(out='signal-dec-64-work.bin')

        data_lpf = butter_lowpass_filter(buff, 2, 1000, order=3)
        demodulated = bpsk_demodulation(buff, freq=5)
        lpf = butter_lowpass_filter(demodulated, 3, 1000, order=3)
        bits = decision(lpf)
        print(''.join([str(i) for i in bits]))
        
        plot.plot(buff)
        plot.plot(demodulated)
        #plot.plot(lpf)
        plot.ylabel('Voltage')
        plot.title('Signal')

    plot.show()