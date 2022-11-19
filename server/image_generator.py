from PIL import Image
import os


class ImageGenerator():
    def __init__(self) -> None:
        self.SCRIPT_DIR = os.path.dirname(__file__)

    def generate_image(self):
        data = bytearray()
        image = Image.open(os.path.join(self.SCRIPT_DIR, "orange.jpg"))
        for y in range(135):
            for x in range(240):
                colour = image.getpixel((x, y))
                print(colour)
                r = int((colour[0] / 255) * 31) << 11
                g = int((colour[1] / 255) * 63) << 5
                b = int((colour[2] / 255) * 31)
                data.append((r + g + b) >> 8)
                data.append((r + g + b) & 0x00ff)
        return data
