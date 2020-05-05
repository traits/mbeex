from pathlib import Path
from pytraits.image.base import *
from pytraits.image.io import *
from pytraits.base import Size2D
from test import *

onames = [
    "gray",
    "color",
    "color_with_alpha",
    "noise_color",
    "noise_gray",
]

_i = make_odict(onames)


def _r(fname, should):
    img = read_image(_i[fname])
    print(f"Read: {img.shape} depth should be: {should} ")


def _test_write():
    img = create_mono_colored_image(src_size, 1, 100)
    write_image(_i["gray"], img)
    img = create_mono_colored_image(src_size, 3, (100, 0, 0))  # bgr
    write_image(_i["color"], img)
    img = create_mono_colored_image(src_size, 4, (0, 0, 100, 80))  # bgra
    write_image(_i["color_with_alpha"], img)
    img = create_noisy_image(src_size, 3)
    write_image(_i["noise_color"], img)
    img = create_noisy_image(src_size, 1)
    write_image(_i["noise_gray"], img)


def _test_read():
    _r("gray", 1)
    _r("color", 3)
    _r("color_with_alpha", 4)
    _r("noise_color", 3)
    _r("noise_gray", 1)


def test():
    printPreamble(__file__)
    _test_write()  # writing images to file
    _test_read()  # reading images from file
