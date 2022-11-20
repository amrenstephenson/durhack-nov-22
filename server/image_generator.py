from PIL import Image
import os
import socket


class ImageGenerator():
    def __init__(self) -> None:
        self.SCRIPT_DIR = os.path.dirname(__file__)

    def to_bytes(self, image_path):
        data = bytearray()
        image = Image.open(image_path)
        for y in range(135):
            for x in range(240):
                colour = image.getpixel((x, y))

                r = ((colour[0] * 31) // 255) << 11
                g = ((colour[1] * 63) // 255) << 5
                b = ((colour[2] * 31) // 255)
                flipped = socket.htons(r + g + b)
                data.append(flipped >> 8)
                data.append(flipped & 0x00ff)
        return data
