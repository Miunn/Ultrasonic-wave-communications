import numpy as np
import socketio
import traceback

try:
    import rp
except ModuleNotFoundError:
    import sys

from pitaya_communication.read_pitaya_api import Read_Pitaya_API
from pitaya_communication.write_pitaya_api import Write_Pitaya_API
from signal_processing.modulation_api import ModulationApi
from signal_processing.demodulation_api import DemodulationApi
from threading import Lock


class RedPitaya_Standalone:
    unknownErrors: int = 0
    ioron_frame_errors: int = 0
    encapsulated_frame_errors: int = 0
    valid_data: int = 0

    last_graph: list[tuple[np.ndarray, str, str]] = []
    last_message: np.ndarray = np.array([])
    ex: Lock

    def __init__(self):
        rp.rp_Init()
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

        @self.server.on("fetch-new-compared-data")
        def onFetchNewComparedData(sid, data):
            print("Fetch new compared data")
            return (
                self.unknownErrors,
                self.ioron_frame_errors,
                self.encapsulated_frame_errors,
                self.valid_data,
            )

        @self.server.on("request-graph")
        def onRequestGraph(sid, data):
            print("Request graph")

            # Map ndarray graph inside last_graph to a list
            serializable_graph = []

            for graph in self.last_graph:
                serializable_graph.append((graph[0].tolist(), graph[1], graph[2]))

            return (self.last_message.tolist(), serializable_graph)

        @self.server.on("change-parameters")
        def onChangeParameters(sid, data):
            print("Change parameters")
            print(data)
            return 0

        @self.server.on("start-listening")
        def onStartListening(sid, data):
            if self.ex.acquire(True, 0.1):
                print("=========== START LISTENING =======")
                try:
                    signal = self.readPitayaApi.read(
                        data["decimation"], data["sig_trig"], trig_delay=8192
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

    def start_daemon():
        return
