#!/usr/bin/env python3

"""
This file is meant to be running on local RedPitaya

If you want to run the software with a distant RedPitaya, use SCPI mode
"""

import numpy as np

import time

try:
    import rp
    from rp_overlay import overlay
except ModuleNotFoundError:
    import sys

    sys.path.append("/opt/redpitaya/lib/python")

    try:
        import rp
        from rp_overlay import overlay
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
    def __init__(self):
        rp.rp_Init()
        fpga = overlay()

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

        # rp.rp_Init()

        rp.rp_AcqReset()

        rp.rp_AcqSetDecimation(rp_dec)

        rp.rp_AcqSetTriggerLevel(rp.RP_T_CH_1, trig_lvl)
        print(trig_delay)
        rp.rp_AcqSetTriggerDelay(trig_delay)

        print("[*] Acquisition params set, ready to acquire")
        rp.rp_AcqStart()
        time.sleep(0.1)

        rp.rp_AcqSetTriggerSrc(acq_trig_src)
        time.sleep(0.1)

        # This is used to generate FROM OUTPUT not setting INPUT Setting
        # rp.rp_GenTriggerOnly(rp.RP_CH_1)  # Trigger generator

        # Trigger state
        print(rp.rp_AcqGetTriggerState()[1], rp.RP_TRIG_STATE_TRIGGERED)
        while 1:
            time.sleep(0.001)
            trig_state = rp.rp_AcqGetTriggerState()[1]
            # print(trig_state)
            if trig_state == rp.RP_TRIG_STATE_TRIGGERED:
                break

        print("[*] Triggered, waiting for buffer to fill")

        ## ! OS 2.00 or higher only ! ##
        # Fill state
        while 1:
            time.sleep(0.001)
            if rp.rp_AcqGetBufferFillState()[1]:
                break

        print("[*] Triggered, reading data")

        # ibuff = rp.i16Buffer(N)
        # rp.rp_AcqGetOldestDataRaw(rp.RP_CH_1, N, ibuff.cast())

        # Volts
        tp = rp.rp_AcqGetWritePointer()
        fbuff = rp.fBuffer(N)
        rp.rp_AcqGetDataV(rp.RP_CH_1, 0, N, fbuff)

        data_V = np.zeros(N, dtype=float)
        # data_raw = np.zeros(N, dtype = int)
        print(tp)
        for i in range(0, N, 1):
            data_V[i] = fbuff[(i + tp[1] + 1) % N]
            # data_raw[i] = ibuff[i]

        # Release resources
        # rp.rp_Release()
        rp.rp_AcqReset()

        return data_V

    def messageDaemon(self, dec, trig_lvl, trig_delay=8192):
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

        # rp.rp_Init()

        rp.rp_AcqReset()

        rp.rp_AcqSetDecimation(rp_dec)

        rp.rp_AcqSetTriggerLevel(rp.RP_T_CH_1, trig_lvl)
        print(trig_delay)
        rp.rp_AcqSetTriggerDelay(trig_delay)

        print("[*] Acquisition params set, ready to acquire")
        rp.rp_AcqStart()
        time.sleep(0.1)

        rp.rp_AcqSetTriggerSrc(acq_trig_src)
        time.sleep(0.1)

        # This is used to generate FROM OUTPUT not setting INPUT Setting
        rp.rp_GenTriggerOnly(rp.RP_CH_1)  # Trigger generator

        # Trigger state
        print(rp.rp_AcqGetTriggerState()[1], rp.RP_TRIG_STATE_TRIGGERED)
        while 1:
            time.sleep(0.001)
            trig_state = rp.rp_AcqGetTriggerState()[1]
            # print(trig_state)
            if trig_state == rp.RP_TRIG_STATE_TRIGGERED:
                break

        print("[*] Triggered, waiting for buffer to fill")

        ## ! OS 2.00 or higher only ! ##
        # Fill state
        while 1:
            time.sleep(0.001)
            if rp.rp_AcqGetBufferFillState()[1]:
                break

        print("[*] Triggered, reading data")

        # ibuff = rp.i16Buffer(N)
        # rp.rp_AcqGetOldestDataRaw(rp.RP_CH_1, N, ibuff.cast())

        # Volts
        tp = rp.rp_AcqGetWritePointer()
        fbuff = rp.fBuffer(N)
        rp.rp_AcqGetDataV(rp.RP_CH_1, 0, N, fbuff)

        data_V = np.zeros(N, dtype=float)
        # data_raw = np.zeros(N, dtype = int)
        print(tp)
        for i in range(0, N, 1):
            data_V[i] = fbuff[(i + tp[1] + 1) % N]
            # data_raw[i] = ibuff[i]

        # Release resources
        # rp.rp_Release()
        rp.rp_AcqReset()

        return data_V
