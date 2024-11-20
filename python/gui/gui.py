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


class Gui:
    root: tk.Tk
    graph: FigureCanvasTkAgg
    toolbar: NavigationToolbar2Tk
    frame: tk.Frame
    text: tk.Label
    errorRate: tk.DoubleVar
    cid: int = 0

    def __init__(self):
        self.root = tk.Tk()

        self.errorRate = tk.DoubleVar()

        self.root.title("IOron - Visualizer")
        self.root.geometry("800x480")

        fig = Figure(figsize=(9, 1.7), dpi=88.9)

        self.sp = fig.add_subplot(111, projection="Ratio_le_y")

        self.frame = tk.Frame(self.root)
        self.frame.grid(column=0, row=0, columnspan=2)

        self.graph = FigureCanvasTkAgg(fig, master=self.frame)
        self.graph.draw()
        self.graph.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2Tk(self.graph, self.frame, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.toolbar.release_zoom = types.MethodType(self.release_zoom, self.toolbar)

        self.text = tk.Label(
            self.root,
            text="Statistics\n\n\nMessages Envoyés : 53\nMessages recus : 53\n\nFaux positif : 1 (1.89%)\n\nFaux négatifs : 1 (1.89%)\n\nMessages corrompus : 1 (1.89%)\n\nMessages non-corrompus et non-valide : 0 (0.00%)\n\nMessages valide : 51 (96.22%)",
        )
        self.text.grid(column=1, row=1)

    def onKeyPress(self, event) -> None:
        # print("you pressed {}".format(event.key))
        key_press_handler(event, self.graph, self.toolbar)

    def release_zoom(self, s, event):
        # print(s, event, event.__dict__)
        event.key = "x"
        # print(s, event, event.key)
        NavigationToolbar2Tk.release_zoom(s, event)

    def mainloop(self) -> None:
        self.root.mainloop()

    def setPlot(self, plot_array: list[tuple[list[float], str]]):
        self.sp.clear()

        for item in plot_array:
            self.sp.plot(item[0], color=item[1])
            self.sp.set(ylim=(-1.1, 1.1), xlim=(0, len(item[0])))
            self.sp.set_yticks([-1, 0, 1])
            self.sp.grid(axis="y")

        self.graph.figure.subplots_adjust(left=0.04, right=1, top=1, bottom=0)
        self.graph.draw()
        self.toolbar.update()
        if self.cid != 0:
            self.graph.mpl_disconnect(self.cid)
        self.cid = self.graph.mpl_connect("key_press_event", self.onKeyPress)


if __name__ == "__main__":
    with open("gui/signal-dec-64-work-voltage.bin", "r") as f:
        voltage = [float(n) for n in f.readline().split()]

    with open("gui/signal-dec-64-work-demod.bin", "r") as f:
        demod = [float(n) for n in f.readline().split()]

    with open("gui/signal-dec-64-work-lpf.bin", "r") as f:
        lpf = [float(n) for n in f.readline().split()]

    g = Gui()
    g.setPlot(
        [(voltage[:10800], "#BBBBFF"), (demod[:10800], "#FFBB99"), (lpf[:10800], "red")]
    )
    g.mainloop()
