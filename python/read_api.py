from demodulation_from_pitaya import Read_Pitaya
import numpy as np
import scipy.signal
from signal_processing.psk_modulation import bpsk_demodulation
from utils import get_one_block_step

from typing import List, Tuple

from matplotlib import pyplot as plt


class Read_Api:
    def __init__(self, ip):
        self.pitayaReader = Read_Pitaya(ip)

    def connect(self):
        return self.pitayaReader.connect()

    def startListening(
        self, freq, cyc, decimation, sig_trig, dec_trig, dec_thesh, mode=1
    ):
        # normalized_correlated, demodulated, lpf = self.listenSignal(
        #    freq, decimation, sig_trig, cyc
        # )

        # step = int(get_one_block_step(freq, cyc, decimation))
        # integralSignal = scipy.signal.square(np.linspace(0, 1, 16384))

        # bits = self.decision_making_device(
        #    lpf, freq, cyc, decimation, dec_trig, dec_thesh
        # )

        # return normalized_correlated, demodulated, lpf, bits

        signal, square_correlate, bits = self.listenSignal(
            freq, decimation, sig_trig, cyc, dec_thesh
        )
        return signal, square_correlate, bits

    def listenSignal(self, freq, decimation, sig_trig, cyc, dec_thresh=0.5):
        print("Call listen signal with dec_thresh: ", dec_thresh)
        data = self.pitayaReader.read(decimation, sig_trig)
        return self.readData(data, freq, cyc, decimation, dec_thresh, sig_trig)

    def readData(
        self, data, freq, cyc, decimation, dec_thresh, sig_trig
    ) -> Tuple[np.ndarray, np.ndarray, List[int]]:
        print("Reading data with decition threshold: ", dec_thresh)
        (probe_sine, start_probing, end_probing) = self.get_probing_sine_from_signal(
            data, freq, cyc, decimation, sig_trig
        )

        maxs_graph = np.zeros(start_probing)
        bits = []
        correlation_samples = 17

        # Probing the probe (to tget the max)
        _, extremum_value_probe, _ = self.correlate_through_one_block(
            probe_sine,
            data,
            start_probing,
            end_probing,
            correlation_samples,
            start_probing,
            end_probing,
            0,
            plot=False,
        )

        maxs_graph = np.concatenate(
            (
                maxs_graph,
                [extremum_value_probe / extremum_value_probe]
                * (end_probing - start_probing),
            )
        )

        realign_offset = 0

        for i in range(1, len(data) // get_one_block_step(freq, cyc, decimation) - 2):
            block_start, block_end = self.get_block_indexes(
                data, sig_trig, freq, cyc, decimation, i
            )

            block_start -= realign_offset
            block_end -= realign_offset

            correlation_points, extremum_value, extremum_index = (
                self.correlate_through_one_block(
                    probe_sine,
                    data,
                    block_start,
                    block_end,
                    correlation_samples,
                    start_probing,
                    end_probing,
                    extremum_value_probe,
                    plot=False,
                )
            )
            # avg = np.mean(correlation_points)

            if extremum_index != correlation_samples // 2 and i != 1:
                print(
                    f"[{i} ({block_start}-{block_end})] Extremum found at index {extremum_index}, realign by {extremum_index - correlation_samples // 2}"
                )
                realign_offset += extremum_index - correlation_samples // 2

            extremum_value = extremum_value / extremum_value_probe

            if extremum_value > 1:
                extremum_value = 1
            elif extremum_value < -1:
                extremum_value = -1

            maxs_graph = np.concatenate(
                (maxs_graph, [extremum_value] * (block_end - block_start))
            )

            # Decision making device
            if i != 1:
                if extremum_value > dec_thresh:
                    bits.append(1)
                elif extremum_value < -dec_thresh:
                    bits.append(0)

        # self.correlate_in_new_graph(data, freq, cyc, decimation, sig_trig)

        # Correlate the signal with the first sine as probing signal
        # correlated = self.correlate_signal(data[75:140], data)

        # Normalize the signal
        # normalized_correlated = correlated / np.max(correlated)
        # normalized_correlated = data / np.max(data)
        # demodulated = bpsk_demodulation(normalized_correlated, freq, decimation)

        # lpf = butter_lowpass_filter(demodulated, 5, 100, order=6)

        """with open("sig-dec-64-voltage.txt", "w") as f:
            f.write(" ".join([str(i) for i in normalized_correlated]))

        with open("sig-dec-64-demod.txt", "w") as f:
            f.write(" ".join([str(i) for i in demodulated]))

        with open("sig-dec-64-lpf.txt", "w") as f:
            f.write(" ".join([str(i) for i in lpf]))"""

        # return normalized_correlated, demodulated, lpf
        return data, maxs_graph, bits

    def readFromSignal(
        self,
        signal: np.ndarray,
        freq: int,
        cyc: int,
        decimation: int,
        dec_thresh: float,
        sig_trig: float = 0.6,
    ) -> np.ndarray:
        """(probe_sine, start, end) = self.get_probing_sine_from_signal(signal, freq, cyc, decimation, sig_trig)



        #bad_correlation = self.correlate_signal(probe_sine, signal[end:end+get_one_block_step(freq, cyc, decimation)])
        one_correlation = self.correlate_signal(probe_sine, signal[end+get_one_block_step(freq, cyc, decimation):end+get_one_block_step(freq, cyc, decimation)*2])
        zero_correlation = self.correlate_signal(probe_sine, signal[end+get_one_block_step(freq, cyc, decimation)*2:end+get_one_block_step(freq, cyc, decimation)*3])
        slide_correlation = self.sliding_correlation(probe_sine, signal[end+get_one_block_step(freq, cyc, decimation):], freq, cyc, decimation)

        fig, (base, one, zero, full, demod) = plt.subplots(5)

        base.plot(signal)
        #bad.plot(bad_correlation)
        one.plot(one_correlation)
        zero.plot(zero_correlation)
        full.plot(slide_correlation)
        full.set_yticks([-6.5,0,6.5])
        full.grid(axis="y")

        demodulation = bpsk_demodulation(slide_correlation, freq, decimation)
        demod.plot(signal[end+get_one_block_step(freq, cyc, decimation):])
        demod.plot(demodulation/max(demodulation))

        plt.show()"""

        """return [
            0,
            "101111",
            [
                (signal, "#BBBBFF", "Voltage"),
                (demodulation, "#FFBB99", "Demodulated"),
            ],
        ]"""
        data, maxs_graph, bits = self.readData(
            signal, freq, cyc, decimation, dec_thresh, sig_trig
        )
        print("Bits: ", bits)
        return [
            0,
            "".join([str(i) for i in bits]),
            [
                (data, "#BBBBFF", "Voltage"),
                (maxs_graph, "#FFBB99", "Correlation"),
            ],
        ]

    def correlate_in_new_graph(
        self,
        signal: np.ndarray,
        freq: int,
        cyc: int,
        decimation: int,
        sig_trig: float = 0.2,
    ) -> np.ndarray:
        (probe_sine, start, end) = self.get_probing_sine_from_signal(
            signal, freq, cyc, decimation, sig_trig
        )

        # bad_correlation = self.correlate_signal(probe_sine, signal[end:end+get_one_block_step(freq, cyc, decimation)])
        one_correlation = self.correlate_signal(
            probe_sine,
            signal[
                end + get_one_block_step(freq, cyc, decimation) : end
                + get_one_block_step(freq, cyc, decimation) * 2
            ],
        )
        zero_correlation = self.correlate_signal(
            probe_sine,
            signal[
                end + get_one_block_step(freq, cyc, decimation) * 2 : end
                + get_one_block_step(freq, cyc, decimation) * 3
            ],
        )
        slide_correlation = self.sliding_correlation(
            probe_sine,
            signal[end + get_one_block_step(freq, cyc, decimation) :],
            freq,
            cyc,
            decimation,
        )

        fig, (base, one, zero, full, demod) = plt.subplots(5)

        base.plot(signal)
        # bad.plot(bad_correlation)
        one.plot(one_correlation)
        zero.plot(zero_correlation)
        full.plot(slide_correlation)
        full.set_yticks([-6.5, 0, 6.5])
        full.grid(axis="y")

        demodulation = bpsk_demodulation(slide_correlation, freq, decimation)
        demod.plot(signal[end + get_one_block_step(freq, cyc, decimation) :])
        demod.plot(demodulation / max(demodulation))

        plt.show()

    @staticmethod
    def get_probing_sine_from_signal(
        signal: np.ndarray,
        freq: float,
        cyc: int,
        decimation: int,
        threshold: float = 0.2,
    ) -> tuple[np.ndarray, int, int]:
        print(
            "Probing for frequency: ", freq, " cyc: ", cyc, " decimation: ", decimation
        )
        for i in range(0, len(signal)):
            if signal[i] > threshold:
                print(
                    "Trigger at: ",
                    i,
                    " one block step: ",
                    get_one_block_step(freq, cyc, decimation),
                )
                return (
                    signal[i : i + get_one_block_step(freq, cyc, decimation)],
                    i,
                    i + get_one_block_step(freq, cyc, decimation),
                )

        return (np.zeros(0), 0, 0)

    def decision_making_device(
        self, lpf: np.ndarray, freq, cyc, decimation, dec_trig, dec_thresh
    ) -> List[int]:
        integrals = self.compute_integrals(lpf, freq, cyc, decimation, dec_trig)

        bits = []
        threshold = dec_thresh * get_one_block_step(freq, cyc, decimation) * 0.5
        print(f"Threshold: {threshold}")
        for integral in integrals:
            if integral > threshold:
                bits.append(1)
            elif integral < -threshold:
                bits.append(0)

        return bits

    @staticmethod
    def correlate_signal(probing: np.ndarray, signal: np.ndarray) -> np.ndarray:
        return scipy.signal.correlate(signal, probing, mode="full")

    @staticmethod
    def slide_correlate_through_one_block(
        probing: np.ndarray, signal: np.ndarray, start_block_index, end_block_index
    ) -> np.ndarray:
        if start_block_index > end_block_index:
            print(
                "Slide correlate through one block: start block index is greater than end block index"
            )
            return np.zeros(0)

        if start_block_index < len(probing):
            print(
                "Slide correlate through one block: start block index is less than probing length"
            )
            return np.zeros(0)

        if end_block_index > len(signal) - len(probing):
            print(
                "Slide correlate through one block: end block index doesn't leave enough space for probing"
            )
            return np.zeros(0)

        fig, (signal_plot, correlation_graph) = plt.subplots(2)
        signal_plot.plot(signal)
        signal_plot.axvline(start_block_index, color="r")
        signal_plot.axvline(end_block_index, color="r")
        graph = np.empty(0)
        for i in range(1, end_block_index - start_block_index):
            correlation = Read_Api.correlate_signal(
                probing[len(probing) - i :],
                signal[start_block_index : start_block_index + i],
            )

            center_value = correlation[int(len(correlation) // 2)]

            graph = np.concatenate((graph, [center_value]))

        print("Plotting correlation plot for one block")
        correlation_graph.plot(graph)
        plt.show()
        return graph

    @staticmethod
    def correlate_through_one_block(
        probing: np.ndarray,
        signal: np.ndarray,
        start_block_index,
        end_block_index,
        samples,
        start_probing,
        end_probing,
        extremum_probe,
        plot=False,
    ) -> np.ndarray:
        if start_block_index > end_block_index:
            print(
                "Slide correlate through one block: start block index is greater than end block index"
            )
            return np.zeros(0)

        """if start_block_index < len(probing):
            print("Slide correlate through one block: start block index is less than probing length")
            return np.zeros(0)"""

        """if end_block_index > len(signal) - len(probing):
            print("Slide correlate through one block: end block index doesn't leave enough space for probing")
            return np.zeros(0)"""

        graph = np.empty(0)
        for i in range(
            -samples // 2 + 1, min(samples // 2 + 1, len(signal) - len(probing))
        ):
            correlation = Read_Api.correlate_signal(
                probing,
                signal[start_block_index - i : start_block_index - i + len(probing)],
            )
            center_value = correlation[int(len(correlation) // 2)]
            graph = np.concatenate((graph, [center_value]))

        # +/- Max
        max_ = np.max(np.abs(graph))

        # Extremum value (max without abs)
        extremum_value = graph[np.where(np.abs(graph) == max_)[0][0]]

        print(
            f"[{start_block_index}, {end_block_index}] Extremum index: {np.where(np.abs(graph) == max_)[0][0]} Extremum: {extremum_value} Extremum probe: {extremum_probe}"
        )

        if plot:
            fig, (signal_plot, correlation_graph) = plt.subplots(2)
            signal_plot.plot(signal)
            signal_plot.axvline(start_probing, color="g")
            signal_plot.axvline(end_probing, color="g")
            signal_plot.axvline(start_block_index, color="r")
            signal_plot.axvline(end_block_index, color="r")
            correlation_graph.plot(graph)
            plt.show()
        return graph, extremum_value, np.where(np.abs(graph) == max_)[0][0]

    @staticmethod
    def realign_signal(
        signal: np.ndarray, correlation: np.ndarray, start: int, end: int
    ):
        return

    @staticmethod
    def get_block_indexes(signal, trigger, freq, cyc, decimation, index):
        block_length = get_one_block_step(freq, cyc, decimation)

        start = 0
        for i in range(len(signal)):
            if signal[i] > trigger:
                start = i
                break

        return (
            start + (block_length * index),
            start + (block_length * index) + block_length,
        )

    def compute_integrals(
        self, lpf: np.ndarray, freq, cyc, decimation, dec_trig
    ) -> List[float]:
        integrals = []
        trig_x = 0
        for x in range(len(lpf)):
            if lpf[x] > dec_trig:
                trig_x = x
                break

        prev_x = 0
        step = int(get_one_block_step(freq, cyc, decimation))
        for x in range(trig_x, len(lpf))[::step]:
            if prev_x != 0:
                integrals.append(scipy.integrate.simpson(lpf[prev_x:x], dx=1))

            prev_x = x

        return integrals
