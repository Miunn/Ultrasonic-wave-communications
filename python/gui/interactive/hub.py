import tkinter as tk
from tkinter import ttk

from gui.interactive.testingmode import TestingMode
from numpy import ndarray

from gui.communication_interface import CommunicationInterface


class Hub(ttk.Notebook):
    comm: CommunicationInterface
    f1: ttk.Frame
    f2: TestingMode

    def __init__(self, master, comm: CommunicationInterface):
        super().__init__(master)
        self.comm = comm
        self.f1 = ttk.Frame(self)
        self.f2 = TestingMode(self, comm)
        self.f1.pack(fill=tk.BOTH, expand=True)
        self.f2.pack(fill=tk.BOTH, expand=True)
        self.add(self.f1, text="Async Mode")
        self.add(self.f2, text="Testing Mode")
        self.f2.bind("<<ChangeGraph>>", self.handleGraphModF2)

    def connect(self) -> bool:
        return self.comm.connect()

    def handleGraphModF2(self, event):
        self.event_generate("<<changeGraph_f2>>")

    def setResult(self, value: ndarray):
        pass
