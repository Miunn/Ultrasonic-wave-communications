import tkinter as tk
from tkinter import ttk

from interactive.testingmode import TestingMode
from numpy import ndarray

from communication_interface import CommunicationInterface


class Hub(ttk.Notebook):
    comm: CommunicationInterface

    def __init__(self, master, comm: CommunicationInterface):
        super().__init__(master)
        self.comm = comm
        f1 = ttk.Frame(self)
        f2 = TestingMode(self, comm)
        f1.pack(fill=tk.BOTH, expand=True)
        f2.pack(fill=tk.BOTH, expand=True)
        self.add(f1, text="Async Mode")
        self.add(f2, text="Testing Mode")

    def setResult(self, value: ndarray):
        pass
