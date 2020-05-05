import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.colors as mcol

from pytraits.base import Size2D


class ImageException(Exception):
    """
    General image exception
    """

    pass


def image_size(img):
    """
    Returns (xsize,ysize) instead numpy's img.shape[:2]
    (would be (ysize,xsize) instead)
    """

    return Size2D(
        *img.shape[1::-1]
    )  # http://stackoverflow.com/questions/25000159/how-to-cast-tuple-into-namedtuple


def image_area(img):
    """
    Image area in pixels
    """

    return img.shape[0] * img.shape[1]


def create_mono_colored_image(size, depth, color):
    """
    Return new mono-colored (depth==3) [with alpha for depth==4]
    or grayscale (depth == 1) image
    """

    img = np.empty((size.y, size.x, depth), np.uint8)
    img[:] = color
    return img


def create_noisy_image(size, depth):
    """
    Return image with every pixel channel randomized
    """

    imarray = np.random.randint(0, 256, size=(size.y, size.x, depth)).astype("uint8")
    return imarray


def transformation_from_angle(img, angle):
    """
    Return transformation matrix and new (width,height) for an image, rotated by 
    some angle around the center. The matrix will contain the rotation and the 
    necessary translation for adjusting the center point.
    Be aware, that this transformation is the backward (inverse) transformation
    (dst -> img), because OpenCV's warpAffine function utilizes this form. 

    Parameters:
        :img:       source image
        :angle:     rotation angle (radians)
        :return:    transformation matrix for OpenCV warpAffine
    """

    w = img.shape[1]
    h = img.shape[0]
    # now calculate new image width and height
    nw = abs(np.sin(angle) * h) + abs(np.cos(angle) * w)
    nh = abs(np.cos(angle) * h) + abs(np.sin(angle) * w)
    # ask OpenCV for the rotation matrix
    rot_mat = cv2.getRotationMatrix2D((nw * 0.5, nh * 0.5), np.degrees(angle), 1.0)
    # calculate the move from the old center to the new center combined
    # with the rotation
    rot_move = np.dot(rot_mat, np.array([(nw - w) * 0.5, (nh - h) * 0.5, 0]))
    # the move only affects the translation, so update the translation
    # part of the transform
    rot_mat[0, 2] += rot_move[0]
    rot_mat[1, 2] += rot_move[1]
    return [rot_mat, int(np.math.ceil(nw)), int(np.math.ceil(nh))]


def create_transformed_rect_mask(src_size, trafo, dst_size, flags):
    """
    Create white grayscale image, transform it into black target and return result image
    
    Parameters:
        :src_size:  rectangular mask size before transformation
        :trafo:     affine transformation for cv2.warpAffine
        :dst_size:  target size (pre-calculated)
        :flags:     cv2.warpAffine flags
        :return:    transformed rectangular mask (white==255) on black background
    """
    img = create_mono_colored_image(src_size, 1, 255)
    img = cv2.warpAffine(img, trafo, dst_size, flags=flags)
    _, mask = cv2.threshold(
        img, 0, 255, cv2.THRESH_BINARY
    )  # set all pixels > 0 to white (255)
    return mask


def overlay_on_noisy_background(img, angle, dx0=0, dy0=0, dx1=0, dy1=0):
    """ 
    Put transformed image on white-noise background. 
    Offsets must be always >= 0.

    Parameters:
        :img:   source image
        :angle: rotation angle (radians)
        :dx0:   x offset (left)
        :dy0:   y offset (top)
        :dx1:   x offset (right)
        :dy1:   y offset (bottom)
    """

    par = transformation_from_angle(img, angle)

    # adjust matrix translation part
    par[0][0, 2] += dx0
    par[0][1, 2] += dy0
    par[1] += dx0 + dx1
    par[2] += dy0 + dy1

    bg = create_noisy_image(Size2D(par[1], par[2]), img.shape[2])
    return overlay_transformed_image(img, bg, par[0])


def overlay_transformed_image(top, bg, trafo):
    flag = cv2.INTER_NEAREST
    mask = create_transformed_rect_mask(
        image_size(top), trafo, image_size(bg), flags=flag
    )
    top = cv2.warpAffine(top, trafo, image_size(bg), flags=flag)
    return overlay_images(top, bg, mask)


def overlay_images(top, bg, mask):
    """
    Copy image onto some background overwriting them using a mask. All argument images must have
    the same size, otherwise an exception is called.

    Parameters:
        :top:  foreground image
        :bg:   background image
        :mask: mask
    """

    if image_size(bg) != image_size(top) or image_size(bg) != image_size(mask):
        raise ImageException("image size mismatch")

    return cv2.copyTo(top, mask, bg)


def colormapped_image(img, matplot_map_name):
    """
    Applies matplotlib colormap to opencv grayscale image
    """

    cmap = plt.get_cmap(matplot_map_name)
    cmaplist = [cmap(i) for i in range(cmap.N)]

    # replace 1st entry by black
    cmaplist[0] = (
        0.0,
        0.0,
        0.0,
        1.0,
    )  # clip this later, if using 1.0 values for color components
    # colormap = mcol.LinearSegmentedColormap.from_list("pytraits", cmaplist, cmap.N)
    colormap = mcol.ListedColormap(cmaplist, "pytraits", cmap.N)
    cmap = colormap(img) * 2 ** 16
    # np.clip(cmap, 0, 2 ** 16 - 1, out=cmap)  # avoid overflows (see above)
    result = cmap.astype(np.uint16)[:, :, :3]
    return cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
