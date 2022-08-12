from mbeex.image.base import *
from mbeex.image.io import *
from mbeex.image.region import *
from test import *


inames = [
    "random_border",
]
_i = make_idict(inames)


onames = [
    "random",
    "randomborder",
    "spiral",
    "randomborder_colored",
    "sampler_roi",
    "sampler_random_contour_t",
    "sampler_random_contour",
    "sampler_random_all",
    "sampler_grid",
]
_o = make_odict(onames)


def _test_random():
    fac = 10
    img, _ = random_grid(src_size, classes=10, factor=fac)
    write_image(_o["random"], img)
    print(f"random: {fac} classes seeded")


def _test_generator():
    partitioner = Generator_RB(src_size, 10)
    img = partitioner.execute()
    write_image(_o["randomborder"], img)
    print(f"randomborder: written")

    partitioner = Generator_Spiral(src_size)
    img = partitioner.execute()

    # import matplotlib.pyplot as plt

    # fig, ax = plt.subplots()
    # ax.imshow(partitioner.execute(), interpolation="none", cmap="Spectral")

    # plt.show()

    write_image(_o["spiral"], img)
    print(f"spiral: written")


def _test_sampler():
    def maximizedImage(img):
        result = img.copy()
        # preserve zero for background
        return cv2.normalize(img, result, 1, 255, cv2.NORM_MINMAX)

    def writeColorImage(img, fname):
        # https://matplotlib.org/3.1.1/gallery/color/colormap_reference.html
        mplot_map = "PuBuGn"
        write_image(
            fname,
            colormapped_image(img, mplot_map),
        )

    def writeSampleImage(shape, max_value, samples, fname):
        samples_img = np.zeros(shape, dtype=np.uint8)
        for p in samples:
            samples_img[p[1], p[2]] = np.uint8(255.0 * p[0] / max_value)

        writeColorImage(samples_img, fname)

    def loadImage(image):
        img = read_image(image)

        # The values of inv's elements are indices of u. u is a unique
        # sorted 1D array, so the indexes come from the consecutive
        # vector [0,1,2,...,len(u)-1], which maps 1<->1 to
        # [u_min,u_1,u_2,...,u_max], preserving the order. Indices
        # of inv's values also correspondent to respective u_i
        # coordinates in u

        # This will map img to a new one with pixel values from
        # [1,...,len(u)]
        u, inv = np.unique(img, return_inverse=True)
        inv += 1  # (we need the zero later)
        return inv.reshape(img.shape).astype(np.uint8), len(u)

    def sample(img, out_file, sampler, *args):
        samples = sampler(img, *args)
        writeSampleImage(regions.shape, categories, samples, _o[out_file])

    regions, categories = loadImage(_i["random_border"])
    writeColorImage(maximizedImage(regions), _o["randomborder_colored"])

    sample(regions, "sampler_roi", roi_sampler, [25, 32, 160, 177])

    samples = partition_sampler(regions)

    _op = make_odict2("sampler_partition", categories)
    i = 0
    for s in samples:
        writeSampleImage(regions.shape, categories, s, _op[i])
        i += 1

    regions_g = ((255 / categories) * regions).astype(np.uint8)
    contours, _ = find_contours(regions_g, 100, complexity=cv2.RETR_EXTERNAL)
    cv2.drawContours(regions, contours, -1, 255, 1)
    cv2.imwrite(str(out_dir / _o["sampler_random_contour_t"]), regions)

    sample(regions, "sampler_random_contour", random_sampler, 10000, contours[3])
    sample(regions, "sampler_random_all", random_sampler, image_area(regions) // 20)
    sample(regions, "sampler_grid", grid_sampler, [60, 30], [25, 32, 160, 177])


def test():
    printPreamble(__file__)
    # _test_random()  # random seeds
    # _test_generator()  # decision region generators
    _test_sampler()
