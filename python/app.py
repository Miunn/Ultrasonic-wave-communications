import argparse

from gui.gui import Gui
from communication.communication_pitaya_scpi import CommunicationPitayaSCPI
from communication.communication_pitaya_socket import CommunicationPitayaSocket

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='IOron',
        description='Sender and signal receiver for Ultrasonic Communication',
        epilog='PLP24INT41 - Ait Taleb Brahim / Caulier Rémi / Bouyaakoub Annas / Sausse Sylvain / Verkimpe Yann'
    )
    parser.add_argument("--scpi", help="Use distant RedPitaya server to send and receive signals", action="store_true")
    parser.add_argument("--standalone", help="Use local RedPitaya server to send and receive signals automatically", action="store_true")
    parser.add_argument("--ip", help="IP address of the distant RedPitaya", type=str)
    
    args = parser.parse_args()
    
    if args.scpi:
        g = Gui(CommunicationPitayaSCPI(args.ip if args.ip is not None else '10.42.0.125'))
        g.mainloop()
    elif args.standalone:
        print("Standalone mode")
    else:
        g = Gui(CommunicationPitayaSocket(args.ip if args.ip is not None else '10.42.0.125'))
        g.mainloop()