import numpy as np
from math import ceil

from numpy.core.multiarray import concatenate


class CanFrame:
    ident: int
    data: np.ndarray
    request: bool
    ack: bool

    def __init__(
        self, ident: int, data: np.ndarray, request: bool = False, ack: bool = False
    ):
        self.data = data
        self.ident = ident
        self.request = request
        self.ack = ack

    def ToIntArray(self) -> np.ndarray:
        if len(self.data) > 64:
            raise ValueError("data len cannot be more than 64 bits")
        tmp = np.zeros(108, int)
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
        for i in range(0, 4):
            tmp[16 + i] = dlc % 2
            dlc = dlc // 2

        # data field
        cursor = 19
        if len(self.data) % 8 != 0:
            for i in range(0, 8 - (len(self.data) % 8)):
                tmp[19 + len(self.data) + i]
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

        return concatenate((out, tmp[cursor - 13 : cursor]))

    @staticmethod
    def FromIntArray(array: np.ndarray) -> "CanFrame":
        is_ack = False
        is_request = False
        for i in range(0, 10):
            if array[len(array) - i - 1] == 0:
                raise ValueError("the given frame has no EOF and IFS or it's invalid")
        if array[len(array) - 11] != 1:
            raise ValueError("ACK delimiter is not 1")
        is_ack = array[len(array) - 12] == 1

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

        is_request = unstuffed[12] == 1
        # DLC
        data_len = 0
        for i in range(18, 15, -1):
            data_len = data_len * 2 + unstuffed[i]

        # DATA
        data = np.zeros(data_len * 8, int)
        for i in range(19, 19 + (data_len * 8)):
            data[i - 19] = unstuffed[i]
        return CanFrame(ident, data, request=is_request, ack=is_ack)

    @staticmethod
    def CRC15_CAN_calc(input: np.ndarray, initialfiller: int) -> np.ndarray:
        # print(input)
        cursor = 0
        pol = np.array([1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1], int)
        while input[cursor] == 0 and cursor < len(input):
            cursor += 1
        len_input = len(input) - cursor
        initial_padding = np.array((len(pol) - 1) * [initialfiller], int)
        # print(initial_padding)
        input_padded_array = np.concatenate((input[cursor:], initial_padding))
        while 1 in input_padded_array[:len_input]:
            cur_shift = 0
            while input_padded_array[cur_shift] == 0:
                cur_shift += 1
            for i in range(len(pol)):
                input_padded_array[cur_shift + i] = (
                    pol[i] ^ input_padded_array[cur_shift + i]
                )
        return input_padded_array[len_input:]

    @staticmethod
    def CRC15_CAN_check(input: np.ndarray, check_value: np.ndarray) -> bool:
        """Calculate the CRC check of a string of bits using a chosen polynomial."""
        pol = np.array([1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1], int)
        len_input = len(input)
        input_padded_array = np.concatenate((input, check_value))
        while 1 in input_padded_array[:len_input]:
            cur_shift = 0
            while input_padded_array[cur_shift] == 0:
                cur_shift += 1
            for i in range(len(pol)):
                input_padded_array[cur_shift + i] = (
                    pol[i] ^ input_padded_array[cur_shift + i]
                )
        # this line may be wrong : add [:len_input] as written in wikipedia if so
        return 1 not in input_padded_array

    # output should be zeroed if u want the bits that may be not used to be @ 0
    @staticmethod
    def BitStuff(input: np.ndarray) -> np.ndarray:
        output = np.zeros(ceil(len(input) * 1.25), int)
        current = input[0]
        same_counter = 1
        output[0] = input[0]
        out_index = 1
        for i in range(1, len(input)):
            output[out_index] = input[i]
            out_index += 1
            if input[i] == current:
                same_counter += 1
                if same_counter >= 5:
                    current = (current + 1) % 2
                    same_counter = 1
                    output[out_index] = current
                    out_index += 1
            else:
                same_counter = 1
                current = input[i]
        return output[:out_index]

    @staticmethod
    def BitUnstuff(input: np.ndarray) -> np.ndarray:
        output = np.zeros(len(input), int)
        current = input[0]
        same_counter = 1
        output[0] = input[0]
        out_index = 1
        i = 1
        while i < len(input):
            output[out_index] = input[i]
            if input[i] == current:
                same_counter += 1
                if same_counter >= 5:
                    i += 1
                    current = (current + 1) % 2
                    same_counter = 1
            else:
                same_counter = 1
                current = input[i]
            i += 1
            out_index += 1
        return output[:out_index]

    def __str__(self) -> str:
        return f"<CanFrame Ident : {hex(self.ident)} | ack : {self.ack} | request : {self.request} | message :\n\t{self.data}\n>"


if __name__ == "__main__":
    c = CanFrame(0x123, np.array([0, 0, 0, 0, 1, 0, 1, 0], int), request=True)
    print("Generating :", c)
    unc = CanFrame.FromIntArray(c.ToIntArray())
    print("Decrypting :", unc)
