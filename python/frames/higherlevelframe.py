import numpy as np
from frames.can import CanFrame
from frames.crypto import AESEncryption
from math import ceil


class IOronSTD1Frame(CanFrame):
    data_: CanFrame

    def __init__(
        self, ident: int, data_: CanFrame, request: bool = False, ack: bool = False
    ):
        self.ident = ident
        self.request = request
        self.data_ = data_
        self.ack = ack

    def ToIntArrayWKey(self, key: bytes) -> np.ndarray:
        c = AESEncryption(key[:16])
        r, iv = c.Encrypt(AESEncryption.IntArrayToBytes(self.data_.ToIntArray()))
        # print(r, iv)
        # print(len(r), len(iv))
        arrr = AESEncryption.BytesToIntArray(r)
        arriv = AESEncryption.BytesToIntArray(iv)
        temp_data = np.zeros(8, int)
        ctr = len(r)
        for i in range(7, -1, -1):
            temp_data[i] = ctr % 2
            ctr //= 2
        self.data = np.concatenate((temp_data, arrr, arriv))
        print(self.data)

        return self.UNSAFE_ToIntArray()

    @staticmethod
    def FromIntArrayWKey(array: np.ndarray, key: bytes) -> "IOronSTD1Frame":
        ok = IOronSTD1Frame.FromIntArray(array)

        print(ok)

        length = 0
        for i in range(0, 8):
            length = length * 2 + ok.data[i]

        print(length)

        arrr = np.zeros(length * 8, int)
        for i in range(0, length * 8):
            arrr[i] = ok.data[8 + i]

        arriv = np.zeros(128, int)
        for i in range(0, 128):
            arriv[i] = ok.data[length * 8 + 8 + i]

        r = AESEncryption.IntArrayToBytes(arrr)
        iv = AESEncryption.IntArrayToBytes(arriv)

        # print(arrr)
        # print(r, iv)
        # print(len(r), len(iv))

        t = AESEncryption(key[:16]).Decrypt(r, iv)

        arrt = AESEncryption.BytesToIntArray(t)

        ctr = len(arrt) - 1

        while arrt[ctr] == 0 and ctr > 0:
            ctr -= 1

        print(arrt[: ctr + 1])

        insider = CanFrame.FromIntArray(arrt[: ctr + 1])

        return IOronSTD1Frame(ok.ident, insider, request=ok.request, ack=ok.ack)

    def UNSAFE_ToIntArray(self) -> np.ndarray:
        tmp = np.zeros(60 + len(self.data), int)
        # arbitration field
        id = self.ident
        for i in range(0, 11):
            tmp[1 + i] = id % 2
            id = id // 2
        # RTR bit
        tmp[12] = self.request
        # IDE bit
        tmp[13] = 0
        # r0 bit
        tmp[14] = 0
        # DLC quad
        dlc = ceil(len(self.data) / 8)

        for i in range(0, 6):
            tmp[15 + i] = dlc % 2
            dlc = dlc // 2

        # data field
        cursor = 21
        if len(self.data) % 8 != 0:
            for i in range(0, 8 - (len(self.data) % 8)):
                tmp[21 + len(self.data) + i]
                cursor += 1
        for i in range(0, len(self.data)):
            tmp[cursor + i] = self.data[i]
        cursor += len(self.data)

        # CRC
        crc = self.CRC15_CAN_calc(tmp[:cursor], 0)

        for i in range(0, 15):
            tmp[cursor + i] = crc[i]
        tmp[cursor + 15] = 1
        cursor += 16
        # ACK
        tmp[cursor] = int(self.ack)
        tmp[cursor + 1] = 1
        cursor += 2
        # EOF and IFS
        for i in range(0, 10):
            tmp[cursor + i] = 1
        cursor += 10

        # Bit Stuffing
        out = self.BitStuff(tmp[: cursor - 13])

        return np.concatenate((out, tmp[cursor - 13 : cursor]))

    @staticmethod
    def FromIntArray(array: np.ndarray) -> "CanFrame":
        is_ack = False
        is_request = False
        for i in range(0, 10):
            if array[len(array) - i - 1] == 0:
                raise ValueError("the given frame has no EOF and IFS or it's invalid")
        if array[len(array) - 11] != 1:
            raise ValueError("ACK delimiter is not 1")
        is_ack = array[len(array) - 12]

        if array[len(array) - 13] != 1:
            raise ValueError("CRC delimiter is not 1")
        unstuffed = CanFrame.BitUnstuff(array[: len(array) - 13])

        crc = unstuffed[len(unstuffed) - 15 :]

        other = unstuffed[: len(unstuffed) - 15]

        if not CanFrame.CRC15_CAN_check(other, crc):
            raise ValueError("Did not pass CRC_check")
        ident = 0
        for i in range(11, 0, -1):
            ident = ident * 2 + unstuffed[i]

        is_request = unstuffed[12]
        # DLC
        data_len = 0
        for i in range(20, 14, -1):
            data_len = data_len * 2 + unstuffed[i]

        # DATA
        data = np.zeros(data_len * 8, int)
        for i in range(21, 21 + (data_len * 8)):
            data[i - 21] = unstuffed[i]

        return CanFrame(ident, data, request=is_request, ack=is_ack)

    def __str__(self) -> str:
        return f"<IOronSTD1Frame Ident : {hex(self.ident)} | ack : {self.ack} | request : {self.request} | data :\n\t{self.data_}\n>"


if __name__ == "__main__":
    fr = IOronSTD1Frame(
        0x123,
        data_=CanFrame(
            0x456, np.array([1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1], int)
        ),
    )
    key = b"zertyuiopfkdjhfdhfk"
    print(fr)
    encfr = fr.ToIntArrayWKey(key)
    print("encfr :", encfr)
    print(len(encfr))
    dencfr = IOronSTD1Frame.FromIntArrayWKey(encfr, key)
    print(dencfr)
