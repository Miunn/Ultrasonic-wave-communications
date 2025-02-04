#!/usr/bin/env python3

"""
This file is meant to be running on local RedPitaya

If you want to run the software with a distant RedPitaya, use SCPI mode
"""

import rp

from utils import get_signal_frequency_from_sampling

class Write_Pitaya_SCPI:
    def write(self, data, len_data, cyc, channel=1, wave_form='arbitrary', freq=250000, volt=1, burst=True):
        N = 16384
        
        rp_channel = rp.RP_CH_1
        
        if channel == 2:
            rp_channel = rp.RP_CH_2
        else:
            raise ValueError("Invalid channel")
        
        rp.rp_Init()
        rp.rp_GenReset()

        rp.rp_GenWaveform(rp_channel, wave_form)
        rp.rp_GenArbWaveform(rp_channel, data, N)
        if wave_form != 'arbitrary':
            rp.rp_GenFreqDirect(rp_channel, freq)
        else:
            rp.rp_GenFreqDirect(rp_channel, get_signal_frequency_from_sampling(freq, cyc, len_data))
        rp.rp_GenAmp(rp_channel, volt)
        
        rp.rp_GenTriggerSource(rp_channel, rp.RP_GEN_TRIG_SRC_INTERNAL)
        rp.rp_GenOutEnableSync(True)
        rp.rp_GenSynchronise()

        rp.rp_Release()
