import tkinter as tk
from tkinter import messagebox as tkmessagebox
from tkinter import filedialog
import threading

from PIL import Image, ImageTk
from gui.guiGraph import GuiGraph
from gui.ctxMenu import CtxMenu
import gui.interactive.hub as ihub
from numpy import ndarray
from classifiedjson import dumps, load
from datetime import datetime
import numpy as np
import gui.decToFreq as decToFreq

from gui.communication_interface import CommunicationInterface


class Gui:
    root: tk.Tk
    graph: GuiGraph
    text: tk.Label
    errorRate: tk.DoubleVar
    connectedLabel: tk.Label
    menu: CtxMenu
    cid: int = 0
    interact: ihub.Hub
    t_connect: threading.Thread | None
    t: tk.Toplevel | None

    def __init__(
        self, comm: CommunicationInterface = CommunicationInterface("0.0.0.0")
    ):
        self.t = None
        self.root = tk.Tk()

        self.t_connect = None
        self.connectedLabel = "Not connected"

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

        self.connectedLabel = tk.Label(self.root, text="Not connected", fg="red")
        self.connectedLabel.grid(column=0, row=2, sticky="e")

        self.ip = tk.StringVar(self.root, self.interact.comm.addr)

        self.root.bind("<<CONNECT>>", self.onConnect)
        self.root.bind("<Configure>", self.onResize)
        self.root.bind("<<toggleEvent>>", self.onToggle)
        self.root.bind("<<FOURIER>>", self.onAskFourrier)
        self.root.bind("<<SAVE>>", self.onSave)
        self.root.bind("<<LOAD>>", self.onLoad)
        self.root.bind("<<EXPORT_MATLAB>>", self.onExportMatlab)
        self.interact.bind("<<changeGraph_f2>>", self.updateGraphFromResultF2)
        self.interact.bind("<<changeGraph_f1>>", self.updateGraphFromResultF1)

    def updateGraphFromResultF2(self, event):
        self.setPlot(self.interact.f2.graphToUpdate)

    def updateGraphFromResultF1(self, event):
        self.setPlot(self.interact.f1.graphToUpdate[2])

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

    def toggleWait(self, value: bool) -> None:
        if value:
            # self.root.configure(cursor="wait")
            # self.graph.getTkWidget().configure(cursor="wait")
            self.root.update()
        else:
            self.root.config(cursor="")
            self.graph.getTkWidget().configure(cursor="")
            self.root.update()

    def dummyCall(self) -> None:
        pass

    def onConnect(self, event) -> None:
        if self.t_connect is None or not self.t_connect.is_alive():
            if self.t_connect is not None:
                self.t_connect.join()
        self.t = tk.Toplevel(self.root)
        tk.Label(self.t, text="IP adress").grid(column=0, row=0, columnspan=2)

        tk.Entry(self.t, textvariable=self.ip).grid(column=0, row=1)
        tk.Button(self.t, text="Connect", command=self.commitConnect).grid(
            column=1, row=1
        )

    def commitConnect(self) -> None:
        self.t.destroy()
        self.t = None
        self.interact.comm.addr = self.ip.get()
        print("On connect")
        self.connectedLabel.configure(text="Connecting...")
        self.connectedLabel.configure(fg="orange")
        self.toggleWait(True)
        self.t_connect = threading.Thread(target=self.t_onConnect)
        self.t_connect.start()

    def t_onConnect(self):
        if self.interact.connect():
            self.connectedLabel.config(text="Connected")
            self.connectedLabel.config(fg="green")
            self.interact.f1.updateStatus()
        else:
            self.connectedLabel.config(text="Not connected")
            self.connectedLabel.config(fg="red")
            tkmessagebox.showerror("Connection", "Failed to connect to the device.")
        self.toggleWait(False)

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
            plt = []
            for i in self.graph.plot_array:
                plt.append((list(i[0]), i[1], i[2]))
            serial_data = dumps(plt)
            with open(f, "w") as file:
                file.write(serial_data)

    def onLoad(self, event) -> None:
        f = filedialog.askopenfilename()
        if f != "":
            with open(f, "r") as file:
                try:
                    data = load(file)
                except Exception as _:
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

            result = self.interact.f2.comm.readFromSignal(
                data[0][0],
                float(self.interact.f2.freq.get()) * 1000,
                int(self.interact.f2.cyc.get()),
                self.interact.f2.getDecim(),
                float(self.interact.f2.threshold.get()) / 100,
            )

            """self.interact.f2.RecepterStatusLabel.configure(
                text=status[1][0], foreground=status[1][1]
            )"""

            # Build the result string with '\n' separator every 35 cahracters from bits in result[1]
            resultString = "\n".join(
                [result[1][i : i + 35] for i in range(0, len(result[1]), 35)]
            )

            self.interact.f2.graphToUpdate = result[2]
            self.interact.f2.event_generate("<<ChangeGraph>>")
            self.interact.f2.result_label.configure(text="RESULT :\n" + resultString)

    def onExportMatlab(self, evt):
        t = datetime.today().__str__().replace(" ", "_").replace(":", "-").split(".")[0]
        f = filedialog.asksaveasfilename(
            defaultextension="txt",
            initialfile="ioron_" + t + "_yaxis.txt",
            filetypes=[("Text file", ".txt"), ("all files", "*")],
        )
        f2 = filedialog.asksaveasfilename(
            defaultextension="txt",
            initialfile="ioron_" + t + "_xaxis.txt",
            filetypes=[("Text file", ".txt"), ("all files", "*")],
        )
        print(f, f2)
        if f != "" and f2 != "":
            print("export")
            serial_data = " ".join([str(x) for x in self.graph.plot_array[0][0]])
            with open(f, "w") as file:
                file.write(serial_data)
            serial_data = " ".join(
                [
                    str(x)
                    for x in (
                        np.arange(0, len(list(self.graph.plot_array[0][0])))
                        / decToFreq.dectofreq[64]
                    )
                ]
            )
            with open(f2, "w") as file:
                file.write(serial_data)
            print("done")

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
