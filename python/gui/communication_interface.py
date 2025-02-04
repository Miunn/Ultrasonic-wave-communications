from numpy import ndarray, zeros
import time

from frames.can import CanFrame
from frames.higherlevelframe import IOronSTD1Frame


class CommunicationInterface:
    addr: str

    def __init__(self, addr: str) -> None:
        self.addr = addr

    def toggleMode(self, current: int) -> bool:
        """
        Toggle between auto (0) and manual (1) mode.
        """
        time.sleep(0.5)
        return True

    # ------------------------- Manual Mode commands --------------------------------
    def connect(self) -> bool:
        """
        Connect to the capture device
        """
        time.sleep(2)
        return True

    def emit(self, message: ndarray, freq: float, cyc: int, mode: int = 1) -> int:
        """
        Emit the message
        mode :
        - 0 : BSPK
        - 1 : Crosscorrelation
        """
        print(message, freq, cyc)
        time.sleep(2)
        return 0

    def startListening(
        self,
        freq: float,
        cyc: int,
        decimation: int,
        sig_trig: float,
        dec_trig: float,
        dec_thesh: float,
        mode: int = 1,
    ) -> tuple[int, ndarray, list[tuple[list[float], str, str]]]:
        time.sleep(5)
        """
        Start the listen process and sets a trigger
        to capture the voltage receieved
        mode :
        - 0 : BSPK
        - 1 : Crosscorrelation
        """
        return (0, zeros(2, int), [([], "red", "Name")])

    # -----------------------------------------------------------

    # --------- AUTO MODE COMMAND -------------------------------
    def fetchNewComparedData(self) -> list[tuple[ndarray, ndarray]]:
        """
        Fetch the last data exchnanges into a list of tuples
        (sent_data, receieved_data)
        """
        pass

    def requestGraph(self) -> list[tuple[list[float], str, str]]:
        """
        Request the graph data of the last exchange
        """
        pass

    def changeParameter(self, parameters: any) -> bool:
        """
        change the parameter of the exchange in auto mode
        (this may restart to exchange process)
        """
        pass

    # -----------------------------------------------------------

    @staticmethod
    def readFromSignal(
        self, signal: ndarray, freq: float, cyc: int, decimation: int, dec_thresh: float
    ):
        time.sleep(5)
        return zeros(2, int)

    @staticmethod
    def convertBitString(value: str) -> ndarray:
        """
        Convert a dirty string containing '1' and '0'
        into a np array of 1 and 0
        """
        sanitized_value = "".join(c for c in value if c in "01")
        result = zeros(len(sanitized_value), int)
        for i in range(0, len(sanitized_value)):
            result[i] = int(sanitized_value[i])
        return result

    @staticmethod
    def convertHexString(value: str) -> ndarray:
        """
        Convert a dirty string containing a Hex value
        (chars from 0 to F) into a np array of 1 and 0
        """
        sanitized_value = "".join(c for c in value if c in "ABCDEFabcdef01234567890")
        result = zeros(len(sanitized_value) * 4, int)
        int_san = int(sanitized_value, 16)
        i = 0
        while int_san > 0:
            result[i] = int_san % 2
            int_san //= 2
            i += 1
        return result[::-1]

    @staticmethod
    def convertString(value: str) -> ndarray:
        """
        Convert a string containing utf8 characters into
        a np array of 1 and 0
        """
        b = bytes(value, "utf-8")
        f = ""
        for i in range(1, len(b)):
            f += bin(int.from_bytes(b[(i - 1) * 8 : i * 8], byteorder="big")).lstrip(
                "0b"
            )
        result = zeros(len(f) + (8 - len(f) % 8), int)
        for i in range(0, len(f)):
            result[i + (8 - len(f) % 8)] = int(f[i])
        return result

    @staticmethod
    def convertToBitString(value: ndarray) -> str:
        """
        Convert a np array of 1 and 0 to a string of 1 and 0
        """
        return "".join(str(i) for i in value)

    @staticmethod
    def convertToHexString(value: ndarray) -> str:
        """
        Convert a np array of 1 and 0 into a string of the
        hex value of the array
        """
        string = "".join(str(i) for i in value)
        string = string[: len(string) - len(string) % 8]
        return str(hex(int(string, 2))).lstrip("0x").upper()

    @staticmethod
    def convertToString(value: ndarray) -> str:
        """
        Convert a np array of 1 and 0 into a string of the
        UTF8 encoded value of the array
        """
        v = ""
        for k in range(8, len(value) + 1, 8):
            v += str(
                int.to_bytes(
                    int("".join(str(i) for i in value[k - 8 : k]), 2),
                    byteorder="big",
                ),
                "ASCII",
            )
        return v

    @staticmethod
    def convertToArray(value: str, conv_type: str) -> ndarray:
        """
        Convert a str into a ndarray of 1 and 0 using
        the conversion type given ("Bits" / "Hex" / "ASCII/UTF-8")
        """
        match conv_type:
            case "Bits":
                return CommunicationInterface.convertBitString(value)
            case "Hex":
                return CommunicationInterface.convertHexString(value)
            case "ASCII/UTF-8":
                return CommunicationInterface.convertString(value)
            case _:
                raise ValueError()

    @staticmethod
    def convertToStringM(value: ndarray, conv_type: str) -> str:
        """
        Convert a ndarray of 1 and 0 into a str using
        the conversion type given ("Bits" / "Hex" / "ASCII/UTF-8")
        """
        match conv_type:
            case "Bits":
                return CommunicationInterface.convertToBitString(value)
            case "Hex":
                return CommunicationInterface.convertToHexString(value)
            case "ASCII/UTF-8":
                return CommunicationInterface.convertToString(value)
            case _:
                raise ValueError()

    @staticmethod
    def encapsulate(value: ndarray, cap_type) -> ndarray:
        """
        Encapsulate the data into a frame
        the type of te frame is deterined by cap_type
        ("Plain" / "CAN" / "ENCcan")
        """
        match cap_type:
            case "Plain":
                return value
            case "CAN":
                x = min(64, len(value))
                return CanFrame(0x123, value[:x], False, False).ToIntArray()
            case "ENCcan":
                x = min(64, len(value))
                c = CanFrame(0x123, value[:x], False, False)
                return IOronSTD1Frame(0x456, c, False, False).ToIntArrayWKey(
                    b"sau6ctrobon88130zer"
                )
            case _:
                raise ValueError()

    @staticmethod
    def decapsulate(value: ndarray, cap_type) -> ndarray:
        """
        Retrieve the data encapsulated in a frame
        the type of the frame is deterined by cap_type
        ("Plain" / "CAN" / "ENCcan")
        """
        print(list(value))
        match cap_type:
            case "Plain":
                return value
            case "CAN":
                v = CanFrame.FromIntArray(CommunicationInterface.trimCan(value))
                print("decoded :", v)
                return v.data

            case "ENCcan":
                return IOronSTD1Frame.FromIntArrayWKey(
                    CommunicationInterface.trimCan(value), b"sau6ctrobon"
                ).data_.data
            case _:
                raise ValueError()

    @staticmethod
    def trimCan(value: ndarray) -> ndarray:
        """
        This method allow to trim excess data from a raw frame
        for CAN format
        """
        compteur = 0
        for i in range(0, len(value)):
            if value[i] == 0:
                compteur = 0
            else:
                compteur += 1
            if compteur == 11:
                print(value[0 : i + 1])
                return value[0 : i + 1]
        return value

    def emergencyStop(self):
        """
        Never used, do not need to implement it.
        """
        pass
