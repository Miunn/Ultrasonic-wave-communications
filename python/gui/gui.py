import tkinter as tk
from gui.guiGraph import GuiGraph
from gui.ctxMenu import CtxMenu
import gui.interactive.hub as ihub
from numpy import ndarray

from gui.communication_interface import CommunicationInterface


class Gui:
    root: tk.Tk
    graph: GuiGraph
    text: tk.Label
    errorRate: tk.DoubleVar
    menu: CtxMenu
    cid: int = 0
    interact: ihub.Hub

    def __init__(
        self, comm: CommunicationInterface = CommunicationInterface("0.0.0.0")
    ):
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
        self.interact.bind("<<changeGraph_f2>>", self.updateGraphFromResultF2)

    def updateGraphFromResultF2(self, event):
        self.setPlot(self.interact.f2.graphToUpdate)

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
