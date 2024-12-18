DECIMATION_TIME_SCALE = {
    1: 0.131072,
    8: 1.049,
    64: 8.389,
    1024: 134.218,
    8192: 1074,
    65536: 8590
}

DECIMATION_SAMPLING_RATE = {
    1: 125000000,
    8: 15600000,
    64: 1953000,
    1024: 122070,
    8192: 15258,
    65536: 1907
}

def get_signal_frequency_from_sampling(freq, cyc, nb_bits):
    return freq / cyc / nb_bits

def get_sampling_signal_frequency(freq, decimation):
    return freq / DECIMATION_SAMPLING_RATE[decimation]

def get_one_block_step(freq, cyc, dec):
    bloc_timing = cyc / (freq/1000)
    decimation_time = DECIMATION_TIME_SCALE[dec]
    return 16384 * bloc_timing / decimation_time