# shuffle-png

This Python script ([`src/main.py`](src/main.py)) provides functionality to shuffle and unshuffle the chunks of a PNG image file. This can be used, for example, to obfuscate PNG files in a way that might deter simple analysis or to solve specific CTF challenges involving PNG file structure.

The script defines a `PNGShuffle` class that handles the core logic.

## Features

*   **Chunk Collection**: Parses a PNG byte stream, identifies, and collects all its chunks (e.g., `IHDR`, `PLTE`, `IDAT`, `IEND`).
*   **Shuffling (`shuffle` method)**:
    *   Reads a standard PNG file.
    *   Collects all its chunks.
    *   The `IHDR` (Image Header) and `IEND` (Image End) chunks are treated specially.
    *   Other chunks are randomly reordered.
    *   The shuffled PNG is constructed with the `IEND` chunk first, followed by the reordered data chunks (each appended with its original position), and finally the `IHDR` chunk at the very end.
    *   CRCs for data chunks are replaced by their original position index during shuffling.
*   **Unshuffling (`unshuffle` method)**:
    *   Reads a PNG file shuffled by this script.
    *   Collects chunks, reading their original positions.
    *   Reconstructs the PNG by placing chunks back in their original order.
    *   Recalculates CRCs for each chunk during the unshuffling process.
*   **CRC Recalculation**: Includes a helper to calculate CRC32 checksums for PNG chunks.

## How it Works

The script manipulates the order of PNG chunks. A standard PNG file starts with a magic number, followed by a series of chunks. Each chunk has a length, a type (e.g., `IHDR`, `IDAT`, `IEND`), data, and a CRC checksum.

*   **Shuffling**: The `shuffle` method takes a valid PNG, separates its chunks, shuffles most of them randomly, and then writes them back in a non-standard order. Specifically, it places `IEND` at the beginning of the chunk sequence (after the magic number), followed by the shuffled data chunks, and `IHDR` at the very end. For the shuffled data chunks, instead of their CRC, their original 4-byte position index is written.
*   **Unshuffling**: The `unshuffle` method reverses this process. It reads the shuffled file, uses the stored position indices to determine the correct order of chunks, reassembles them, and recalculates the correct CRC for each chunk.

## Usage

1.  Instantiate the `PNGShuffle` class.
2.  Use the `shuffle` method to shuffle the chunks of a PNG file.
3.  Use the `unshuffle` method to restore a shuffled PNG file to its original state.

```python
from .src.main import PNGShuffle, get_bytes

if __name__ == "__main__":
    parser = PNGShuffle()

    # Load an original PNG image
    original_img_bytes = get_bytes("original.png")

    # Shuffle the PNG
    shuffled_bytes = parser.shuffle(original_img_bytes, seed=42) # Optional seed for reproducible shuffle

    with open("shuffled_image.png", "wb") as f:
        f.write(shuffled_bytes)

    # Unshuffle the PNG
    unshuffled_bytes = parser.unshuffle(shuffled_bytes)

    with open("unshuffled_image.png", "wb") as f:
        f.write(unshuffled_bytes)

    print("PNG shuffling and unshuffling complete.")
```

This script relies on the standard `zlib` library for CRC32 calculations and `random` for shuffling.
