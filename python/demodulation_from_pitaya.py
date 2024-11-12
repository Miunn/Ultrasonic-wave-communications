#!/usr/bin/env python3

import sys
import pitaya.redpitaya_scpi as scpi
import matplotlib.pyplot as plot
import struct
from signal_processing.psk_modulation import bpsk_demodulation, butter_lowpass_filter, decision

IP = '10.42.0.125'

rp_s = scpi.scpi(IP)

rp_s.tx_txt('ACQ:RST')

dec = 1
trig_lvl = 0.4

# Function for configuring Acquisition
rp_s.acq_set(dec, trig_lvl, units='volts', sample_format='bin', trig_delay=8000)

rp_s.tx_txt('ACQ:START')
rp_s.tx_txt('ACQ:TRig CH1_PE')

while 1:
    rp_s.tx_txt('ACQ:TRig:STAT?')
    if rp_s.rx_txt() == 'TD':
        break

## ! OS 2.00 or higher only ! ##
while 1:
    rp_s.tx_txt('ACQ:TRig:FILL?')
    if rp_s.rx_txt() == '1':
        break


# function for Data Acquisition
buff = rp_s.acq_data(1, binary=True, convert=True)

#with open('pitayareadings-burst.bin', 'w') as f:
#    f.write(' '.join([str(f) for f in buff]))

print(buff)
import numpy as np
plot.plot(buff)

demodulated = bpsk_demodulation(buff, freq=5)
plot.plot(demodulated)

lpf = butter_lowpass_filter(demodulated, 3, 1000, order=3)

bits = decision(lpf)
print(''.join([str(i) for i in bits]))
        
plot.plot(lpf)

rp_s.close()

plot.ylabel('Voltage')
plot.show()