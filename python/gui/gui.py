from os import walk
import tkinter as tk
from tkinter import filedialog

from PIL import Image, ImageTk
from gui.guiGraph import GuiGraph
from gui.ctxMenu import CtxMenu
import gui.interactive.hub as ihub
from numpy import ndarray
from classifiedjson import dumps, load
from datetime import datetime

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
        self.menu.bind("<<FOURIER>>", self.onAskFourrier)
        self.menu.bind("<<SAVE>>", self.onSave)
        self.menu.bind("<<LOAD>>", self.onLoad)
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
        self.graph.setPlot(curves)

        self.menu.setGraphLayer([item[2] for item in curves])

    def setResult(self, value: ndarray):
        self.interact.setResult(value)

    def mainloop(self) -> None:
        self.root.mainloop()

    def onAskFourrier(self, event) -> None:
        index = self.interact.index(self.interact.select())
        print(index)
        if index == 1:
            deci = self.interact.f2.getDecim()
        else:
            deci = 64
        self.graph.generateFourier(deci)

    def onSave(self, event) -> None:
        t = datetime.today().__str__().replace(" ", "_").replace(":", "-").split(".")[0]
        f = filedialog.asksaveasfilename(
            defaultextension=".iro",
            initialfile="ioron_" + t + ".iro",
            filetypes=[("IOron saves", ".iro"), ("all files", "*")],
        )
        if f != "":
            serial_data = dumps(self.graph.plot_array)
            with open(f, "w") as file:
                file.write(serial_data)

    def onLoad(self, event) -> None:
        f = filedialog.askopenfilename()
        if f != "":
            with open(f, "r") as file:
                try:
                    data = load(file)
                except:
                    self.tl_load_error()
                    return

            if type(data) is not list:
                self.tl_load_error()
                return
            for item in data:
                if type(item) is not tuple:
                    self.tl_load_error()
                    return
                if (
                    type(item[0]) is not list
                    or type(item[1]) is not str
                    or type(item[2]) is not str
                ):
                    self.tl_load_error()
                    return
            self.setPlot(data)
            print("ok")

    def tl_load_error(self):
        tl = tk.Toplevel(self.root)
        tl.title("IOron visualizer - Error")
        tl.geometry("400x100")
        img = Image.open("gui/err.png")
        c = ImageTk.PhotoImage(img.resize((75, 75)))
        d = tk.Label(tl, image=c)
        d.grid(sticky="", row=0, column=0)
        label = tk.Label(
            tl,
            text="Error during loading of the file :\nFile malformed or not an IOron graph.",
            justify="left",
        )
        label.grid(row=0, column=1)
        tl.columnconfigure(1, weight=1)
        tl.columnconfigure(0, weight=1)
        tl.rowconfigure(0, weight=1)

        tl.mainloop()
