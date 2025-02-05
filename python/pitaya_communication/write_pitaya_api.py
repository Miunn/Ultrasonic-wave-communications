#!/usr/bin/env python3

"""
This file is meant to be running on local RedPitaya

If you want to run the software with a distant RedPitaya, use SCPI mode
"""

try:
    import rp
except ModuleNotFoundError:
    import sys
    sys.path.append('/opt/redpitaya/lib/python')
    
    try:
        import rp
    except ModuleNotFoundError:
        print(
"""
Couldn't found rp library, you are most likely not running this program on a RedPitaya.
If you want to connect a distant RedPitaya, use SCPI mode.

If you are running this program on a RedPitaya, make sure you have the rp library installed in /opt/redpitaya/lib/python or located next to these sources.
"""
        )
        exit(1)

from utils import get_signal_frequency_from_sampling

class Write_Pitaya_API:
    def write(self, data, len_data, cyc, channel=1, wave_form='arbitrary', freq=250000, volt=1, burst=True):
        print(f"[INFO] Start write data: {data} with len: {len_data, len(data)} cyc: {cyc}, channel: {channel}, wave_form: {wave_form}, freq: {freq}, volt: {volt}, burst: {burst}")
        N = 16384
        print("creating buffer")
        d = rp.arbBuffer(N)
        print("buffer created")
        
        rp_channel = rp.RP_CH_1
        if channel == 1:
            rp_channel = rp.RP_CH_1
        elif channel == 2:
            rp_channel = rp.RP_CH_2
        else:
            raise ValueError("Invalid channel")
        
        rp_waveform = rp.RP_WAVEFORM_ARBITRARY
        if wave_form == 'arbitrary':
            rp_waveform = rp.RP_WAVEFORM_ARBITRARY
        elif wave_form == 'sine':
            rp_waveform = rp.RP_WAVEFORM_SINE
            
        for i in range(N):
            if i < len(data):
                d[i] = float(data[i])
            else:
                d[i] = 0
        
        rp.rp_Init()
        rp.rp_GenReset()

        rp.rp_GenWaveform(rp_channel, rp_waveform)
        rp.rp_GenArbWaveform(rp_channel, d.cast(), N)
        if wave_form != 'arbitrary':
            rp.rp_GenFreqDirect(rp_channel, freq)
        else:
            rp.rp_GenFreqDirect(rp_channel, get_signal_frequency_from_sampling(freq, cyc, len_data))
        rp.rp_GenAmp(rp_channel, volt)

        rp.rp_GenTriggerSource(rp_channel, rp.RP_GEN_TRIG_SRC_INTERNAL)
        
        if burst:
            rp.rp_GenMode(rp_channel, rp.RP_GEN_MODE_BURST)
            rp.rp_GenBurstCount(rp_channel, 1)                   # Ncyc
            rp.rp_GenBurstRepetitions(rp_channel, 2)             # Nor
            rp.rp_GenBurstPeriod(rp_channel, 0)                    # Period
        
        rp.rp_GenOutEnable(rp_channel)
        rp.rp_GenTriggerOnly(rp_channel)


        rp.rp_Release()
        print("SIGNAL RELEASED")
