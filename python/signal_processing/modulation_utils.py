from typing import List
import numpy as np
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
import math
from utils import get_sampling_signal_frequency

PTS_BITS = 1000
FREQ = 5

def psk_modulation(bits: List[int], cyc: int = 5, mode=1):
    # Mode
    # - 0 : To be demodulated with bpsk (without probe)
    # - 1 : To be demodulated with cross (with probe)
    
    len_bits = len(bits)
    if mode == 1:
        pts_bits = 16384//(len(bits)+2)
    else:
        pts_bits = 16384//(len(bits))
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
    
    modulation = (modulated * c_t)[:len_bits * pts_bits]
    if mode == 1:
        first_positive = c_t[:pts_bits]
        waiting =  np.zeros(pts_bits)
        return np.concatenate((first_positive, waiting, modulation))
    else:
        return modulation
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

if __name__ == "__main__":
    message = [1, 1, 0, 1, 0, 0, 1, 1, 1, 0]
    mod, c = psk_modulation(message, cyc=1)

    fig, (message_ax, cosine, modulated) = plt.subplots(3)
    
    message_signal = []
    for b in message:
        message_signal += [1 if b == 1 else -1] * (16384//(len(message)))
    
    message_ax.plot(message_signal)
    cosine.plot(c)
        
    modulated.plot(mod)
    

    plt.show()