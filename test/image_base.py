import cv2
from pytraits.image.io import *
from pytraits.image.base import *
from test import *

inames = [
    "random_border",
]

_i = make_idict(inames)


onames = [
    "masked",
    "transformed_mask",
    "overlay",
    "colormap",
]

_o = make_odict(onames)


def _test_transformed_mask():
    angle_deg = -20
    angle = angle_deg * np.pi / 180
    img = create_mono_colored_image(src_size, 1, 0)
    trafo = transformation_from_angle(img, angle)
    rot = trafo[0]  # rotational part
    dst_size = [trafo[2], trafo[1]]  # use rectangular hull of rotated source

    img = create_transformed_rect_mask(src_size, rot, dst_size, flags=cv2.INTER_NEAREST)
    write_image(_o["transformed_mask"], img)
    print(f"transformed_mask: rotated white rectangle (angle = {angle_deg} degrees)")


def _test_mask():
    top = create_mono_colored_image(src_size, 3, (255, 0, 0))  # blue
    bg = create_mono_colored_image(src_size, 3, (0, 0, 255))
    mask = create_mono_colored_image(src_size, 1, 0)
    radius = 20
    mask = cv2.circle(
        mask,
        center=(src_size[1] // 2, src_size[0] // 2),
        radius=radius,
        color=255,
        thickness=cv2.FILLED,
    )
    img = overlay_images(top, bg, mask)
    write_image(_o["masked"], img)
    print(f"masked: blue circle (r={radius}) on red background")


def _test_overlay():
    angle_deg = 15
    angle = angle_deg * np.pi / 180
    img = create_mono_colored_image(src_size, 3, (0, 200, 0))
    img = overlay_on_noisy_background(img, angle, dx0=0, dy0=0, dx1=0, dy1=0)
    write_image(_o["overlay"], img)
    print(
        f"overlay: rotated green rectangle (angle = {angle_deg} degrees) on noisy background"
    )


def _test_colormap():
    img = read_image(_i["random_border"])
    img = cv2.normalize(img, img, 1, 255, cv2.NORM_MINMAX)
    img = colormapped_image(img, "PuBuGn")
    write_image(_o["colormap"], img)
    print(f"colormap: colormapped grayscale image")


def test():
    printPreamble(__file__)
    _test_mask()  # creating masked image
    _test_transformed_mask()  # creating transformed rectangular mask
    _test_overlay()  # overlay image with transformed 2nd image
    _test_colormap()  # false color creation from matplotlib color map
