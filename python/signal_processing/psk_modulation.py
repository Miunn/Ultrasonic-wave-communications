from typing import List
import numpy as np
import sys

def psk_modulation(bits: List[int]):
    len_bits = len(bits)
    pts_bit = 1000
    linspace = np.linspace(0, len_bits, len_bits * pts_bit)

    c_t = np.cos(1 * 2 * np.pi * linspace + np.pi/2)

    # PSK Modulation
    modulated = np.zeros(len_bits * pts_bit)
    for i in range(len_bits):
        if bits[i] == 0:
            modulated[i * pts_bit:(i + 1) * pts_bit] = -1
        else:
            assert bits[i] == 1
            modulated[i * pts_bit:(i + 1) * pts_bit] = 1
    return modulated * c_t

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        bits = [int(i) for i in sys.argv[1]]
        mod = psk_modulation(bits)

        import matplotlib.pyplot as plt
        linspace = np.linspace(0, len(bits), len(bits) * 1000)
        plt.plot(linspace, mod)
        plt.show()