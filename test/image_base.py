import sys
import cv2
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
    'masked',
    'overlay',
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


def _test_mask():
    top = create_mono_colored_image(src_size, 3, (255, 0, 0))  # blue
    bg = create_mono_colored_image(src_size, 3, (0, 0, 255))
    mask = create_mono_colored_image(src_size, 1, 0)
    mask = cv2.circle(mask, center = (src_size.x // 2, src_size.y // 2), radius = 20, color = 255, thickness = cv2.FILLED)
    img = overlay_images(top, bg, mask)
    write_image(_i['masked'], img)
    print(f'masked: blue circle on red background')


def _test_overlay():
    angle = 15 * np.pi / 180
    img = create_mono_colored_image(src_size, 3, (0, 200, 0))
    img = overlay_on_noisy_background(img, angle, dx0=0, dy0=0, dx1=0, dy1=0)
    write_image(_i['overlay'], img)
    print(f'overlay: 15 deg rotated green rect on noisy background')


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

    _test_mask()
    _test_overlay()

