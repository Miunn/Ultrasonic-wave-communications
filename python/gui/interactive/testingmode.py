import tkinter as tk
from tkinter import ttk

import numpy as np

import threading

from gui.communication_interface import CommunicationInterface


frame_opt = ["Plain", "CAN", "ENCcan"]


entry_opt = ["Bits", "Hex", "ASCII/UTF-8"]

frequency = []

status: list[tuple[str, str]] = [
    ("Error", "red"),
    ("Ready", "green"),
    ("Running...", "orange"),
]

decim_opt = ["1", "8", "64", "1024"]


class TestingMode(tk.Frame):
    emmiter: tk.Frame
    common: tk.Frame
    reciever: tk.Frame

    entry_t: tk.StringVar
    entry_v: tk.StringVar

    common_t: tk.StringVar

    deim_t: tk.StringVar
    trigger: tk.StringVar
    freq: tk.StringVar
    cyc: tk.StringVar
    trigg_dd: tk.StringVar
    threshold: tk.StringVar

    EmitterStatusLabel: tk.Label
    RecepterStatusLabel: tk.Label

    te: threading.Thread | None
    tr: threading.Thread | None

    comm: CommunicationInterface

    result_label: tk.Label

    graphToUpdate: list[tuple[list[float], str, str]]

    def __init__(self, master, comm):
        super().__init__(master=master)
        self.te = None
        self.tr = None
        self.comm = comm
        self.freq = tk.StringVar(self, value="250")
        self.cyc = tk.StringVar(self, value="5")
        self.entry_t = tk.StringVar(self, value="Bits")
        self.entry_v = tk.StringVar(self, value="")
        self.common_t = tk.StringVar(self, value="Plain")
        self.deim_t = tk.StringVar(self, value="64")
        self.trigger = tk.StringVar(self, "0.6")
        self.trigg_dd = tk.StringVar(self, "0.2")
        self.threshold = tk.StringVar(self, "30")

        self.emmiter = tk.Frame(self)
        self.emmiter.grid(column=2, row=0, sticky="nsew")
        self.common = tk.Frame(self)
        self.common.grid(column=0, row=0, sticky="nsew")
        self.reciever = tk.Frame(self)
        self.reciever.grid(column=4, row=0, sticky="nsew")
        ttk.Separator(self, orient="vertical").grid(column=1, row=0, sticky="ns")
        ttk.Separator(self, orient="vertical").grid(column=3, row=0, sticky="ns")

        self.generateEmitter()
        self.generateCommon()
        self.generateReciever()

        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(4, weight=1)
        self.rowconfigure(0, weight=1)

    def emit(self):
        if self.te == None or not self.te.is_alive():
            if self.te != None:
                self.te.join()
            self.te = threading.Thread(target=self.t_emit)
            self.te.start()

    def listen(self):
        if self.tr == None or not self.tr.is_alive():
            if self.tr != None:
                self.tr.join()
            self.tr = threading.Thread(target=self.t_listen)
            self.tr.start()

    def t_emit(self):
        self.EmitterStatusLabel.configure(text=status[2][0], foreground=status[2][1])
        result = self.comm.emit(
            np.zeros(2, int), int(float(self.freq.get()) * 1000), int(self.cyc.get())
        )
        if result == 0:
            self.EmitterStatusLabel.configure(
                text=status[1][0], foreground=status[1][1]
            )
        else:
            self.EmitterStatusLabel.configure(
                text=status[0][0], foreground=status[0][1]
            )

    def t_listen(self):
        self.RecepterStatusLabel.configure(text=status[2][0], foreground=status[2][1])
        result = self.comm.startListening(
            int(float(self.freq.get()) * 1000),
            int(self.cyc.get()),
            int(self.deim_t.get()),
            float(self.trigger.get()),
            float(self.trigg_dd.get()),
            float(self.threshold.get()),
        )
        if result[0] == 0:
            self.RecepterStatusLabel.configure(
                text=status[1][0], foreground=status[1][1]
            )
            self.graphToUpdate = result[2]
            self.event_generate("<<ChangeGraph>>")
            self.result_label.configure(
                text="RESULT :\n" + "".join([str(r) for r in result[1]])
            )
        else:
            self.RecepterStatusLabel.configure(
                text=status[0][0], foreground=status[0][1]
            )

    def generateEmitter(self):
        emiter_title = tk.Label(self.emmiter, text="Signal generation")
        emiter_title.grid(row=0, column=0)

        emiter_entry = tk.Text(self.emmiter, height=4, width=30)
        emiter_entry.grid(column=0, row=3)

        emiter_btn1 = tk.Button(self.emmiter, text="Emit signal", command=self.emit)
        emiter_btn1.grid(row=5, column=0)

        self.EmitterStatusLabel = tk.Label(
            self.emmiter, text=status[1][0], foreground=status[1][1]
        )
        self.EmitterStatusLabel.grid(column=0, row=6)

        self.emmiter.rowconfigure(4, weight=1)
        self.emmiter.rowconfigure(0, weight=1)
        self.emmiter.rowconfigure(2, weight=1)
        self.emmiter.rowconfigure(7, weight=1)
        self.emmiter.columnconfigure(0, weight=1)

    def generateCommon(self):
        common_title = tk.Label(self.common, text="Common parameters")
        common_title.grid(row=1, column=0, columnspan=2)

        emiter_selector = tk.OptionMenu(self.common, self.entry_t, *entry_opt)
        emiter_selector.grid(row=3, column=0, columnspan=2)

        common_selector = tk.OptionMenu(self.common, self.common_t, *frame_opt)
        common_selector.grid(row=4, column=0, columnspan=2)

        common_freq = tk.Spinbox(
            self.common,
            from_=100,
            to=400,
            increment=0.1,
            width=7,
            textvariable=self.freq,
        )
        common_freq.grid(row=5, column=0, sticky="e")
        tk.Label(self.common, text="KHz").grid(column=1, row=5, sticky="w")

        common_cyc = tk.Spinbox(
            self.common, from_=1, to=10, increment=1, width=5, textvariable=self.cyc
        )
        common_cyc.grid(row=6, column=0, sticky="e")
        tk.Label(self.common, text="sine/bit").grid(column=1, row=6, sticky="w")

        self.common.rowconfigure(0, weight=1)
        self.common.rowconfigure(2, weight=5)
        self.common.rowconfigure(3, weight=1)
        self.common.rowconfigure(4, weight=1)
        self.common.rowconfigure(5, weight=1)
        self.common.rowconfigure(6, weight=1)
        self.common.rowconfigure(7, weight=5)
        self.common.columnconfigure(1, weight=1)
        self.common.columnconfigure(0, weight=1)

    def generateReciever(self):
        reciever_title = tk.Label(self.reciever, text="Recieve signal")
        reciever_title.grid(row=1, column=0, columnspan=4)

        decimation = tk.OptionMenu(self.reciever, self.deim_t, *decim_opt)
        decimation.grid(column=1, row=3, columnspan=2, sticky="w")
        tk.Label(self.reciever, text="Decimation : ").grid(column=0, row=3, sticky="e")

        trigg = tk.Spinbox(
            self.reciever,
            from_=0,
            to=1,
            increment=0.1,
            width=6,
            textvariable=self.trigger,
        )
        trigg.grid(column=1, row=4, sticky="w")
        tk.Label(self.reciever, text="Trigger level : ").grid(
            column=0, row=4, sticky="e"
        )
        tk.Label(self.reciever, text="V").grid(column=2, row=4, sticky="w")

        trigg_dd = tk.Spinbox(
            self.reciever,
            from_=0,
            to=1,
            increment=0.1,
            width=6,
            textvariable=self.trigg_dd,
        )
        trigg_dd.grid(column=1, row=5, sticky="w")
        tk.Label(self.reciever, text="Decision trigger level : ").grid(
            column=0, row=5, sticky="e"
        )
        tk.Label(self.reciever, text="V").grid(column=2, row=5, sticky="w")

        thre = tk.Spinbox(
            self.reciever,
            from_=0,
            to=100,
            increment=5,
            width=6,
            textvariable=self.threshold,
        )
        thre.grid(column=1, row=6, sticky="w")
        tk.Label(self.reciever, text="Decision area threshold : ").grid(
            column=0, row=6, sticky="e"
        )
        tk.Label(self.reciever, text="%").grid(column=2, row=6, sticky="w")

        tk.Button(self.reciever, text="Start listening", command=self.listen).grid(
            column=0, row=8, columnspan=3
        )

        self.result_label = tk.Label(self.reciever, text="RESULT :\n")
        self.result_label.grid(column=0, row=9, columnspan=4)

        self.RecepterStatusLabel = tk.Label(
            self.reciever, text=status[1][0], foreground=status[1][1]
        )
        self.RecepterStatusLabel.grid(column=0, row=10, columnspan=3)

        self.reciever.columnconfigure(0, weight=1)
        self.reciever.columnconfigure(2, weight=1)
        self.reciever.rowconfigure(0, weight=3)
        self.reciever.rowconfigure(2, weight=6)
        self.reciever.rowconfigure(11, weight=6)
        self.reciever.rowconfigure(7, weight=6)
