import os
from pathlib import Path
import numpy as np
import cv2

from pytraits.base import Size2D


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
    return cv2.imread(_s(fname), flags=f)


def write_image(fname, img):
    """ Write image to file and create all intermediate directories, if not existing. """
    path = Path(fname)
    dir = path.parent
    if not dir.exists():
        os.makedirs(dir)
    cv2.imwrite(_s(fname), img)


def image_size(img):
    """ Returns (xsize,ysize) instead numpy's img.shape[:2] (would be (ysize,xsize) instead) """
    return Size2D(*img.shape[1::-1])  # http://stackoverflow.com/questions/25000159/how-to-cast-tuple-into-namedtuple


def image_area(img):
    return img.shape[0] * img.shape[1]


def create_mono_colored_image(size, depth, color):
    """ Return new mono-colored RGB (depth==3) or grayscale (depth == 1) image """
    img = np.empty((size.y, size.x, depth), np.uint8)
    img[:] = color
    return img


def create_noisy_image(size, depth):
    """ Return white-noised color image """
    imarray = np.random.randint(0, 256, size=(size.y, size.x, depth)).astype('uint8')
    return imarray


def calc_rotate_parameters(img, angle):
    """
    Return transformation matrix and new (width,height) for an image, rotated by 
    some angle around the center. The matrix will contain the rotation and the 
    necessary translation for adjusting the center point.
    Be aware, that this transformation is the backward (inverse) transformation
    (dst -> img), because OpenCV's warpAffine function utilizes this form. 

    img -- source image
    angle -- rotation angle (radians)
    """

    w = img.shape[1]
    h = img.shape[0]
    # now calculate new image width and height
    nw = abs(np.sin(angle) * h) + abs(np.cos(angle) * w)
    nh = abs(np.cos(angle) * h) + abs(np.sin(angle) * w)
    # ask OpenCV for the rotation matrix
    rot_mat = cv2.getRotationMatrix2D((nw * 0.5, nh * 0.5), np.degrees(angle), 1.)
    # calculate the move from the old center to the new center combined
    # with the rotation
    rot_move = np.dot(rot_mat, np.array([(nw - w) * 0.5, (nh - h) * 0.5, 0]))
    # the move only affects the translation, so update the translation
    # part of the transform
    rot_mat[0, 2] += rot_move[0]
    rot_mat[1, 2] += rot_move[1]
    return [rot_mat, int(np.math.ceil(nw)), int(np.math.ceil(nh))]


def create_mask(src_size, trafo, dst_size, flags):
    img2gray = create_mono_colored_image(src_size, 1, 255)
    img2gray = cv2.warpAffine(img2gray, trafo, dst_size, flags=flags)
    ret, mask = cv2.threshold(img2gray, 0, 255, cv2.THRESH_BINARY)
    return cv2.bitwise_not(mask)


def overlay_on_noisy_background(img, angle, dx0=0, dy0=0, dx1=0, dy1=0):
    """ 
    Put transformed image on white-noise background. 
    Offsets must be always >= 0.

    img -- source image
    angle -- rotation angle (radians)
    dx0 -- x offset (left)
    dy0 -- y offset (top)
    dx1 -- x offset (right)
    dy1 -- y offset (bottom)
    """
    par = calc_rotate_parameters(img, angle)

    # adjust matrix translation part
    par[0][0, 2] += dx0
    par[0][1, 2] += dy0
    par[1] += dx0 + dx1
    par[2] += dy0 + dy1

    bg = create_noisy_image(Size2D(par[1], par[2]), img.shape[2])
    return overlay_transformed_image(img, bg, par[0])


def overlay_transformed_image(img, bg, trafo):
    flag = cv2.INTER_NEAREST
    mask = create_mask(image_size(img), trafo, image_size(bg), flags=flag)
    img = cv2.warpAffine(img, trafo, image_size(bg), flags=flag)
    return overlay_images(img, bg, mask)


def overlay_images(top, bg, mask):
    """
    Copy image onto some background, using a mask. All argument images must have
    the same size, otherwise an exception is called

    top -- foreground image
    bg -- background image
    mask -- mask
    """
    if (image_size(bg) != image_size(top) or image_size(bg) != image_size(mask)):
        raise Exception('image size mismatch')
    masked_bg = cv2.bitwise_and(bg, bg, mask=mask)
    return cv2.add(masked_bg, top)
