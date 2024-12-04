import tkinter as tk
from PIL import Image, ImageTk
from webbrowser import open as wopen


class CtxMenu(tk.Menu):
    view_graph: tk.Menu
    graph_toggle: list[list]

    def __init__(self, master):
        super().__init__(master=master)

        # File submenu
        file = tk.Menu(master=master)
        self.add_cascade(label="File", menu=file)

        # Edit submenu
        edit = tk.Menu(master=master)
        edit.add_command(label="Fourier transform", command=self.askFourier)
        self.add_cascade(label="Edit", menu=edit)

        # View submenu
        view = tk.Menu(master=master)
        self.view_graph = tk.Menu(master=master)
        self.view_graph.add_command(label="dummy")
        view.add_cascade(label="Graph", menu=self.view_graph)
        self.add_cascade(label="View", menu=view)

        # Help submenu
        help = tk.Menu(master=master)
        help.add_command(label="Documentation", command=self.getHelp)
        help.add_command(label="About", command=self.getAbout)
        self.add_cascade(label="Help", menu=help)

        self.setGraphLayer([])

    def getHelp(self):
        wopen("https://fr.wikihow.com/bien-utiliser-un-ordinateur")

    def getAbout(self):
        topl = tk.Toplevel(master=self.master)
        topl.geometry("300x240")
        topl.title("IOron visualizer - About")
        img = Image.open("gui/logo.png")
        c = ImageTk.PhotoImage(img.resize((240, 150)))
        d = tk.Label(topl, image=c)
        d.grid(sticky="", row=0, column=1)
        l = tk.Label(topl, text="IOron visualizer\nversion 0.0.2")
        l.grid(sticky="", row=1, column=1)
        topl.resizable(False, False)
        topl.columnconfigure(1, weight=1)
        topl.rowconfigure(1, weight=1)
        topl.mainloop()

    def setGraphLayer(self, items: list[str]):
        self.graph_toggle = [[item, True] for item in items]
        self.updateGraphMenu()

    def updateGraphMenu(self):
        self.view_graph.delete(0, 1000)
        for i, item in enumerate(self.graph_toggle):
            self.view_graph.add_command(
                label=("✓⠀" if item[1] else "⠀⠀") + item[0],
                command=lambda idx=i: self.triggerGraphAction(idx),
            )

    def triggerGraphAction(self, idx: int):
        print("toggleEvent :", idx)
        self.graph_toggle[idx][1] = not self.graph_toggle[idx][1]
        self.updateGraphMenu()
        self.event_generate("<<toggleEvent>>", when="now", x=idx)

    def askFourier(self):
        self.event_generate("<<FOURIER>>", when="now", x=64)
