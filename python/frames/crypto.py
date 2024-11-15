from Crypto import Cipher
import numpy as np
from Crypto.Cipher import AES
import can as can


class AESEncryption:
    key: bytes

    def __init__(self, key) -> None:
        self.key = key

    @staticmethod
    def IntArrayToBytes(array: np.ndarray) -> bytes:
        # print("array :", array)
        if len(array) % 8 == 0:
            padded_array = array
        else:
            padded_array = np.concatenate(
                (array, np.array([0] * (8 - (len(array) % 8))))
            )
        # print("padded_array :", padded_array)
        result: bytes = b""
        for i in range(0, len(array), 8):
            byte: int = 0x00
            for j in range(0, 8):
                byte += padded_array[i + j] << (7 - j)
            # print(byte)
            result = result + int(byte).to_bytes(1, "little")
        return result

    @staticmethod
    def BytesToIntArray(bts: bytes) -> np.ndarray:
        result = np.zeros(len(bts) * 8, int)
        for i in range(0, len(bts)):
            one_byte = int(bts[i])
            for j in range(0, 8):
                result[i * 8 + (7 - j)] = one_byte % 2
                one_byte >>= 1
        return result

    def Encrypt(self, data: bytes) -> tuple[bytes, bytes]:
        cipher = AES.new(self.key, AES.MODE_OFB)

        iv = cipher.iv

        ciphertext = cipher.encrypt(data)

        return ciphertext, bytes(iv)

    def Decrypt(self, data: bytes, iv: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_OFB, iv=iv)
        plaintext = cipher.decrypt(data)
        return plaintext

    @staticmethod
    def CleanTrailingZeros(arr: np.ndarray):
        i = len(arr) - 1
        while arr[i] == 0:
            i -= 1
        return arr[: i + 1]


if __name__ == "__main__":
    stage0 = can.CanFrame(
        0x123, np.array([0, 1, 1, 1, 0, 1, 0, 1, 0, 1], int)
    ).ToIntArray()
    print(stage0)
    encoded_frame = AESEncryption.IntArrayToBytes(stage0)
    print(encoded_frame)
    stage1 = AESEncryption.CleanTrailingZeros(
        AESEncryption.BytesToIntArray(encoded_frame)
    )
    print(stage1)
    decoded_frame = can.CanFrame.FromIntArray(stage1)
    print(decoded_frame)

    crypter = AESEncryption(b"#cauhet#saucisses#onestpaschezlesbobos"[:16])

    encrypted_frame, iv = crypter.Encrypt(encoded_frame)

    print(len(iv))

    decrypted_frame = crypter.Decrypt(encrypted_frame, iv)

    stage2 = AESEncryption.CleanTrailingZeros(
        AESEncryption.BytesToIntArray(encoded_frame)
    )

    decoded_frame2 = can.CanFrame.FromIntArray(stage2)

    print(decoded_frame2)
