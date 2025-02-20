import tkinter as tk
from tkinter import ttk

from gui.interactive.testingmode import TestingMode
from gui.interactive.automode import AutoMode
from numpy import ndarray

from gui.communication_interface import CommunicationInterface


class Hub(ttk.Notebook):
    comm: CommunicationInterface
    f1: AutoMode
    f2: TestingMode

    def __init__(self, master, comm: CommunicationInterface):
        super().__init__(master)
        self.comm = comm
        self.f1 = AutoMode(self, comm)
        self.f2 = TestingMode(self, comm)
        self.f1.pack(fill=tk.BOTH, expand=True)
        self.f2.pack(fill=tk.BOTH, expand=True)
        self.add(self.f1, text="Auto Mode")
        self.add(self.f2, text="Testing Mode")
        self.f2.bind("<<ChangeGraph>>", self.handleGraphModF2)
        self.f1.bind("<<ChangeGraph>>", self.handleGraphModF1)
        self.bind("<<NotebookTabChanged>>", self.toggleMode)

    def connect(self) -> bool:
        return self.comm.connect(self.index(self.select()))

    def handleGraphModF2(self, event):
        self.event_generate("<<changeGraph_f2>>")

    def handleGraphModF1(self, event):
        self.event_generate("<<changeGraph_f1>>")

    def setResult(self, value: ndarray):
        pass

    def toggleMode(self, evt) -> None:
        mode = self.index(self.select())
        print("[HUB EVENT] changing to mode", mode)
        if self.comm.isConnected:
            self.comm.toggleMode(mode)
            if mode == 0:
                self.f1.updateStatus()
