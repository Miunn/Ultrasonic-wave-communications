import threading
import numpy as np
import socketio
import traceback
import time

from pitaya_communication.read_pitaya_api import Read_Pitaya_API
from pitaya_communication.write_pitaya_api import Write_Pitaya_API
from gui.communication_interface import CommunicationInterface
from signal_processing.modulation_api import ModulationApi
from signal_processing.demodulation_api import DemodulationApi
from threading import Lock


class RedPitaya_Standalone:
    daemon_started: bool = False

    truePositive: int = 0
    falsePositive: int = 0
    trueNegative: int = 0
    falseNegative: int = 0

    error_bits: int = 0
    sent_bits: int = 0

    last_graph: list[tuple[np.ndarray, str, str]] = []
    last_message: np.ndarray = np.array([])
    last_error_state: int = 0

    demodulation_mode: int = 0
    frequency: float = 0
    cyc: int = 0
    trig_lvl: float = 0
    dec_trig: float = 0
    dec_thresh: float = 0

    t_daemon: threading.Thread = None

    ex: Lock

    def __init__(self):
        self.ex = Lock()
        self.server = socketio.Server()
        self.events()

        self.readPitayaApi = Read_Pitaya_API()
        self.writePitayaApi = Write_Pitaya_API()

        self.modulationApi = ModulationApi()
        self.demodulationApi = DemodulationApi()

    def getServerApp(self):
        return socketio.WSGIApp(self.server)

    def events(self):
        @self.server.event
        def connect(sid, environ, auth):
            print("connect ", sid)

        @self.server.event
        def disconnect(sid, reason):
            print("disconnect ", sid, reason)
            
        @self.server.on("get-daemon-status")
        def get_daemon_status(sid):
            return self.t_daemon is not None and self.t_daemon.is_alive() and self.daemon_started

        @self.server.on("play")
        def start_daemon(sid, data):
            if self.t_daemon is None or not self.t_daemon.is_alive():
                if self.t_daemon is not None:
                    self.t_daemon.join()
                self.t_daemon = threading.Thread(target=self.t_start_daemon)
                self.t_daemon.start()
                return True
            return False

        @self.server.on("pause")
        def stop_daemon(sid, data):
            if self.t_daemon is not None and self.t_daemon.is_alive():
                self.daemon_started = False
                self.t_daemon.join()
                return True

            return True

        @self.server.on("fetch-new-compared-data")
        def onFetchNewComparedData(sid, data):
            print("Fetch new compared data")
            return (
                self.truePositive,
                self.trueNegative,
                self.falsePositive,
                self.falseNegative,
                round((self.error_bits/self.sent_bits) * 100, 2) if self.sent_bits > 0 else 0,
            )

        @self.server.on("request-graph")
        def onRequestGraph(sid, data):
            print("Request graph")

            # Map ndarray graph inside last_graph to a list
            serializable_graph = []

            for graph in self.last_graph:
                serializable_graph.append((graph[0].tolist(), graph[1], graph[2]))

            return (
                self.last_error_state,
                self.last_message.tolist(),
                serializable_graph,
            )

        @self.server.on("change-parameters")
        def onChangeParameters(sid, data):
            print("[INFO] Change parameters to", data["data"])

            self.demodulation_mode = int(data["data"]["mode"])
            self.frequency = float(data["data"]["freq"])
            self.cyc = int(data["data"]["cyc"])
            self.trig_lvl = float(data["data"]["trig_lvl"])
            self.dec_trig = float(data["data"]["dec_trig"])
            self.dec_thresh = float(data["data"]["dec_thresh"])

            return 0

        @self.server.on("reset-stat")
        def resetStat(sid, data):
            print("Reset stat")
            self.truePositive = 0
            self.trueNegative = 0
            self.falsePositive = 0
            self.falseNegative = 0
            self.error_bits = 0
            self.sent_bits = 0
            return True

        @self.server.on("start-listening")
        def onStartListening(sid, data):
            if self.ex.acquire(True, 0.1):
                print("=========== START LISTENING =======")
                try:
                    signal = self.readPitayaApi.read(
                        data["decimation"], data["sig_trig"], trig_delay=8000
                    )
                    print("[INFO] Signal received, starting demodulation")

                    if data["mode"] == 0:
                        signal, demodulated, lpf, bits = (
                            self.demodulationApi.bpsk_demodulation(
                                signal,
                                data["freq"],
                                data["cyc"],
                                data["decimation"],
                                data["sig_trig"],
                                data["dec_trig"],
                                data["dec_thresh"],
                            )
                        )
                        self.ex.release()
                        return [
                            0,
                            bits,
                            [
                                (signal.tolist(), "#BBBBFF", "Signal"),
                                (demodulated.tolist(), "orange", "Demodulation"),
                                (lpf.tolist(), "green", "Low-pass filter"),
                            ],
                        ]

                    elif data["mode"] == 1:
                        signal, square_correlation, bits = (
                            self.demodulationApi.cross_correlation_demodulation(
                                signal,
                                data["freq"],
                                data["cyc"],
                                data["decimation"],
                                data["dec_thresh"],
                                data["sig_trig"],
                            )
                        )
                        self.ex.release()
                        return [
                            0,
                            bits,
                            [
                                (signal.tolist(), "#BBBBFF", "Signal"),
                                (square_correlation.tolist(), "orange", "Correlation"),
                            ],
                        ]
                except Exception as e:
                    print("[ERROR] ", e)
                    print(traceback.format_exc())
                    self.ex.release()
                    return [1, [], []]

        @self.server.on("write")
        def onWrite(sid, data):
            print("data", data)
            mod = self.modulationApi.modulate(
                data["message"], data["cyc"], mode=data["mode"]
            )
            try:
                self.writePitayaApi.write(
                    mod,
                    len(data["message"]),
                    data["cyc"],
                    channel=1,
                    wave_form="arbitrary",
                    freq=data["freq"],
                    volt=1,
                    burst=True,
                )
                print("[INFO] Signal sent")
                return 0
            except Exception as e:
                print("[ERROR] ", e)
                return 1

    def t_start_daemon(self):
        self.daemon_started = True
        print("[INFO] Daemon thread started")
        while self.daemon_started:
            # Generate a random message to send
            message = np.random.randint(0, 2, 16)

            # CAN encapsulation
            message = CommunicationInterface.encapsulate(message, "CAN")

            # Modulation
            modulated_message = self.modulationApi.modulate(
                message, self.cyc, self.demodulation_mode
            )

            # Set the buffer
            # self.writePitayaApi.prepareWriteDaemon(modulated_message, len(message), self.cyc, freq=self.frequency)

            # Start acquisition
            print(
                f"[INFO] Send {message} in CAN frame with trig_lvl: {self.trig_lvl} {type(self.trig_lvl)}"
            )
            signal = self.readPitayaApi.messageDaemon(
                8,
                self.trig_lvl,
                modulated_message,
                len(message),
                self.cyc,
                self.frequency,
                self.writePitayaApi,
                trig_delay=8000,
            )
            print("[INFO] Signal received :", signal)
            if self.demodulation_mode == 0:
                signal, demodulated, lpf, encoded_bits = (
                    self.demodulationApi.bpsk_demodulation()
                )
                self.last_error_state = 0
                self.last_graph = [
                    (signal, "#BBBBFF", "Signal"),
                    (demodulated, "orange", "Demodulation"),
                    (lpf, "green", "Low-pass filter"),
                ]
            else:
                signal, square_correlation, encoded_bits = (
                    self.demodulationApi.cross_correlation_demodulation(
                        signal,
                        self.frequency,
                        self.cyc,
                        8,
                        self.dec_thresh,
                        self.trig_lvl,
                    )
                )
                self.last_error_state = 0
                self.last_graph = [
                    (signal, "#BBBBFF", "Signal"),
                    (square_correlation, "orange", "Correlation"),
                ]
                
            encoded_bits = encoded_bits[:len(message)]

            try:
                print("Encoded bits:", encoded_bits)
                decoded_can_data = CommunicationInterface.decapsulate(
                    encoded_bits, "CAN"
                )
                print("Message encoded:", message)
                print("Encoded bits:", encoded_bits)
                tested = False
                for (i, b) in enumerate(message):
                    if b != encoded_bits[i]:
                        print("[ERROR] False positive")
                        self.falsePositive += 1
                        tested = True
                        break
                    
                if not tested:
                    print("[INFO] Message decoded successfully")
                    self.truePositive += 1
            except ValueError:
                tested = False
                for (i, b) in enumerate(message):
                    if b != encoded_bits[i]:
                        print("[ERROR] True negative")
                        self.trueNegative += 1
                        tested = True
                        break
                
                if not tested:
                    print("[ERROR] False negative")
                    self.falseNegative += 1
                    
            # Compute BEP
            for (i, b) in enumerate(message):
                if b != encoded_bits[i]:
                    self.error_bits += 1
            self.sent_bits += len(message)
            
            time.sleep(0.5)
