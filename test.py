#!/usr/bin/env python3

import sys
import time
import redpitaya_scpi as scpi

IP = '10.42.0.200'
rp_s = scpi.scpi(IP)

print(sys.argv)
if (len(sys.argv) >= 2):
    led = int(sys.argv[1])
else:
    led = 0

print ("Blinking LED["+str(led)+"]")

period = 1 # seconds

while 1:
    time.sleep(period/2.0)
    rp_s.tx_txt('DIG:PIN LED' + str(led) + ',' + str(1))
    time.sleep(period/2.0)
    rp_s.tx_txt('DIG:PIN LED' + str(led) + ',' + str(0))

rp_s.close()