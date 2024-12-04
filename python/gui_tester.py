import threading
from gui.gui import Gui
from gui.communication_interface import CommunicationInterface


if __name__ == "__main__":
    g = Gui(CommunicationInterface("10.5.0.0"))

    with open("python/gui/signal-dec-64-work-voltage.bin", "r") as f:
        d = [float(i) for i in f.read().split(" ")]

    g.setPlot([(d, "#0000FF99", "a")])
    g.mainloop()
