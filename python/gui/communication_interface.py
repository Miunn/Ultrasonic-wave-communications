from numpy import ndarray, zeros, array
import time


class CommunicationInterface:
    addr: str

    def __init__(self, addr: str) -> None:
        self.addr = addr

    def emit(self, message: ndarray, freq: float, cyc: int) -> int:
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
    ) -> tuple[int, ndarray, list[tuple[list[float], str, str]]]:
        time.sleep(5)
        return (0, zeros(2, int), [([], "red", "Name")])

    @staticmethod
    def convertBitString(value: str) -> ndarray:
        sanitized_value = "".join(c for c in value if c in "01")
        result = zeros(len(sanitized_value), int)
        for i in range(0, len(sanitized_value)):
            result[i] = int(sanitized_value[i])
        return result

    @staticmethod
    def convertHexString(value: str) -> ndarray:
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
        return "".join(str(i) for i in value)

    @staticmethod
    def convertToHexString(value: ndarray) -> str:
        string = "".join(str(i) for i in value)
        string = string[: len(string) - len(string) % 8]
        return str(hex(int(string, 2))).lstrip("0x").upper()

    @staticmethod
    def convertToString(value: ndarray) -> str:
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
        match conv_type:
            case "Bits":
                return CommunicationInterface.convertToBitString(value)
            case "Hex":
                return CommunicationInterface.convertToHexString(value)
            case "ASCII/UTF-8":
                return CommunicationInterface.convertToString(value)
            case _:
                raise ValueError()

    def emergencyStop(self):
        pass


if __name__ == "__main__":
    a = "10100011101010101001010"
    b = CommunicationInterface.convertToBitString(
        CommunicationInterface.convertBitString(a)
    )
    print(a, a == b, b)

    a = "DEADBEEF"

    h = CommunicationInterface.convertHexString(a)
    b = CommunicationInterface.convertToHexString(h)
    print(a, h, a == b, b)

    a = "bonjoir"
    b = CommunicationInterface.convertToString(CommunicationInterface.convertString(a))
    print(a, a == b, b)
