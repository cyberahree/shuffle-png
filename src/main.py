from zlib import crc32

import random

PNG_CHUNKS = [b"IHDR", b"IDAT", b"IEND", b"PLTE", b"tRNS", b"cHRM", b"bKGD", b"gAMA", b"iCCP", b"sBIT", b"sRGB", b"tEXt", b"zTXt", b"tIME"]
PNG_MAGIC = bytes.fromhex("89504e470d0a1a0a")

class Chunk:
    length: bytes
    type: bytes
    data: bytes
    crc: bytes
    pos: bytes

class BytesReader:
    def __init__(self, data: bytes):
        self.data = data
        self.cursor = 0

    def read(self, bytes: int, parse: type = None) -> int | bytes:
        if bytes < 1:
            return b""

        try:
            data = self.data[self.cursor:self.cursor + bytes]
            self.cursor += bytes

            if parse is int:
                return int.from_bytes(data, "big")

            return data
        except IndexError:
            print(f"Error reading {bytes} bytes at position {self.cursor}")
            return b""

class PNGShuffle:
    def __init__(self):
        pass

    def _make_crc32(self, data: bytes) -> bytes:
        """
        Calculate the CRC32 checksum of the given data.

        :param data: The data to calculate the checksum for.

        :return: The CRC32 checksum as a 4-byte string.
        """
        return crc32(data).to_bytes(4, "big")

    def _collect_chunks(self, bytes: bytes, shuffled: bool = False) -> dict[int, Chunk]:
        """
        Collects the chunks from a PNG byte array.
        Unshuffles the chunks if the PNG is shuffled.

        :param bytes: The PNG byte array to collect chunks from.
        :param shuffled: Whether the PNG is shuffled or not.

        :return: A dictionary of chunks, where the key is the chunk position and the value is a list of chunk data.
        """
        reader = BytesReader(bytes)
        chunks = {}

        while reader.cursor < len(bytes):
            # collect chunk length, type and data
            length, b_type = reader.read(4, int), reader.read(4)
            b_data = reader.read(length)
            
            # read the crc if not suffled, else generate one
            b_crc = reader.read(4) if not shuffled else self._make_crc32(b_type + b_data)

            # read the position if shuffled, else get the next position
            # in the dictionary
            position = reader.read(4, int) if shuffled else len(chunks)

            print(f"[{b_type.decode()} {('0' + str(position))[-2:]}] L {('00000000' + str(length))[-8:]} CRC {b_crc.hex()}")

            data = Chunk()

            data.length = length.to_bytes(4, "big")
            data.type = b_type
            data.data = b_data
            data.crc = b_crc
            data.pos = position.to_bytes(4, "big")

            chunks[position] = data

        return chunks

    def unshuffle(self, data: bytes) -> bytes:
        """
        Unshuffles a PNG byte array's chunks.

        :param data: The PNG byte array to unshuffle.

        :return: The unshuffled PNG byte array.
        """
        # check for magic number
        if data[:8] != PNG_MAGIC:
            raise ValueError("Invalid PNG file")
        
        # collect chunks
        chunks = self._collect_chunks(data[8:], True)
        b_new_file = PNG_MAGIC

        # append the chunks in order
        for i in range(len(chunks)):
            data = chunks[i]

            b_new_file += data.length + data.type + data.data + data.crc
        
        return b_new_file

    def shuffle(self, data: bytes, seed: any = None) -> bytes:
        """
        Suffles a PNG byte array's chunks.

        :param data: The PNG byte array to shuffle.

        :return: The shuffled PNG byte array.
        """
        # check for magic number
        if data[:8] != PNG_MAGIC:
            raise ValueError("Invalid PNG file")
        
        # collect chunks
        chunks = self._collect_chunks(data[8:])
        ihdr = chunks.pop(0)
        iend = chunks.pop(len(chunks) - 1)
        b_new_file = PNG_MAGIC

        # rearrange the chunks
        random.seed(seed)
        keys = list(chunks.values())
        random.shuffle(keys)

        # append the IEND first
        b_new_file += iend.length + iend.type + iend.data + iend.crc

        # append the chunks in order
        for i in range(len(keys)):
            data = keys[i]

            b_new_file += data.length + data.type + data.data + data.pos
        
        # append the IHDR last
        # (i know we already moved the iend to the beginning, that works
        # but make it doubler annoying and put the IHDR at the end
        # additionally, if the renderer is smart enough, and the
        # rng is unfortunate enough, it might be able to render the image
        # correctly)
        b_new_file += ihdr.length + ihdr.type + ihdr.data + ihdr.crc

        return b_new_file

def get_bytes(file: str) -> bytes:
    """
    Get the bytes of a file.
    :param file: The file to get the bytes from.
    :return: The bytes of the file.
    """
    with open(file, "rb") as f:
        return f.read()

if __name__ == "__main__":
    parser = PNGShuffle()

    img_bytes = get_bytes("lol.png")
    shuffled_bytes = parser.shuffle(img_bytes)

    with open("example1.png", "wb") as f:
        f.write(shuffled_bytes)
