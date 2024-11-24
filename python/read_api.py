from conf import Configuration
from demodulation_from_pitaya import Read_Pitaya
import numpy as np
import scipy.signal
from signal_processing.psk_modulation import bpsk_demodulation, butter_lowpass_filter

from typing import List

class Read_Api:
    def __init__(self, conf_file: str):
        self.configuration = Configuration(conf_file)
        self.configuration.load()

        if not self.configuration.check_all(['ip', 'channel', 'frequency', 'cyc', 'decimation', 'decison-device-threshold-percentage']):
            raise ValueError("Configuration file must contain 'ip', 'channel', 'frequency', 'cyc', 'decimation' and 'decison-device-threshold-percentage' keys")

        self.pitayaReader = Read_Pitaya(
            ip=self.configuration.get('ip'),
            dec=self.configuration.get('decimation'),
            trig_lvl=self.configuration.get('decison-device-threshold-percentage'),
        )

    def read_signal(self) -> List[np.ndarray]:
        data = self.pitayaReader.read()

        # Correlate the signal with the first sine as probing signal
        correlated = self.correlate_signal(data[75:140], data)

        # Normalize the signal
        normalized_correlated = correlated / np.max(correlated)

        demodulated = bpsk_demodulation(normalized_correlated, freq=self.configuration.get('cyc'))

        lpf = butter_lowpass_filter(demodulated, 5, 100, order=6)

        return normalized_correlated, demodulated, lpf
    
    def decision_making_device(self, lpf: np.ndarray) -> List[int]:
        integrals = self.compute_integrals(lpf)

        bits = []
        threshold = self.configuration.get('decison-device-threshold-percentage') * 19.5
        for integral in integrals:
            if integral > threshold:
                bits.append(1)
            elif integral < -threshold:
                bits.append(0)
        
        return bits
    
    def correlate_signal(self, probing: np.ndarray, signal: np.ndarray) -> np.ndarray:
        return scipy.signal.correlate(signal, probing, mode="full")
    
    def compute_integrals(self, lpf: np.ndarray) -> List[float]:
        integrals = []
        trig_x = 0
        for x in range(len(lpf)):
            if lpf[x] > self.configuration.get('decison-device-trigger'):
                trig_x = x
                break
        
        prev_x = 0
        for x in range(trig_x, len(lpf))[::39]:
            if prev_x != 0:
                integrals.append(scipy.integrate.simpson(lpf[prev_x:x], dx=1))
            
            prev_x = x
        
        return integrals