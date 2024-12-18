from conf import Configuration
from demodulation_from_pitaya import Read_Pitaya
import numpy as np
import scipy.signal
from signal_processing.psk_modulation import bpsk_demodulation, butter_lowpass_filter
from utils import get_one_block_step

from typing import List


class Read_Api:
    def __init__(self, ip):
        self.pitayaReader = Read_Pitaya(ip)

    def startListening(self, freq, cyc, decimation, sig_trig, dec_trig, dec_thesh):
        normalized_correlated, demodulated, lpf = self.listenSignal(
            freq, decimation, sig_trig
        )

        # step = int(get_one_block_step(freq, cyc, decimation))
        # integralSignal = scipy.signal.square(np.linspace(0, 1, 16384))

        bits = self.decision_making_device(
            lpf, freq, cyc, decimation, dec_trig, dec_thesh
        )

        return normalized_correlated, demodulated, lpf, bits

    def listenSignal(self, freq, decimation, sig_trig):
        data = self.pitayaReader.read(decimation, sig_trig)

        # Correlate the signal with the first sine as probing signal
        # correlated = self.correlate_signal(data[75:140], data)

        # Normalize the signal
        # normalized_correlated = correlated / np.max(correlated)
        normalized_correlated = data / np.max(data)
        demodulated = bpsk_demodulation(normalized_correlated, freq, decimation)

        lpf = butter_lowpass_filter(demodulated, 5, 100, order=6)

        with open("sig-dec-64-voltage.txt", "w") as f:
            f.write(" ".join([str(i) for i in normalized_correlated]))

        with open("sig-dec-64-demod.txt", "w") as f:
            f.write(" ".join([str(i) for i in demodulated]))

        with open("sig-dec-64-lpf.txt", "w") as f:
            f.write(" ".join([str(i) for i in lpf]))

        return normalized_correlated, demodulated, lpf

    def get_probing_sine_from_signal(self, signal: np.ndarray) -> np.ndarray:
        # TODO
        return np.zeros(0)

    def decision_making_device(
        self, lpf: np.ndarray, freq, cyc, decimation, dec_trig, dec_thresh
    ) -> List[int]:
        integrals = self.compute_integrals(lpf, freq, cyc, decimation, dec_trig)

        bits = []
        threshold = dec_thresh * 19.5
        print(f"Threshold: {threshold}")
        for integral in integrals:
            if integral > threshold:
                bits.append(1)
            elif integral < -threshold:
                bits.append(0)

        return bits

    def correlate_signal(self, probing: np.ndarray, signal: np.ndarray) -> np.ndarray:
        return scipy.signal.correlate(signal, probing, mode="full")

    def compute_integrals(
        self, lpf: np.ndarray, freq, cyc, decimation, dec_trig
    ) -> List[float]:
        integrals = []
        trig_x = 0
        for x in range(len(lpf)):
            if lpf[x] > dec_trig:
                trig_x = x
                break

        prev_x = 0
        step = int(get_one_block_step(freq, cyc, decimation))
        for x in range(trig_x, len(lpf))[::step]:
            if prev_x != 0:
                integrals.append(scipy.integrate.simpson(lpf[prev_x:x], dx=1))

            prev_x = x

        return integrals

