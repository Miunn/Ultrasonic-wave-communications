import tkinter as tk
from tkinter import ttk

import numpy as np

import threading

from gui.communication_interface import CommunicationInterface
from gui.ErrorTopLevel import ErrorTopLevel
from gui import decToFreq
from frames.can import CanFrame


frame_opt = ["Plain", "CAN", "ENCcan"]


entry_opt = ["Bits", "Hex", "ASCII/UTF-8"]

frequency = []

status: list[tuple[str, str]] = [
    ("Error", "red"),
    ("Ready", "green"),
    ("Running...", "orange"),
]


def generate_deim_text(v):
    if decToFreq.dectofreq[v] < 1000000:
        return f"{v} ({int(decToFreq.dectofreq[v] * 0.001)} KHz)"
    else:
        return f"{v} ({int(decToFreq.dectofreq[v] * 0.001)*0.001} MHz)"


decim_opt = [generate_deim_text(i) for i in [1, 8, 64, 1024]]


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

    emiter_entry: tk.Text

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
        self.deim_t = tk.StringVar(self, value=generate_deim_text(64))
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

    def getDecim(self) -> int:
        return int(self.deim_t.get().split(" ")[0])

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
        convtype = self.entry_t.get()
        text = self.emiter_entry.get("1.0", tk.END)
        print(text)
        to_send = self.comm.encapsulate(
            self.comm.convertToArray(text, convtype), self.common_t.get()
        )
        print(to_send)
        self.EmitterStatusLabel.configure(text=status[2][0], foreground=status[2][1])
        result = self.comm.emit(
            to_send, int(float(self.freq.get()) * 1000), int(self.cyc.get())
        )
        if result == 0:
            self.EmitterStatusLabel.configure(
                text=status[1][0], foreground=status[1][1]
            )
        else:
            self.EmitterStatusLabel.configure(
                text=status[0][0], foreground=status[0][1]
            )
            ErrorTopLevel(str(result)).mainloop()

    def t_listen(self):
        convtype = self.entry_t.get()
        self.RecepterStatusLabel.configure(text=status[2][0], foreground=status[2][1])
        result = self.comm.startListening(
            int(float(self.freq.get()) * 1000),
            int(self.cyc.get()),
            self.getDecim(),
            float(self.trigger.get()),
            float(self.trigg_dd.get()),
            float(self.threshold.get()) / 100,
        )
        if result[0] == 0:
            self.RecepterStatusLabel.configure(
                text=status[1][0], foreground=status[1][1]
            )
            self.graphToUpdate = result[2]
            self.event_generate("<<ChangeGraph>>")
            self.result_label.configure(
                text="RESULT :\n" + self.comm.convertToStringM(result[1], convtype)
            )
        else:
            self.result_label.configure(text="RESULT :\n")
            self.RecepterStatusLabel.configure(
                text=status[0][0], foreground=status[0][1]
            )

    def generateEmitter(self):
        emiter_title = tk.Label(self.emmiter, text="Signal generation")
        emiter_title.grid(row=0, column=0)

        self.emiter_entry = tk.Text(self.emmiter, height=4, width=30)
        self.emiter_entry.grid(column=0, row=3)

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
        reciever_title.grid(row=1, column=0, columnspan=5)

        decimation = tk.OptionMenu(self.reciever, self.deim_t, *decim_opt)
        decimation.grid(column=2, row=3, columnspan=3, sticky="e")
        tk.Label(self.reciever, text="Decimation : ").grid(column=1, row=3, sticky="w")

        trigg = tk.Spinbox(
            self.reciever,
            from_=0,
            to=1,
            increment=0.1,
            width=6,
            textvariable=self.trigger,
        )
        trigg.grid(column=3, row=4, sticky="w")
        tk.Label(self.reciever, text="Trigger level : ").grid(
            column=1, row=4, sticky="w", columnspan=2
        )
        tk.Label(self.reciever, text="V").grid(column=4, row=4, sticky="w")

        trigg_dd = tk.Spinbox(
            self.reciever,
            from_=0,
            to=1,
            increment=0.1,
            width=6,
            textvariable=self.trigg_dd,
        )
        trigg_dd.grid(column=3, row=5, sticky="w")
        tk.Label(self.reciever, text="Decision trigger level : ").grid(
            column=1, row=5, sticky="w", columnspan=2
        )
        tk.Label(self.reciever, text="V").grid(column=4, row=5, sticky="w")

        thre = tk.Spinbox(
            self.reciever,
            from_=0,
            to=100,
            increment=5,
            width=6,
            textvariable=self.threshold,
        )
        thre.grid(column=3, row=6, sticky="w")
        tk.Label(self.reciever, text="Decision area threshold : ").grid(
            column=1, row=6, sticky="w", columnspan=2
        )
        tk.Label(self.reciever, text="%").grid(column=4, row=6, sticky="w")

        tk.Button(self.reciever, text="Start listening", command=self.listen).grid(
            column=1, row=8, columnspan=4
        )

        self.result_label = tk.Label(self.reciever, text="RESULT :\n")
        self.result_label.grid(column=1, row=9, columnspan=4)

        self.RecepterStatusLabel = tk.Label(
            self.reciever, text=status[1][0], foreground=status[1][1]
        )
        self.RecepterStatusLabel.grid(column=1, row=10, columnspan=4)

        self.reciever.columnconfigure(0, weight=1)
        self.reciever.columnconfigure(5, weight=1)
        self.reciever.rowconfigure(0, weight=3)
        self.reciever.rowconfigure(2, weight=6)
        self.reciever.rowconfigure(11, weight=6)
        self.reciever.rowconfigure(7, weight=6)
