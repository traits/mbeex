import sys
from pathlib import Path
from pytraits.base import Size2D
from pytraits.image.base import *

# Python >= 3.7
if sys.version_info[0] >= 3 and sys.version_info[1] >= 7:
    pass
else:
    raise Exception("Python 3.7 or a more recent version is required.")

root = Path(__file__).parents[1]
out_dir = root / '_output'
src_size = Size2D(x = 300, y = 200)

inames = [
    'gray',
    'color',
    'color_with_alpha',
    'noise_color',
    'noise_gray',
]


def _make_idict():
    ret = {}
    for i in inames:
        ret[i] = str(out_dir / i) + '.png'
    return ret


_i = _make_idict()


def _r(fname, should):
    img = read_image(_i[fname])
    print(f'Read: {img.shape} depth should be: {should} ')


def test():
    img = create_mono_colored_image(src_size, 1, 100)
    write_image(_i['gray'], img)
    img = create_mono_colored_image(src_size, 3, (100, 0, 0))  # bgr
    write_image(_i['color'], img)
    img = create_mono_colored_image(src_size, 4, (0, 0, 100, 80))  # bgra
    write_image(_i['color_with_alpha'], img)
    img = create_noisy_image(src_size, 3)
    write_image(_i['noise_color'], img)
    img = create_noisy_image(src_size, 1)
    write_image(_i['noise_gray'], img)

    _r('gray', 1)
    _r('color', 3)
    _r('color_with_alpha', 4)
    _r('noise_color', 3)
    _r('noise_gray', 1)
