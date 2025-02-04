import argparse

from gui.gui import Gui

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="IOron",
        description="Sender and signal receiver for Ultrasonic Communication",
        epilog="PLP24INT41 - Ait Taleb Brahim / Caulier Rémi / Bouyaakoub Annas / Sausse Sylvain / Verkimpe Yann",
    )
    parser.add_argument(
        "--scpi",
        help="Use distant RedPitaya server to send and receive signals",
        action="store_true",
    )
    parser.add_argument(
        "--standalone",
        help="Use local RedPitaya server to send and receive signals automatically",
        action="store_true",
    )
    parser.add_argument("--ip", help="IP address of the distant RedPitaya", type=str)

    args = parser.parse_args()

    if args.scpi:
        from client_communication.communication_pitaya_scpi import (
            CommunicationPitayaSCPI,
        )

        g = Gui(
            CommunicationPitayaSCPI(args.ip if args.ip is not None else "10.42.0.125")
        )
        g.mainloop()
    elif args.standalone:
        from pitaya.redpitaya_standalone import RedPitaya_Standalone
        from werkzeug.serving import run_simple

        app = RedPitaya_Standalone()
        run_simple(
            "127.0.0.1", 5000, app.getServerApp(),
            use_debugger=True,
            use_reloader=True
        )
    else:
        from client_communication.communication_pitaya_socket import (
            CommunicationPitayaSocket,
        )

        g = Gui(
            CommunicationPitayaSocket(args.ip if args.ip is not None else "10.42.0.125")
        )
        g.mainloop()
