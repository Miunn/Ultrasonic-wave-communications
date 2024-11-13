#!/usr/bin/env python3

import sys
import pitaya.redpitaya_scpi as scpi
from signal_processing.psk_modulation import psk_modulation
import numpy as np
import matplotlib.pyplot as plt
IP = '10.42.0.125'
rp_s = scpi.scpi(IP)

if len(sys.argv) >= 2:
    if sys.argv[1] == 'stop':
        rp_s.tx_txt('OUTPUT1:STATE OFF')
        rp_s.close()
        sys.exit(0)

    if sys.argv[1] != 'sine':
        bits = [int(i) for i in sys.argv[1]]
        print(len(bits))
        mod = psk_modulation(bits, freq=5)
        print(len(mod))
        plt.plot(mod)

else:
    print("Provide a bit sequence as argument")
    sys.exit(1)


rp_s.tx_txt('GEN:RST')

if sys.argv[1] == 'sine':
    rp_s.sour_set(1, 'sine', 1, 300000, nor=2)
else:
    rp_s.sour_set(1, 'arbitrary', 1, 300000/(len(bits)*5), data=mod, burst=True)

rp_s.tx_txt('OUTPUT1:STATE ON')
rp_s.tx_txt('SOUR1:TRig:INT')


rp_s.close()

#plt.show()


"""
import numpy as np
import math
from matplotlib import pyplot as plt
import pitaya.redpitaya_scpi as scpi

IP = '169.254.93.192'
rp_s = scpi.scpi(IP)

wave_form = 'arbitrary'
freq = 2000
ampl = 1

N = 16384                   # Number of samples
t = np.linspace(0, 1, N)*2*math.pi

x = np.sin(t) + 1/3*np.sin(3*t)
y = 1/2*np.sin(t) + 1/4*np.sin(4*t)

plt.plot(t, x, t, y)
plt.title('Custom waveform')
#plt.show()


# Function for configuring a Source
rp_s.tx_txt('GEN:RST')
rp_s.sour_set(1, wave_form, ampl, freq, data= x)
rp_s.sour_set(2, wave_form, ampl, freq, data= y)

rp_s.tx_txt('OUTPUT1:STATE ON')
rp_s.tx_txt('SOUR1:TRig:INT')

rp_s.close()
"""

"""
#!/usr/bin/env python3

import sys
import pitaya.redpitaya_scpi as scpi

IP = "169.254.93.192"
rp_s = scpi.scpi(IP)

wave_form = 'sine'
freq = 2000
ampl = 1

rp_s.tx_txt('GEN:RST')

rp_s.tx_txt('SOUR1:FUNC ' + str(wave_form).upper())
rp_s.tx_txt('SOUR1:FREQ:FIX ' + str(freq))
rp_s.tx_txt('SOUR1:VOLT ' + str(ampl))

# Enable output
rp_s.tx_txt('OUTPUT1:STATE ON')
rp_s.tx_txt('SOUR1:TRig:INT')

rp_s.close()

"""

#!/usr/bin/env python3

"""
import sys
import pitaya.redpitaya_scpi as scpi

wave_form = 'sine'
freq = 2000
ampl = 1

IP = "169.254.93.192"
rp_s = scpi.scpi(IP)

rp_s.tx_txt('GEN:RST')

# Function for configuring a Source
rp_s.sour_set(1, wave_form, ampl, freq)

# Enable output
rp_s.tx_txt('OUTPUT1:STATE ON')
rp_s.tx_txt('SOUR1:TRig:INT')

rp_s.close()
"""