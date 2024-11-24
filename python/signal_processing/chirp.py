import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import chirp
from scipy.signal.windows import tukey

f_ech = 125*10**6

t=np.arange (0,2**14*1/f_ech, 1/f_ech)
Amp = 0.9
#chirp creation 
sig_fen = chirp (t, f0=1e5,f1=2e6, t1=t[len(t)-1], method='linear')
sig_fen= sig_fen*tukey(len (t),0.10)

plt.plot (t, Amp*sig_fen)
plt.show()