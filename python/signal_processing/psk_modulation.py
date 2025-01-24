from typing import List
import numpy as np
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
import math
from utils import get_sampling_signal_frequency

PTS_BITS = 1000
FREQ = 5

def psk_modulation(bits: List[int], cyc: int = 5):
    len_bits = len(bits)
    pts_bits = 16384//(len(bits)+2)
    linspace = np.linspace(0, len_bits, len_bits * pts_bits)
    c_t = np.cos(cyc * 2 * np.pi * linspace + np.pi/2)

    # PSK Modulation
    modulated = np.zeros(len_bits * pts_bits)
    for i in range(len_bits):
        if bits[i] == 0:
            modulated[i * pts_bits:(i + 1) * pts_bits] = -1
        else:
            assert bits[i] == 1
            modulated[i * pts_bits:(i + 1) * pts_bits] = 1
    
    first_positive = c_t[:pts_bits]
    waiting =  np.zeros(pts_bits)
    modulation = (modulated * c_t)[:len_bits * pts_bits]
    return np.concatenate((first_positive, waiting, modulation))
    #return modulation

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

def bpsk_demodulation(modulated: np.ndarray, freq, decimation):
    len_modulated = len(modulated)
    #f = 2 * (0.002402) * np.pi
    signal_frequency = get_sampling_signal_frequency(freq, decimation)
    f = 2 * signal_frequency * np.pi
    linspace = np.linspace(0, len_modulated, len_modulated)
    c = np.linspace(0, len_modulated, len_modulated)
    for i in range(len_modulated):
        x = float(linspace[i])
        c[i] = math.cos(f * x + np.pi/2)
    #plt.plot(linspace)
    #linspace = f * linspace + np.pi/2
    #plt.title("Linspace")
    #plt.show()

    
    #c = np.cos((len_modulated / (PTS_BITS) * freq * 2 * np.pi * linspace + np.pi/2))
    #c = np.cos(len_modulated * 15 * freq * 2 * np.pi * linspace + np.pi/2)
    #c = np.cos(linspace)
    

    #plt.plot(c)
    
    return modulated * c

def correlation_demodulation(modulated: np.ndarray, freq, decimation):
    len_modulated = len(modulated)
    signal_frequency = get_sampling_signal_frequency(freq, decimation)

    return

if __name__ == "__main__":
    mod = psk_modulation([1, 0, 1, 0, 1, 1], cyc=1)
    plt.plot(mod)
    plt.show()