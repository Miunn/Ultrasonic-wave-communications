from typing import List
import numpy as np
from scipy.signal import butter, lfilter
import sys
import matplotlib.pyplot as plt
import math

PTS_BITS = 1000
FREQ = 5

def psk_modulation(bits: List[int], freq: int = 5):
    len_bits = len(bits)
    pts_bits = 16384//len(bits)
    linspace = np.linspace(0, len_bits, len_bits * pts_bits)
    c_t = np.cos(freq * 2 * np.pi * linspace + np.pi/2)

    # PSK Modulation
    modulated = np.zeros(len_bits * pts_bits)
    for i in range(len_bits):
        if bits[i] == 0:
            modulated[i * pts_bits:(i + 1) * pts_bits] = -1
        else:
            assert bits[i] == 1
            modulated[i * pts_bits:(i + 1) * pts_bits] = 1
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
    print("Modulated len:", len_modulated)
    f = 2 * (0.002402) * np.pi
    linspace = np.linspace(0, len_modulated, len_modulated)
    c = np.linspace(0, len_modulated, len_modulated)
    for i in range(len_modulated):
        x = float(linspace[i])
        c[i] = math.cos(f * x + np.pi/2)
    #plt.plot(linspace)
    #linspace = f * linspace + np.pi/2
    print(linspace)
    #plt.title("Linspace")
    #plt.show()

    #c = np.cos((len_modulated / (PTS_BITS) * freq * 2 * np.pi * linspace + np.pi/2))
    #c = np.cos(len_modulated * 15 * freq * 2 * np.pi * linspace + np.pi/2)
    #c = np.cos(linspace)
    

    #plt.plot(c)
    
    return modulated * c

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        bits = [int(i) for i in sys.argv[1]]
        print(len(bits))
        mod = psk_modulation(bits)
    else:
        with open("../pitayareadings.bin", "r") as f:
            mod = [float(s) for s in f.readline().split()]
    plt.plot(mod)
        
    #plt.plot(linspace, mod)
        
        
    demod = bpsk_demodulation(mod)
    #demod = butter_lowpass_filter(demod, 0.1, 1000)
    plt.plot(demod)

    plt.show()

    lpf = butter_lowpass_filter(demod, 1, 1000, order=5)

    bits = decision(lpf)
    print(''.join([str(i) for i in bits]))
    #print(''.join([str(i) for i in bits]) == sys.argv[1])

    plt.plot(lpf)
    plt.show()