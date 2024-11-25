import tkinter as tk
import threading
from guiGraph import GuiGraph
from ctxMenu import CtxMenu
import interactive.hub as ihub
import time
from numpy import ndarray

from communication_interface import CommunicationInterface


class Gui:
    root: tk.Tk
    graph: GuiGraph
    text: tk.Label
    errorRate: tk.DoubleVar
    menu: CtxMenu
    cid: int = 0
    interact: ihub.Hub

    def __init__(self, comm: CommunicationInterface):
        self.root = tk.Tk()

        self.menu = CtxMenu(self.root)

        self.root.config(menu=self.menu)

        self.root.rowconfigure(1, weight=1)

        self.errorRate = tk.DoubleVar()

        self.root.title("IOron visualizer")
        self.root.geometry("800x480")

        self.graph = GuiGraph(parent=self.root)
        self.graph.getTkWidget().grid(column=0, row=0)

        self.interact = ihub.Hub(self.root, comm)
        self.interact.grid(column=0, row=1, sticky="nswe")

        self.root.bind("<Configure>", self.onResize)
        self.menu.bind("<<toggleEvent>>", self.onToggle)

    def onToggle(self, event):
        print(event)
        self.graph.toggleGraph(event.x)

    def onResize(self, event):
        if event.widget != self.root:
            return
        self.graph.onResize(event.width)

    def setPlot(self, curves: list[tuple[list[float], str, str]]) -> None:
        self.graph.setPlot([it[0:2] for it in curves])

        self.menu.setGraphLayer([item[2] for item in curves])

    def setResult(self, value: ndarray):
        self.interact.setResult(value)

    def mainloop(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    with open("gui/signal-dec-64-work-voltage.bin", "r") as f:
        voltage = [float(n) for n in f.readline().split()]

    with open("gui/signal-dec-64-work-demod.bin", "r") as f:
        demod = [float(n) for n in f.readline().split()]

    with open("gui/signal-dec-64-work-lpf.bin", "r") as f:
        lpf = [float(n) for n in f.readline().split()]

    g = Gui(comm=CommunicationInterface())

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
