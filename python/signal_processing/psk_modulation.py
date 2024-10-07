from typing import List
import numpy as np
from scipy.signal import butter, lfilter
import sys
import matplotlib.pyplot as plt

PTS_BITS = 1000
FREQ = 5

def psk_modulation(bits: List[int]):
    len_bits = len(bits)
    linspace = np.linspace(0, len_bits, len_bits * PTS_BITS)

    c_t = np.cos(FREQ * 2 * np.pi * linspace + np.pi/2)

    # PSK Modulation
    modulated = np.zeros(len_bits * PTS_BITS)
    for i in range(len_bits):
        if bits[i] == 0:
            modulated[i * PTS_BITS:(i + 1) * PTS_BITS] = -1
        else:
            assert bits[i] == 1
            modulated[i * PTS_BITS:(i + 1) * PTS_BITS] = 1
    return modulated * c_t

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def decision(demodulated: np.ndarray):
    bits: List[int] = []
    
    for i in range(1, len(demodulated)//PTS_BITS+1):
        if demodulated[i * PTS_BITS - 1] < 0:
            bits.append(0)
        else:
            bits.append(1)

    return bits

def bpsk_demodulation(modulated: np.ndarray, freq: int = 5):
    len_modulated = len(modulated)
    linspace = np.linspace(0, len_modulated, len_modulated)

    c = np.cos(len_modulated / PTS_BITS * freq * 2 * np.pi * linspace + np.pi/2)
    
    return modulated * c

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        bits = [int(i) for i in sys.argv[1]]
        print(len(bits))
        linspace = np.linspace(0, len(bits), len(bits) * 1000)
        mod = psk_modulation(bits)
        
        #plt.plot(linspace, mod)
        
        demod = bpsk_demodulation(mod, FREQ)
        #demod = butter_lowpass_filter(demod, 0.1, 1000)
        
        
        plt.plot(linspace, demod)
        
        lpf = butter_lowpass_filter(demod, 3, 1000, order=3)
        
        bits = decision(lpf)
        print(''.join([str(i) for i in bits]))
        print(''.join([str(i) for i in bits]) == sys.argv[1])
        
        plt.plot(linspace, lpf)
        plt.show()