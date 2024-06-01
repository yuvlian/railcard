from PIL import Image, ImageDraw
import numpy as np
from urllib.request import urlopen

def img_from_url(url: str) -> Image.Image:
    return Image.open(urlopen(url))

def create_dark_block(width: int, height: int) -> Image.Image:
    return Image.new("RGBA", (width, height), (26, 26, 26))

def create_light_block(width: int, height: int, mode="RGBA") -> Image.Image:
    return Image.new(mode, (width, height), (41, 41, 41))

def create_rounded_mask(size: tuple[int, int], radius: int):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)

    draw.rounded_rectangle((0, 0, *size), radius, fill=255)
    return mask

def linear_gradient_img(size: tuple[int, int], color1: tuple[int, int, int], color2: tuple[int, int, int]) -> Image.Image:
    w, h = size
    gradient = np.zeros((h,w,3), np.uint8)

    gradient[:,:,0] = np.linspace(color1[0], color2[0], w, dtype=np.uint8)
    gradient[:,:,1] = np.linspace(color1[1], color2[1], w, dtype=np.uint8)
    gradient[:,:,2] = np.linspace(color1[2], color2[2], w, dtype=np.uint8)

    return Image.fromarray(gradient)

def linear_gradient_l_img(size: tuple[int, int], color1: int, color2: int) -> Image.Image:
    w, h = size
    gradient = np.zeros((h,w), np.uint8)

    gradient[:,:] = np.linspace(color1, color2, w, dtype=np.uint8)

    return Image.fromarray(gradient, "L")

def create_relic_background(size: tuple[int, int], rarity: int) -> Image.Image:
    color = (92, 255, 89)

    if rarity == 3: color = (92, 89, 255)
    if rarity == 4: color = (189, 123, 255)
    if rarity == 5: color = (255, 222, 89)

    img = Image.new("RGBA", size, color)
    mask = linear_gradient_l_img(size, 255, 255-204)

    img.putalpha(mask)
    return img
