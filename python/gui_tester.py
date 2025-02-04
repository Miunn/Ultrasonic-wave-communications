from gui.gui import Gui
from python.communication_pitaya import CommunicationPitaya

if __name__ == "__main__":
    g = Gui(CommunicationPitaya("10.42.0.125"))
    # g = Gui()
    g.mainloop()
