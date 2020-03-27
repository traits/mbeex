from pytraits.base.directory import *


def test():
    def f(fname):
        return len(fname) < 20

    fl = filter_directory(Path('../'), f)
    print(fl)
