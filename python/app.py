import argparse

from gui.gui import Gui
from communication_pitaya import CommunicationMode, CommunicationPitaya

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='IOron',
        description='Sender and signal receiver for Ultrasonic Communication',
        epilog='PLP24INT41'
    )
    parser.add_argument("--scpi", help="Use distant RedPitaya server to send and receive signals", action="store_true")
    parser.add_argument("--standalone", help="Use local RedPitaya server to send and receive signals automatically", action="store_true")
    
    args = parser.parse_args()
        
    if args.scpi:
        g = Gui(CommunicationPitaya(CommunicationMode.SCPI, args.ip))
        g.mainloop()
    elif args.standalone:
        print("Standalone mode")
    else:
        print("Default mode")