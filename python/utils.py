DECIMATION_TIME_SCALE = {
    1: 0.131072,
    8: 1.049,
    64: 8.389,
    1024: 134.218,
    8192: 1074,
    65536: 8590
}

def get_one_block_step(freq, cyc, dec):
    bloc_timing = cyc / freq
    decimation_time = DECIMATION_TIME_SCALE[dec]
    return decimation_time * 16384 / bloc_timing
