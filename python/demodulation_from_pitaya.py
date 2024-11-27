#!/usr/bin/env python3

import sys
import pitaya.redpitaya_scpi as scpi
import matplotlib.pyplot as plot
import numpy as np
from scipy.signal import butter, filtfilt
from signal_processing.psk_modulation import bpsk_demodulation, butter_lowpass_filter, decision

LPF_TRIGGER_LEVEL = 0.2

class Read_Pitaya:
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

    def read(self, dec, trig_lvl):
        self.tx_txt('ACQ:RST')
        self.acq_set(dec, trig_lvl, units='volts', sample_format='bin', trig_delay=8100)
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
    """with open("signal-dec-64-work-voltage.bin", "r") as f:
        voltage = [float(n) for n in f.readline().split()]

    with open("signal-dec-64-work-demod.bin", "r") as f:
        demod = [float(n) for n in f.readline().split()]

    
    plot.plot(voltage)
    plot.plot(demod)
    plot.show()
    sys.exit(0)"""

    if len(sys.argv) >= 2:
        #with open(sys.argv[1], 'r') as f:
        #    probing = [float(s) for s in f.readline().split()][75:140]

        with open(sys.argv[1], 'r') as f:
            buff = [float(s) for s in f.readline().split()]
        
        import scipy.signal
        import scipy.integrate
        len_buff = len(buff)

        ref_signal = np.cos(2 * (0.1275) * np.pi * np.linspace(0, 16384, 16384) + np.pi/2)

        corr = scipy.signal.correlate(buff, buff[75:140], mode="full")

        corr = corr / max(corr)

        demodulated = bpsk_demodulation(corr, freq=5)
        lpf = butter_lowpass_filter(demodulated, 5, 100, order=6)
        #bits = decision(lpf)
        #print(''.join([str(i) for i in bits]))

        fig, (probing_ax, signal_ax, cross_ax) = plot.subplots(3)
        
        probing_ax.plot(buff[75:140])
        signal_ax.plot(buff)
        cross_ax.plot(corr)
        cross_ax.plot(demodulated)
        cross_ax.plot(lpf)

        integrals = []
        trig_x = 0
        for x in range(len(lpf)):
            if lpf[x] > LPF_TRIGGER_LEVEL:
                trig_x = x
                break
        
        prev_x = 0
        for x in range(trig_x, len(lpf))[::39]:
            cross_ax.axvline(x, color='r')

            if prev_x != 0:
                integrals.append(scipy.integrate.simpson(lpf[prev_x:x], dx=1))
            
            prev_x = x

        print(integrals)

        received_bits = []
        for integral in integrals:
            if integral > 0.3 * 19.5:
                received_bits.append(1)
            elif integral < -0.3 * 19.5:
                received_bits.append(0)

        print(len(integrals))
        print(len(received_bits))
        print(''.join([str(i) for i in received_bits]))

        with open("signal-dec-64-work-voltage-max.bin", "w") as f:
            f.write(' '.join([str(f) for f in buff]))

        with open("signal-dec-64-work-demod-max.bin", "w") as f:
            f.write(' '.join([str(f) for f in demodulated]))

        with open("signal-dec-64-work-lpf-max.bin", "w") as f:
            f.write(' '.join([str(f) for f in lpf]))

    else:
        rp = Read_Pitaya(ip='10.42.0.125', dec=64)
        signal_acquired = False
        buff = rp.read(out='signal-dec-64-probing-message-work.bin')

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