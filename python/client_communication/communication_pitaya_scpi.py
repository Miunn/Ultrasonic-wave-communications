import numpy as np
from gui.communication_interface import CommunicationInterface
from pitaya_communication.read_pitaya_scpi_api import Read_Pitaya_SCPI
from pitaya_communication.write_pitaya_scpi_api import Write_Pitaya_SCPI
from signal_processing.demodulation_api import DemodulationApi
from signal_processing.modulation_api import ModulationApi

from enum import StrEnum


class CommunicationMode(StrEnum):
    SCPI = "scpi"  # Use distant RedPitaya server to send and receive signals
    STANDALONE = "standalone"  # Run on local RedPitaya without gui
    DEFAULT = "default"  # Connect to distant standalone instance


class CommunicationPitayaSCPI(CommunicationInterface):
    demodulationMode: int

    last_graph: list[int, list, tuple[np.ndarray, str, str]]

    unknownErrors: int = 0
    ioron_frame_errors: int = 0
    encapsulated_frame_errors: int = 0
    valid_data: int = 0

    daemon_started: bool = False

    def __init__(self, addr):
        super().__init__(addr)

        self.readPitayaApi = Read_Pitaya_SCPI(addr)
        self.writePitayaApi = Write_Pitaya_SCPI(addr)

        self.demodulationApi = DemodulationApi()
        self.modulationApi = ModulationApi()

    def toggleMode(self, current):
        self.demodulationMode = current

    def connect(self, hub_frame):
        print("Trying to connect apis to pitaya")
        self.readPitayaApi.IP = self.addr
        self.writePitayaApi.IP = self.addr
        return self.readPitayaApi.connect() and self.writePitayaApi.connect()

    def emit(self, message, freq, cyc, mode=1):
        mod = self.modulationApi.modulate(message, cyc, mode=mode)
        self.writePitayaApi.write(
            mod,
            len(message),
            cyc,
            channel=1,
            wave_form="arbitrary",
            freq=freq,
            burst=True,
            mode=mode
        )
        return 0

    def startListening(
        self, freq, cyc, decimation, sig_trig, dec_trig, dec_thresh, mode=1
    ):
        data = self.readPitayaApi.read(decimation, sig_trig)

        if mode == 0:
            signal, demodulated, lpf, bits = self.demodulationApi.readData(
                data, freq, cyc, decimation, dec_trig, dec_thresh, sig_trig, mode=mode
            )

            return [
                0,
                bits,
                [
                    (signal, "#BBBBFF", "Signal"),
                    (demodulated, "orange", "Demodulation"),
                    (lpf, "green", "Low-pass filter"),
                ],
            ]

        elif mode == 1:
            signal, square_correlation, bits = self.demodulationApi.readData(
                data, freq, cyc, decimation, dec_trig, dec_thresh, sig_trig, mode=mode
            )

            return [
                0,
                bits,
                [
                    (signal, "#BBBBFF", "Signal"),
                    (square_correlation, "orange", "Correlation"),
                ],
            ]

    def readFromSignal(
        self,
        signal,
        freq: float,
        cyc: int,
        decimation: int,
        sig_trig: float,
        dec_trig: float,
        dec_thesh: float,
    ):
        return self.demodulationApi.readFromSignal(
            signal,
            freq,
            cyc,
            decimation,
            sig_trig,
            dec_trig,
            dec_thesh,
        )

    def emergencyStop(self):
        return super().emergencyStop()

    def start_daemon(self, freq, cyc, mode=1):
        self.daemon_started = True
        while self.daemon_started:
            # Generate a random message to send
            message = np.random.randint(0, 2, 10)

            # Send the message
            self.emit(message, freq, cyc, mode)

        return

    def stop_daemon(self):
        self.daemon_started = False
        return
