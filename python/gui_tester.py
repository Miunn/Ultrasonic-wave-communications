from gui.gui import Gui
from python.communication.communication_pitaya_scpi import CommunicationPitayaSCPI

if __name__ == "__main__":
    g = Gui(CommunicationPitayaSCPI('10.42.0.125'))
    g.mainloop()