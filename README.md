# Ultrasonic communications applied to smart vehicules

These codes want to deliver a proof of concept about ultrasonic communications through metal plates for smart vehicules applications.

For this to work we use a RedPitaya coupled with an amplificator and a RaspberryPi for the display.

## RedPitaya documentation

- [Running C and Python applications](https://redpitaya.readthedocs.io/en/latest/appsFeatures/remoteControl/API_scripts.html)
- [Code examples](https://redpitaya.readthedocs.io/en/latest/appsFeatures/remoteControl/examples_top.html#examples)


## Structure

The project is divided into two main directories: `c` and `python`.

### C

The `c` directory contains the source code and headers for the CAN protocol and signal processing. The main files are:

- [can.c](c/src/can/can.c): Implements the CAN protocol.
- [psk_modulation.c](c/src/signal_processing/psk_modulation.c): Implements the PSK modulation for signal processing.
- [supportLib.c](c/src/signal_processing/supportLib.c): Provides a plotting libray for modulation and demodulation graphs.

### Python

The `python` directory contains Python scripts and Jupyter notebooks for signal processing and testing. The main files are:

- [redpitaya_scpi.py](python/pitaya/redpitaya_scpi.py): Implements the SCPI protocol for Red Pitaya.
- [test.py](python/pitaya/test.py): Tests the functionality of the Red Pitaya SCPI.
- [psk_modulation.py](python/signal_processing/psk_modulation.py): Implements the PSK modulation for signal processing.
- [PLP22INT01_jup.ipynb](python/PLP22INT01_jup.ipynb) and [PLP24INT41.ipynb](python/PLP24INT41.ipynb): Jupyter notebooks for the whole project.

## Building

To build the C code, navigate to the `c` directory and run `make` with a MAIN_FILE defined constant.

## Running Python Scripts

To run the Python scripts, navigate to the `python` directory and run `python3 script_name.py`.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.