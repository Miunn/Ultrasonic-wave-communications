import threading
from gui.gui import Gui


if __name__ == "__main__":
    with open("gui/signal-dec-64-work-voltage.bin", "r") as f:
        voltage = [float(n) for n in f.readline().split()]

    with open("gui/signal-dec-64-work-demod.bin", "r") as f:
        demod = [float(n) for n in f.readline().split()]

    with open("gui/signal-dec-64-work-lpf.bin", "r") as f:
        lpf = [float(n) for n in f.readline().split()]

    g = Gui()

    threading.Thread(
        target=lambda: g.setPlot(
            [
                (voltage, "#BBBBFF", "Voltage"),
                (demod, "#FFBB99", "Demodulation"),
                (lpf, "red", "Low-pass filter"),
            ]
        )
    ).start()
    g.mainloop()
