import cv2
from pytraits.base import Size2D
from pytraits.image.io import *
from pytraits.image.base import *
from pytraits.image.region import *
from test import *

inames = [
    'masked',
    'transformed_mask',
    'overlay',
    'random',
    'randomborder',
    'spiral',
]

_i = make_idict(inames)


def _test_transformed_mask():
    angle = -20 * np.pi / 180
    img = create_mono_colored_image(src_size, 1, 0)
    trafo = transformation_from_angle(img, angle)
    rot = trafo[0]  # rotational part
    dst_size = Size2D(trafo[1], trafo[2])  # use rectangular hull of rotated source

    img = create_transformed_rect_mask(src_size, rot, dst_size, flags = cv2.INTER_NEAREST)
    write_image(_i['transformed_mask'], img)
    print(f'transformed_mask: white rectangle rotated -20 degrees')


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
    print(f'overlay: green rectangle rotated 15 degrees on noisy background')


def _test_random():
    img, _ = random_grid(src_size, 10)
    write_image(_i['random'], img)
    print(f'random: 10 classes seeded')


def _test_generator():
    partitioner = Generator_1(src_size, 10)
    img = partitioner.execute()
    write_image(_i['randomborder'], img)
    print(f'randomborder: written')

    partitioner = Generator_2(src_size)
    img = partitioner.execute()
    write_image(_i['spiral'], img)
    print(f'spiral: written')


def test():
    _test_mask()                # creating masked image
    _test_transformed_mask()    # creating transformed rectangular mask
    _test_overlay()             # overlay image with transformed 2nd image
    _test_random()              # random seeds
    _test_generator()



