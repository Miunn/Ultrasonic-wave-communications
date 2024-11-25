import tkinter as tk
from tkinter import ttk

from interactive.testingmode import TestingMode


class Hub(ttk.Notebook):
    def __init__(self, master):
        super().__init__(master)
        f1 = ttk.Frame(self)
        f2 = TestingMode(self)
        f1.pack(fill=tk.BOTH, expand=True)
        f2.pack(fill=tk.BOTH, expand=True)
        self.add(f1, text="Async Mode")
        self.add(f2, text="Testing Mode")
