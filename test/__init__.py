from pathlib import Path
from pytraits.base import Size2D

root = Path(__file__).parents[1]
out_dir = root / "_output"
test_data_dir = root / "test_data"
src_size = Size2D(x=300, y=200)


def make_idict(names):
    ret = {}
    for i in names:
        ret[i] = str(test_data_dir / i) + ".png"
    return ret


def make_odict(names):
    ret = {}
    for i in names:
        ret[i] = str(out_dir / i) + ".png"
    return ret


def printPreamble(file):
    print(f"\n### {file}:\n")
