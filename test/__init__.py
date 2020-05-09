from pathlib import Path

root = Path(__file__).parents[1]
out_dir = root / "_output"
test_data_dir = root / "test_data"
src_size = [200, 300]


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


def make_odict2(name, number):
    ret = {}
    for i in range(number):
        ret[i] = str(out_dir / f"{name}_{i:02d}") + ".png"
    return ret


def printPreamble(file):
    print(f"\n### {file}:\n")
