import threading
from gui.gui import Gui
from gui.communication_interface import CommunicationInterface


if __name__ == "__main__":
    g = Gui(CommunicationInterface("10.5.0.0"))
    g.mainloop()
