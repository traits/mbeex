from pytraits.base.directory import *
from test import *


def test():
    printPreamble(__file__)

    def f(fname):
        return len(fname) < 20

    fl = filter_directory(Path('../'), f)
    print(fl)
