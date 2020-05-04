from pytraits.image.io import *
from pytraits.image.region import *
from test import *

inames = [
    "random",
    "randomborder",
    "spiral",
]

_i = make_idict(inames)


def _test_random():
    fac = 10
    img, _ = random_grid(src_size, classes=10, factor=fac)
    write_image(_i["random"], img)
    print(f"random: {fac} classes seeded")


def _test_generator():
    partitioner = Generator_RB(src_size, 10)
    img = partitioner.execute()
    write_image(_i["randomborder"], img)
    print(f"randomborder: written")

    partitioner = Generator_Spiral(src_size)
    img = partitioner.execute()
    write_image(_i["spiral"], img)
    print(f"spiral: written")


def test():
    printPreamble(__file__)
    _test_random()  # random seeds
    _test_generator()  # decision region generators
