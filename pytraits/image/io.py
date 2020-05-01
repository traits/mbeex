import os
from pathlib import Path
import cv2


def _s(fname):  # OpenCV doesn't understand Path objects
    return str(fname)


def read_image(fname, enforce_color=False):
    """
    Read image from file. For enforce_color==True, the image is converted to BGR:
    2 color channels are added for grayscale images, an alpha channel is ignored
    for corresponding formats.
    """

    f = cv2.IMREAD_UNCHANGED
    if enforce_color:
        f = cv2.IMREAD_COLOR
    ret = cv2.imread(_s(fname), flags=f)
    # TODO: Make a decision regarding general RGB/BGR handling
    # if len(ret.shape) > 2:
    #   if ret.shape[2] == 3:
    #       ret = cv2.cvtColor(ret, cv2.COLOR_BGR2RGB)   # BGR -> RGB
    #   elif ret.shape[2] == 4:
    #       ret = cv2.cvtColor(ret, cv2.COLOR_BGRA2RGBA)
    return ret


def write_image(fname, img):
    """
    Write image to file and create all intermediate directories, if not existing.
    """

    path = Path(fname)
    dir = path.parent
    if not dir.exists():
        os.makedirs(dir)
    cv2.imwrite(_s(fname), img)
