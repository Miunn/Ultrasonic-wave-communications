#!/usr/bin/env python3

import pitaya.redpitaya_scpi as scpi

class Read_Pitaya:
    IP = '10.42.0.125'
    rp_s: scpi.scpi

    def __init__(self, ip='10.42.0.125'):
        self.IP = ip

    def connect(self):
        try:
            self.rp_s = scpi.scpi(self.IP, timeout=10)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def close(self):
        self.rp_s.close()

    def tx_txt(self, txt):
        self.rp_s.tx_txt(txt)

    def rx_txt(self):
        return self.rp_s.rx_txt()
    
    def acq_set(self, dec, trig_lvl, units='volts', sample_format='bin', trig_delay=8192):
        self.rp_s.acq_set(dec, trig_lvl, units=units, sample_format=sample_format, trig_delay=trig_delay)

    def acq_data(self, channel, binary=True, convert=True):
        return self.rp_s.acq_data(channel, binary=binary, convert=convert)

    def read(self, dec, trig_lvl):
        self.tx_txt('ACQ:RST')
        self.acq_set(dec, trig_lvl, units='volts', sample_format='bin', trig_delay=8100)
        self.tx_txt('ACQ:START')
        self.tx_txt('ACQ:TRig CH1_PE')
        print("[*] Acquisition params set, ready to acquire")

        while 1:
            self.tx_txt('ACQ:TRig:STAT?')
            if self.rx_txt() == 'TD':
                break

        while 1:
            self.tx_txt('ACQ:TRig:FILL?')
            if self.rx_txt() == '1':
                break

        print("[*] Triggered, acquire buffer")
        buff = self.acq_data(1, binary=True, convert=True)

        return buff