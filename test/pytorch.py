from pytraits.pytorch import cuda
from test import *


def test():
    printPreamble(__file__)

    cuda.info()
