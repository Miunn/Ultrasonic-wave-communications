from abc import update_abstractmethods
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


class MyAxes(Axes):
    name = "Ratio_le_y"

    def drag_pan(self, button, key, x, y):
        return super().drag_pan(button, "x", x, y)


register_projection(MyAxes)


class GuiGraph:
    root: tk.Frame
    graph: FigureCanvasTkAgg
    toolbar: NavigationToolbar2Tk
    toggle: list[bool]
    plot_array: list[tuple[list[float], str]]
    cid: int = 0

    def __init__(self, parent: tk.Widget | tk.Tk):
        fig = Figure(figsize=(9, 1.7), dpi=88.9)

        self.sp = fig.add_subplot(111, projection="Ratio_le_y")

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
        self.graph.figure.set_size_inches(9 * (width / 800), 1.7 * (width / 800))
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
    def setPlot(self, plot_array: list[tuple[list[float], str]]):
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
