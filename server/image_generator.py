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
                r = ((colour[0] * 31) // 255) << 11
                g = ((colour[1] * 63) // 255) << 5
                b = ((colour[2] * 31) // 255)
                data.append((r + g + b) >> 8)
                data.append((r + g + b) & 0x00ff)
        return data
