import tkinter as tk


class ErrorTopLevel(tk.Toplevel):
    def __init__(self, errormessage: str):
        super().__init__()
        tk.Label(self, text="Error : " + errormessage).grid(
            column=0, row=0, columnspan=2
        )
        tk.Button(self, text="OK", command=self.destroy).grid(column=1, row=1)
