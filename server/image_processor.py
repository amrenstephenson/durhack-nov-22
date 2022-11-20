from abc import ABC, abstractmethod
from PIL import Image, ImageEnhance
import os
import socket


class Color():
    def __init__(self, r, g, b):
        for component in (r, g, b):
            if component < 0 or component > 255:
                raise ValueError("Each color component must be between 0 and 255 inclusive.")
        self.r = r
        self.g = g
        self.b = b


class ImageProcessor(ABC):
    def __init__(self, filepath: str):
        self.filepath = filepath
        if not os.path.exists(filepath):
            raise FileNotFoundError("Could not find image file.")

    @abstractmethod
    def get_width() -> int:
        pass

    @abstractmethod
    def get_height() -> int:
        pass

    @abstractmethod
    def read_pixel(self, x: int, y: int) -> Color:
        pass

    @abstractmethod
    def write_pixel(self, x: int, y: int, color: Color):
        pass

    @abstractmethod
    def crop(self, left: int, upper: int, right: int, lower: int):
        pass

    @abstractmethod
    def resize_down(self, target_width: int, target_height: int):
        pass

    @abstractmethod
    def increase_contrast(self, amount: float):
        pass

    @abstractmethod
    def save_to_file(self, filepath):
        pass

    def to_rgb565(self):
        data = bytearray()
        for y in range(self.get_height()):
            for x in range(self.get_width()):
                color = self.read_pixel(x, y)

                r = ((color.r * 31) // 255) << 11
                g = ((color.g * 63) // 255) << 5
                b = ((color.b * 31) // 255)

                flipped = socket.htons(r + g + b)
                data.append(flipped >> 8)
                data.append(flipped & 0x00ff)
        return data

    def set_black_point(self, threshold: int):
        if threshold < 0 or threshold > 255:
            raise ValueError("The threshold should be between 0 and 255 inclusive.")

        for y in range(self.get_height()):
            for x in range(self.get_width()):
                colour = self.read_pixel(x, y)
                if colour.r < threshold and colour.g < threshold and colour.b < threshold:
                    self.write_pixel(x, y, Color(0, 0, 0))


class ImageProcessorPIL(ImageProcessor):
    def __init__(self, filepath):
        super().__init__(filepath)
        self.pil_image = Image.open(filepath)

    def read_pixel(self, x: int, y: int) -> Color:
        pixel_color = self.pil_image.getpixel((x, y))
        return Color(pixel_color[0], pixel_color[1], pixel_color[2])

    def write_pixel(self, x: int, y: int, color: Color):
        self.pil_image.putpixel((x, y), (color.r, color.g, color.b))

    def crop(self, left, upper, right, lower):
        self.pil_image = self.pil_image.crop((left, upper, right, lower))

    def resize_down(self, new_width: int, new_height: int):
        self.pil_image.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)

    def increase_contrast(self, amount: float):
        image_filter = ImageEnhance.Contrast(self.pil_image)
        self.pil_image = image_filter.enhance(amount)

    def get_width(self) -> int:
        return self.pil_image.width

    def get_height(self) -> int:
        return self.pil_image.height

    def save_to_file(self, filepath):
        self.pil_image.save(filepath, quality=100, optimize=True)


ImageProcessorPIL("orange.jpg")
