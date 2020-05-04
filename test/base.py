import cv2
import albumentations as A
from pytraits.base.directory import *
from test import *


def _test_filter():
    def f(fname):
        return len(fname) < 20

    fl = filter_directory(Path("../"), f)
    print(fl)


def _test_walker():
    def resizeImage(ifile, ofile, scale_x, scale_y):
        """
        Resize single image file to new (size x size)
        image and save the result to disk.
        """
        image = cv2.imread(ifile, -1)
        dims = image.shape
        aug = A.Resize(int(dims[0] * scale_y), int(dims[1] * scale_x))
        new_image = aug(image=image)["image"]
        cv2.imwrite(ofile, new_image)

    dw = DirectoryWalker(test_data_dir / "dirwalk", out_dir / "dirwalk")
    dw.createFilteredData(resizeImage, scale_x=0.5, scale_y=0.25)


def test():
    printPreamble(__file__)

    _test_filter()
    _test_walker()
