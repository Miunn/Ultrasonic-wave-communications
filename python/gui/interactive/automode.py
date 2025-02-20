import tkinter as tk
from tkinter import ttk

from gui.communication_interface import CommunicationInterface

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


modes = ["BSPK", "CROSS."]


class AutoMode(tk.Frame):
    comm: CommunicationInterface
    f1: tk.Frame
    f2: tk.Frame
    requestGraphButton: tk.Button
    optionButton: tk.Button

    def __init__(self, master, comm):
        super().__init__(master=master)
        self.comm = comm
        fig = Figure(figsize=(2.7, 2.7), dpi=88.9)
        f1 = tk.Frame(master=self)
        f1.grid(column=0, row=0, sticky="nsew")
        f2 = tk.Frame(master=self)
        f2.grid(column=2, row=0, sticky="nsew")
        ttk.Separator(self, orient="vertical").grid(column=1, row=0, sticky="ns")
        self.ar = False

        # ------------------- f1 -----------------------------

        self.freq = tk.StringVar(self, value="250")
        self.cyc = tk.StringVar(self, value="1")
        self.trigger = tk.StringVar(self, value="0.6")
        self.trigg_dd = tk.StringVar(self, value="0.2")
        self.threshold = tk.StringVar(self, "30")
        self.mode = tk.StringVar(self, "CROSS.")
        self.refreshTime = tk.StringVar(self, "5")

        tk.Label(f1, text="Options").grid(column=1, row=0, columnspan=3, sticky="ew")

        tk.Label(f1, text="Mode :").grid(column=1, row=1, sticky="w")
        mode_selector = tk.OptionMenu(f1, self.mode, *modes)
        mode_selector.grid(column=2, row=1, columnspan=2, sticky="w")

        tk.Label(f1, text="Frequency :").grid(column=1, row=2, sticky="w")
        freq_selector = tk.Spinbox(
            f1,
            from_=100,
            to=400,
            increment=1.0,
            width=7,
            textvariable=self.freq,
        )
        freq_selector.grid(row=2, column=2, sticky="ew")
        tk.Label(f1, text="KHz").grid(column=3, row=2, sticky="w")

        tk.Label(f1, text="CYC :").grid(column=1, row=3, sticky="w")
        cyc_selector = tk.Spinbox(
            f1, from_=1, to=10, increment=1, width=7, textvariable=self.cyc
        )
        cyc_selector.grid(column=2, row=3, sticky="ew")
        tk.Label(f1, text="sine/bit").grid(column=3, row=3, sticky="w")

        ttk.Separator(f1, orient="horizontal").grid(
            column=1, columnspan=3, row=4, sticky="ew"
        )

        tk.Label(f1, text="Trigger level : ").grid(column=1, row=5, sticky="w")
        trigg = tk.Spinbox(
            f1,
            from_=0,
            to=1,
            increment=0.1,
            width=7,
            textvariable=self.trigger,
        )
        trigg.grid(column=2, row=5, sticky="w")
        tk.Label(f1, text="V").grid(column=3, row=5, sticky="w")

        tk.Label(f1, text="Decision trigger level : ").grid(column=1, row=6, sticky="w")
        trigg_dd = tk.Spinbox(
            f1,
            from_=0,
            to=1,
            increment=0.1,
            width=7,
            textvariable=self.trigg_dd,
        )
        trigg_dd.grid(column=2, row=6, sticky="w")
        tk.Label(f1, text="V").grid(column=3, row=6, sticky="w")

        tk.Label(f1, text="Decision area threshold : ").grid(
            column=1, row=7, sticky="w"
        )
        thre = tk.Spinbox(
            f1,
            from_=0,
            to=100,
            increment=5,
            width=7,
            textvariable=self.threshold,
        )
        thre.grid(column=2, row=7, sticky="w")

        tk.Label(f1, text="%").grid(column=3, row=7, sticky="w")

        self.optionButton = tk.Button(f1, text="Apply Options", command=self.applyParam)
        self.optionButton.grid(column=1, row=8, columnspan=3)

        f1.columnconfigure(0, weight=1)
        f1.columnconfigure(4, weight=2)
        f1.rowconfigure(3, weight=1)
        f1.rowconfigure(0, weight=2)
        f1.rowconfigure(8, weight=2)
        # ------------------- f2 -----------------------------
        self.sp = fig.add_subplot(111)
        self.graph = FigureCanvasTkAgg(fig, master=f2)
        self.graph.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.graph.get_tk_widget().grid(column=0, row=0, rowspan=7)
        self.tpl = tk.Label(
            f2, text="True Positive : 0", fg="green", font=("Arial", 10)
        )
        self.tpl.grid(column=1, row=0, sticky="w")
        self.tnl = tk.Label(
            f2, text="True Negative : 0", fg="yellow", font=("Arial", 10)
        )
        self.tnl.grid(column=1, row=1, sticky="w")
        self.fnl = tk.Label(
            f2, text="False Negative : 0", fg="orange", font=("Arial", 10)
        )
        self.fnl.grid(column=1, row=2, sticky="w")
        self.fpl = tk.Label(f2, text="False Positive : 0", fg="red", font=("Arial", 10))
        self.fpl.grid(column=1, row=3, sticky="w")

        self.bepdisplayer = tk.Label(f2, text="BEP\n\n--")
        self.bepdisplayer.grid(column=2, row=0, rowspan=4)

        f2_1 = tk.Frame(f2)
        f2_1.grid(column=1, row=5, columnspan=2)
        self.updateButton = tk.Button(
            f2_1, text="Update data", command=self.updateData
        ).grid(column=1, row=0)

        self.playButton = tk.Button(
            f2_1, text="Resume session", command=self.Play
        ).grid(column=2, row=0)

        self.pauseButton = tk.Button(
            f2_1, text="Pause Session", command=self.Pause
        ).grid(column=1, row=1)

        self.resetButton = tk.Button(
            f2_1, text="Reset session", command=self.Reset
        ).grid(column=2, row=1)

        self.requestGraphButton = tk.Button(
            f2_1, text="Request graph", command=self.rqGraph
        ).grid(column=1, row=3, columnspan=2)

        self.statusLabel = tk.Label(f2_1, text="Status : Unkown")
        self.statusLabel.grid(column=1, row=5, columnspan=2)
        f2_1_2 = tk.Frame(f2_1)
        f2_1_2.grid(column=1, row=4, columnspan=2)

        self.arButton = tk.Button(
            f2_1_2, text="Auto refresh (disabled)", fg="red", command=self.toggleAr
        )
        self.arButton.grid(column=1, row=1)
        occ_selector = tk.Spinbox(
            f2_1_2,
            from_=3,
            to=120,
            increment=1.0,
            width=5,
            textvariable=self.refreshTime,
        )
        occ_selector.grid(column=2, row=1)
        tk.Label(f2_1_2, text="s").grid(column=3, row=1, sticky="w")

        f2.rowconfigure(5, weight=1)
        f2.columnconfigure(2, weight=1)

        # -----------------------------------------------------

        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)

    def toggleAr(self):
        if not self.comm.isConnected():
            return
        self.ar = not self.ar
        if self.ar:
            self.arButton.configure(text="Auto refresh (enabled)", fg="green")
            self.Ar()
        else:
            self.arButton.configure(text="Auto refresh (disabled)", fg="red")

    def Ar(self):
        if not self.ar:
            return
        self.updateData()
        self.rqGraph()
        self.after(int(self.refreshTime.get()) * 1000, self.Ar)

    def rqGraph(self):
        self.updateStatus()
        if not self.comm.isConnected():
            return
        self.graphToUpdate = self.comm.requestGraph()
        self.event_generate("<<ChangeGraph>>")

    def getMode(self) -> int:
        return modes.index(self.mode.get())

    def applyParam(self) -> None:
        self.updateStatus()
        if not self.comm.isConnected():
            return
        self.comm.changeParameter(
            {
                "mode": modes.index(self.mode.get()),
                "freq": float(self.freq.get()) * 1000,
                "cyc": self.cyc.get(),
                "trig_lvl": self.trigger.get(),
                "dec_trig": self.trigg_dd.get(),
                "dec_thresh": float(self.threshold.get()) * 0.01,
            }
        )

    def updateStatus(self) -> None:
        if self.comm.isConnected():
            status = self.comm.getDaemonStatus()
            if status:
                self.statusLabel.configure(text="Status : Started")
            else:
                self.statusLabel.configure(text="Status : Stopped")
        else:
            self.statusLabel.configure(text="Status : Not connected")

    def updateData(self) -> None:
        self.updateStatus()
        if not self.comm.isConnected():
            return
        self.sp.clear()
        try:
            tp, tn, fp, fn, bep = self.comm.fetchNewComparedData()
            colors = "Red", "Orange", "Yellow", "Green"
            explode = (0.1, 0.1, 0.1, 0.1)
            sizes = [fp, fn, tn, tp]
            self.sp.pie(sizes, autopct="%1.1f%%", colors=colors, explode=explode)
            self.graph.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
            self.graph.draw()
            self.tpl.configure(text=f"True Positive : {tp}")
            self.tnl.configure(text=f"True Negative : {tn}")
            self.fpl.configure(text=f"False Positive : {fp}")
            self.fnl.configure(text=f"False Negative : {fn}")
            self.bepdisplayer.config(text=f"BEP\n\n{bep}%")
        except:
            self.tpl.configure(text="True Positive : 0")
            self.tnl.configure(text="True Negative : 0")
            self.fpl.configure(text="False Positive : 0")
            self.fnl.configure(text="False Negative : 0")
            self.bepdisplayer.config(text="BEP\n\n--%")

    def Play(self) -> None:
        self.comm.play()
        self.updateStatus()

    def Pause(self) -> None:
        self.comm.pause()
        self.updateStatus()

    def Reset(self) -> None:
        self.comm.resetStat()
        self.updateData()
        # TODO set data to Blank
