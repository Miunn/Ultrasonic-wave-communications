#!/usr/bin/env python3

"""
This file is meant to be running on local RedPitaya

If you want to run the software with a distant RedPitaya, use SCPI mode
"""

import numpy as np

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

class Read_Pitaya_API:
    def read(self, dec, trig_lvl, trig_delay=8192):
        N = 16384
        rp_dec = None
        
        if dec == 1:
            rp_dec = rp.RP_DEC_1
        elif dec == 8:
            rp_dec = rp.RP_DEC_8
        elif dec == 64:
            rp_dec = rp.RP_DEC_64
        elif dec == 1024:
            rp_dec = rp.RP_DEC_1024
        
        acq_trig_src = rp.RP_TRIG_SRC_CHA_PE
        
        rp.rp_Init()

        rp.rp_AcqReset()
        
        rp.rp_AcqSetDecimation(rp_dec)

        rp.rp_AcqSetTriggerLevel(rp.RP_T_CH_1, trig_lvl)
        rp.rp_AcqSetTriggerDelay(trig_delay)
        
        print("[*] Acquisition params set, ready to acquire")
        rp.rp_AcqStart()
        
        rp.rp_AcqSetTriggerSrc(acq_trig_src)

        rp.rp_GenTriggerOnly(rp.RP_CH_1)       # Trigger generator

        # Trigger state
        while 1:
            trig_state = rp.rp_AcqGetTriggerState()[1]
            if trig_state == rp.RP_TRIG_STATE_TRIGGERED:
                break

        ## ! OS 2.00 or higher only ! ##
        # Fill state
        while 1:
            if rp.rp_AcqGetBufferFillState()[1]:
                break
            
        ibuff = rp.i16Buffer(N)
        rp.rp_AcqGetOldestDataRaw(rp.RP_CH_1, N, ibuff.cast())

        # Volts
        fbuff = rp.fBuffer(N)
        rp.rp_AcqGetDataV(rp.RP_CH_1, 0, N, fbuff)

        data_V = np.zeros(N, dtype = float)
        #data_raw = np.zeros(N, dtype = int)

        for i in range(0, N, 1):
            data_V[i] = fbuff[i]
            #data_raw[i] = ibuff[i]

        # Release resources
        rp.rp_Release()
        
        return data_V