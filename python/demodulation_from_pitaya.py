#!/usr/bin/env python3

import sys
import pitaya.redpitaya_scpi as scpi
import matplotlib.pyplot as plot
import numpy as np
from scipy.signal import butter, filtfilt
from signal_processing.psk_modulation import bpsk_demodulation, butter_lowpass_filter, decision

class Read_Pitaya:
    IP = '10.42.0.125'

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
    if len(sys.argv) >= 2:
        #with open(sys.argv[1], 'r') as f:
        #    probing = [float(s) for s in f.readline().split()][75:140]
        freq=250000
        decimation=64
        cyc=5
        sig_trig=0.6

        import classifiedjson
        with open(sys.argv[1], 'r') as f:
            buff = classifiedjson.load(f)[0][0]
        
        import scipy.signal
        import scipy.integrate

        from utils import get_one_block_step, get_sampling_signal_frequency
        from read_api import Read_Api
        import math

        # Correlate the signal with the first sine as probing signal
        #probing_sine = buff[80:130]
        #correlated = Read_Api.correlate_signal(probing_sine, buff)

        # Normalize the signal
        normalized_correlated = buff / np.max(buff)

        demodulated = bpsk_demodulation(normalized_correlated, freq, decimation)

        lpf = butter_lowpass_filter(demodulated, 5, 100, order=6)

        fig, (signal_ax) = plot.subplots(1)
        #probing_ax.plot(probing_sine)

        signal_frequency = get_sampling_signal_frequency(freq, decimation)
        print(signal_frequency)
        f = 2 * signal_frequency * np.pi
        linspace = np.linspace(0, len(buff), len(buff))
        c = np.linspace(0, len(buff), len(buff))
        for i in range(len(buff)):
            x = float(linspace[i])
            c[i] = math.cos(f * x + np.pi/2)
        
        #probing_ax.plot(probing_sine)
        signal_ax.plot(buff)
        #signal_ax.plot(demodulated)
        #signal_ax.plot(lpf, 'g')
        #signal_ax.plot([0]*len(lpf), 'purple')
        #signal_ax.plot([0.5]*len(lpf), 'purple')
        #signal_ax.plot([-0.5]*len(lpf), 'purple')
        len_buff = len(buff)

        for x in range(119, len(lpf))[::get_one_block_step(freq, cyc, decimation)]:
            signal_ax.axvline(x, color='r')

        integrals = []
        trig_x = 0
        for x in range(len(lpf)):
            if lpf[x] > 0.2:
                trig_x = x
                break
        
        prev_x = 0
        for x in range(trig_x, len(lpf))[::get_one_block_step(freq, cyc, decimation)]:
            #signal_ax.axvline(x, color='r')

            if prev_x != 0:
                integrals.append(scipy.integrate.simpson(lpf[prev_x:x], dx=1))
            
            prev_x = x

        received_bits = []
        for integral in integrals:
            if integral > 0.1 * get_one_block_step(freq, cyc, decimation) * 0.5:
                received_bits.append(1)
            elif integral < -0.1 * get_one_block_step(freq, cyc, decimation) * 0.5:
                received_bits.append(0)

        print(len(integrals))
        print(len(received_bits))
        print(''.join([str(i) for i in received_bits]))

        #with open("signal-dec-64-work-voltage-max.bin", "w") as f:
        #    f.write(' '.join([str(f) for f in buff]))

        #with open("signal-dec-64-work-demod-max.bin", "w") as f:
        #    f.write(' '.join([str(f) for f in demodulated]))

        #with open("signal-dec-64-work-lpf-max.bin", "w") as f:
        #    f.write(' '.join([str(f) for f in lpf]))

    else:

        from utils import get_one_block_step
        freq=250000
        decimation=64
        cyc=5
        sig_trig=0.6
        rp = Read_Pitaya(ip='10.42.0.125')
        signal_acquired = False
        buff = rp.read(64, 0.6)

        data = rp.read(decimation, sig_trig)

        # Correlate the signal with the first sine as probing signal
        probing_sine = data[75:75+get_one_block_step(freq, 5, decimation)]
        correlated = rp.correlate_signal(probing_sine, data)

        # Normalize the signal
        normalized_correlated = correlated / np.max(correlated)

        demodulated = bpsk_demodulation(normalized_correlated, freq, decimation)

        lpf = butter_lowpass_filter(demodulated, 5, 100, order=6)

        fig, (probing_ax, signal_ax, cross_ax) = plot.subplots(3)
        probing_ax.plot(probing_sine)
        signal_ax.plot(data)
        cross_ax.plot(correlated)

        #plot.plot(lpf)
        plot.ylabel('Voltage')
        plot.title('Signal')

    plot.show()