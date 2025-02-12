import tkinter as tk
import types
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk,
)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.projections import register_projection
from matplotlib.axes import Axes
import numpy as np

from gui import decToFreq

from utils import get_one_block_step


class MyAxes(Axes):
    name = "Ratio_le_y"

    def drag_pan(self, button, key, x, y):
        return super().drag_pan(button, "x", x, y)


register_projection(MyAxes)


class GuiGraph:
    root: tk.Widget | tk.Tk
    graph: FigureCanvasTkAgg
    toolbar: NavigationToolbar2Tk
    toggle: list[bool]
    plot_array: list[tuple[list[float], str, str]]
    cid: int = 0

    def __init__(self, parent: tk.Widget | tk.Tk):
        fig = Figure(figsize=(9, 1.4), dpi=88.9)
        self.plot_array = []
        self.sp = fig.add_subplot(111, projection="Ratio_le_y")
        self.root = parent
        self.frame = tk.Frame(parent, background="white")
        self.graph = FigureCanvasTkAgg(fig, master=self.frame)
        self.graph.draw()
        self.graph.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2Tk(self.graph, self.frame, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.graph.figure.subplots_adjust(left=0.04, right=1, top=1, bottom=0)

        self.toolbar.release_zoom = types.MethodType(self.release_zoom, self.toolbar)

    def onResize(self, width):
        self.graph.figure.set_size_inches(9 * (width / 800), 1.4 * (width / 800))
        self.graph.get_tk_widget().config(
            height=int((1.7 / 9) * width),
            width=int(width),
        )

    def getTkWidget(self):
        return self.frame

    def onKeyPress(self, event) -> None:
        # print("you pressed {}".format(event.key))
        key_press_handler(event, self.graph, self.toolbar)

    def release_zoom(self, s, event):
        event.key = "x"
        NavigationToolbar2Tk.release_zoom(s, event)

    # Clear and load a new plot. Can be called by another thread
    def setPlot(self, plot_array: list[tuple[list[float], str, str]]):
        self.plot_array = plot_array
        self.toggle = [True for i in range(0, len(plot_array))]
        self.updatePlot(reset_lim=True)

    def toggleGraph(self, idx):
        self.toggle[idx] = not self.toggle[idx]
        self.updatePlot()

    def updatePlot(self, reset_lim=False):
        xlim = self.sp.get_xlim()
        self.sp.clear()

        for i, item in enumerate(self.plot_array):
            if not self.toggle[i]:
                continue
            self.sp.plot(item[0], color=item[1])

        # for x in range(102, 16384)[::get_one_block_step(250000, 5, 64)]:
        # self.sp.axvline(x, color='r')

        if reset_lim:
            self.sp.set(ylim=(-1.1, 1.1), xlim=(0, len(self.plot_array[0][0])))
        else:
            self.sp.set(ylim=(-1.1, 1.1), xlim=xlim)
        self.sp.set_yticks([-1, -0.5, 0, 0.5, 1])
        self.sp.grid(axis="y")

        self.graph.draw()
        self.toolbar.update()
        # RESETING EVENT BOUND TO THE GRAPH ON RELOAD
        if self.cid != 0:
            self.graph.mpl_disconnect(self.cid)
        self.cid = self.graph.mpl_connect("key_press_event", self.onKeyPress)

    def generateFourier(self, decimation) -> None:
        if len(self.plot_array) == 0:
            return
        tl: tk.Toplevel = tk.Toplevel(self.root)

        tl.geometry("700x440")

        fig = Figure(figsize=(7, 4), dpi=100)

        sp = fig.add_subplot(111, projection="Ratio_le_y")

        boundaries = self.sp.get_xlim()

        print(boundaries)

        item = self.plot_array[0][0][int(boundaries[0]) : int(boundaries[1])]

        length = len(item) if len(item) > 100 else 100

        ft = np.fft.fft(item, length)
        freq = np.fft.fftfreq(length) * decToFreq.dectofreq[decimation] * 0.001
        sp.plot(freq, ft.real**2)
        sp.set_xlim((0, 400))

        frame = tk.Frame(master=tl, background="white")
        frame.pack()
        graph = FigureCanvasTkAgg(fig, master=frame)
        graph.draw()
        graph.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(graph, frame, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        graph.figure.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.1)

        toolbar.release_zoom = types.MethodType(self.release_zoom, toolbar)

        print("ok")

        def onresizetl(event):
            if event.widget != tl:
                return
            graph.figure.set_size_inches(
                4 * ((event.height - 40) / 400), 7 * (event.width / 700)
            )

            graph.get_tk_widget().config(
                height=int(event.height) - 40,
                width=int(event.width),
            )

            graph.draw()

        tl.bind("<Configure>", onresizetl)
        tl.mainloop()
