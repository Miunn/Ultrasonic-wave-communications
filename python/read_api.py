from conf import Configuration
from demodulation_from_pitaya import Read_Pitaya
from gui.communication_interface import CommunicationInterface
import numpy as np
import scipy.signal
from signal_processing.psk_modulation import bpsk_demodulation, butter_lowpass_filter
from utils import get_one_block_step

from typing import List

class Read_Api:
    def __init__(self, ip):
        self.pitayaReader = Read_Pitaya(ip)

    def startListening(self, freq, cyc, decimation, sig_trig, dec_trig, dec_thesh):
        normalized_correlated, demodulated, lpf = self.listenSignal(freq, decimation, sig_trig)

        bits = self.decision_making_device(lpf, freq, cyc, decimation, dec_trig, dec_thesh)
        
        return normalized_correlated, demodulated, lpf, bits

    def listenSignal(self, freq, decimation, sig_trig):
        data = self.pitayaReader.read(decimation, sig_trig)

        # Correlate the signal with the first sine as probing signal
        correlated = self.correlate_signal(data[75:140], data)

        # Normalize the signal
        normalized_correlated = correlated / np.max(correlated)

        demodulated = bpsk_demodulation(normalized_correlated, freq, decimation)

        lpf = butter_lowpass_filter(demodulated, 5, 100, order=6)

        return normalized_correlated, demodulated, lpf
    
    def decision_making_device(self, lpf: np.ndarray, freq, cyc, decimation, dec_trig, dec_thresh) -> List[int]:
        integrals = self.compute_integrals(lpf, freq, cyc, decimation, dec_trig)

        bits = []
        threshold = dec_thresh * 19.5
        for integral in integrals:
            if integral > threshold:
                bits.append(1)
            elif integral < -threshold:
                bits.append(0)
        
        return bits
    
    def correlate_signal(self, probing: np.ndarray, signal: np.ndarray) -> np.ndarray:
        return scipy.signal.correlate(signal, probing, mode="full")
    
    def compute_integrals(self, lpf: np.ndarray, freq, cyc, decimation, dec_trig) -> List[float]:
        integrals = []
        trig_x = 0
        for x in range(len(lpf)):
            if lpf[x] > dec_trig:
                trig_x = x
                break
        
        prev_x = 0
        step = get_one_block_step(freq, cyc, decimation)
        for x in range(trig_x, len(lpf))[::step]:
            if prev_x != 0:
                integrals.append(scipy.integrate.simpson(lpf[prev_x:x], dx=1))
            
            prev_x = x
        
        return integrals