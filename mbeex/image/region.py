import cv2
import numpy as np
import matplotlib.pyplot as plt
import copy


"""
Shapes, ROI's and operations on them and
containers containing shapes
"""


def get_kernel_border_coordinates(d):
    """
    Generate coordinate pairs for the border of a `d*d` kernel. `d` must be odd
    """
    border = d // 2
    primitive = list(range(-border, border + 1))
    return [
        (x, y)
        for x in primitive
        for y in primitive
        if (abs(x) == border or abs(y) == border)
    ]


def random_grid(size, classes, factor=1, instances=0):
    """
    Creates a black gray image of randomly seeded pixels with values > 0
    from [1,...,classes] (so it is limited to 254 classes for factor==1)
    For `instances` > `classes`, multiple seeds of the same class are allowed
    (but non-connected areas in general might nevertheless appear for
    non-deflecting boundary conditions and other reasons)

    The function also returns an array of coordinate tupels (x,y) for every
    coordinate without seeded pixels (black resp. zero)

    Parameters:
        :size:      image size
        :classes:   number of classes
        :factor:    multiplied with pixel value
                    (example: factor=7 means pixel values of [7,14,21...7*classes]
        :instances: number of instances

        :return: gray image with seeded pixels; coordinate array
    """

    coords = None
    if instances < classes:
        coords = np.random.choice(size[0] * size[1], classes, replace=False)
    else:
        coords = np.random.choice(size[0] * size[1], instances, replace=True)

    grid = np.zeros(size[0] * size[1], dtype=int)
    i = 1
    for c in coords:
        grid[c] = i * factor
        i = i + 1

    grid = grid.reshape(size[0], size[1])
    X = np.arange(size[1], dtype=int)
    Y = np.arange(size[0], dtype=int)
    grid_coords = [(x, y) for x in X for y in Y if grid[y, x] == 0]
    return grid, grid_coords


class VicinityIterator:
    """
    Vicinity Iterator - surrounds a pixel and sets new pixels
    dependent on some condition
    """

    def __init__(
        self, grid, border_coordinates=get_kernel_border_coordinates(3)
    ):  # 3x3 kernel border
        self._grid = grid
        self._size = [self._grid.shape[0], self._grid.shape[1]]
        self.setVicinity(border_coordinates)

    def setVicinity(self, vic):
        self._vic = vic

    def execute(self, x, y, grid):
        np.random.shuffle(self._vic)
        for dx, dy in self._vic:
            xx = (x + dx) % self._size[1]
            yy = (y + dy) % self._size[0]
            if self._grid[yy, xx] != 0:
                grid[y, x] = self._grid[yy, xx]
                return True  # pixel has been set
        return False


class Generator:
    def __init__(self, size):
        self._grid = np.zeros(size[0] * size[1], dtype=int).reshape(size[0], size[1])
        self._size = self._grid.shape
        self._coords = None

    def execute(self):
        pass


class Generator_RB(Generator):
    """
    Creates decompositions with slightly random boundaries
    """

    class Checker:
        """
        Provides state maintaining callable for a list comprehension filter,
        whose use accelerates removing elements from the `Generator._coords` list.
        """

        def __init__(self, skips, coord_len, grid, it):
            self._i = 0
            self._skips = skips
            self._coord_len = coord_len
            self._grid = grid
            self._it = it

        def setGrid(self, grid):
            self._grid = grid

        def __call__(self, x, y):
            self._i = (self._i + 1) % self._skips
            return not self._checkPixel(
                self._i, self._skips, self._coord_len, self._grid, self._it, x, y
            )

        def _checkPixel(self, i, skips, size, new_grid, vic_it, x, y):
            if not i % skips or size < skips:
                return vic_it.execute(x, y, new_grid)
            return False

    def __init__(self, size, number_of_classes):
        super().__init__(size)
        self._grid, self._coords = random_grid(size, number_of_classes, factor=10)
        self._vic = get_kernel_border_coordinates(5)

    def execute(self):
        """Calculates pixel creation on the whole grid"""
        np.random.shuffle(self._coords)
        vic = copy.deepcopy(self._vic)  # this might be shuffled, etc.
        vic_it = VicinityIterator(self._grid, vic)

        new_grid = None
        skips = 3
        fig, ax = plt.subplots()
        h = ax.imshow(self._grid, interpolation="none", cmap="Spectral")

        cc = Generator_RB.Checker(skips, len(self._coords), grid=None, it=vic_it)
        plt.ion()
        while self._coords:
            new_grid = self._grid
            cc.setGrid(new_grid)
            self._coords[:] = [(x, y) for (x, y) in self._coords if cc(x, y)]
            self._grid[:] = new_grid[:]

            h.set_data(new_grid)
            plt.draw()
            plt.pause(1e-3)
            print(f"remaining: {len(self._coords)}")

        return new_grid


class Generator_Spiral(Generator):
    """
    Generates a spiral decomposition
    """

    def __init__(self, size):
        super().__init__(size)

    def execute(self):
        """---"""

        new_grid = copy.deepcopy(self._grid)

        p = np.array(new_grid.shape) / 2  # center point as (c_y, c_x)
        b = 1.8 / (np.pi)
        phi = 1
        i = 1
        cnt = 0
        while i:
            x = np.sqrt(phi)
            phi = i * np.pi / 100 / x
            y, x = (np.rint([b * phi * np.cos(phi), b * phi * np.sin(phi)]) + p).astype(
                int
            )
            if x >= 0 and x < new_grid.shape[1] and y >= 0 and y < new_grid.shape[0]:
                new_grid[y, x] = 100
                cnt = 0
            if cnt > new_grid.shape[0] * new_grid.shape[1]:
                break
            cnt += 1
            i += 1

        self._grid[:] = new_grid[:]
        return new_grid


#
#
#


def roi_sampler(img, rect):
    """
    Returns complete content of rect. area as array of (pixel_value, y, x) samples

    Parameters:
        :img: input gray image
        :rect: rect. ROI as list [x0,y0,x1,y1]
        :return: 1D-array of (pixel_value, y, x) samples
    """

    x0, y0, x1, y1 = rect

    roi = img[y0:y1, x0:x1]
    samples = roi.copy()
    y, x = np.indices(roi.shape)
    y += y0
    x += x0
    samples = np.dstack((samples, y, x))
    return samples.reshape(-1, samples.shape[2])


def _random_sampler(img, rhull, number):
    """
    Samples pixel from random coordinates

    Parameters:
        :img: input gray image
        :number: number of pixel drawn (w/o replacement)
        :return: 1D-array of (pixel_value, y, x) samples
    """

    x, y, w, h = rhull

    roi = img[y : y + h, x : x + w]
    iy, ix = np.indices(roi.shape)
    iy += y
    ix += x
    samples = np.dstack((roi.copy(), iy, ix))
    samples = samples.reshape(
        -1, samples.shape[2]
    )  # create 1D array of (p,y,x) 'points'
    random_indices = np.arange(0, samples.shape[0])  # array of all indices
    np.random.shuffle(random_indices)

    return samples[random_indices[:number]]  # get N samples without replacement


def random_sampler(img, number, contour=np.array([])):
    """
    Randomly samples pixel from the contours rectangular
    hull and returns the subset inside the contour.

    Remark: `number` is the requested number for data points
    inside `contour`. But actually, the function draws the samples from
    the enclosing rectangle. It increases `number` internally by
    multiplying it with the quotient of the both structures area (r_a/c_a)
    before doing so. After that, it returns the samples covered by the contour.
    Their number might slightly differ from the requested number.

    Parameters:
        :img: input gray image
        :number: number of pixel drawn (w/o replacement).
        :contour: ROI as OpenCV contour
        :return: 1D-array of (pixel_value, y, x) samples
    """

    # contour == whole image
    if contour.shape == (0,):
        h, w = img.shape
        return _random_sampler(img, [0, 0, w, h], number)

    # calculate rect. hull
    rhull = cv2.boundingRect(contour)

    # calc. area quotient
    ra = rhull[2] * rhull[3]
    ca = cv2.contourArea(contour)
    q = ra / ca

    # increase 'number' accordingly
    number = int(np.round(number * q))

    # sample in rect. hull
    samples = _random_sampler(img, rhull, number)

    # mask with contour

    points = [(s, tuple([int(round(s[2])), int(round(s[1]))])) for s in samples]

    return [p[0] for p in points if 0 < cv2.pointPolygonTest(contour, p[1], False)]


def partition_sampler(img):
    """
    Creates partition of the whole input image. Every sub-array contains all elements
    with the same pixel value and associated coordinates (pixel_value, y, x).

    Parameters:
        :img: input gray image
        :return: partition of the img
    """
    y, x = np.indices(img.shape)
    samples = np.dstack((img.copy(), y, x))
    samples = samples.reshape(
        -1, samples.shape[2]
    )  # create 1D array of (p,y,x) 'points'

    samples = samples[samples[:, 0].argsort()]  # sort, using pixel value
    first = samples[:, 0]  # sorted 1D array of pixel values
    # calculate indices, where pixel values (class) change
    _, indices = np.unique(first, return_index=True)
    # split the original array at these indices
    return np.split(samples, indices[1:])  # remove zero


def grid_sampler(img, steps, rect=None):
    """
    Returns values at grid coordinates for required coordinate density.
    Coordinates will be rounded, so they are not quite equidistant (up to 2 pixel)

    Parameters:
        :img: input gray image
        :steps: number of equidistant sampling points per coordinate: [ypoints, xpoints]
        :rect:  ROI: [x0,y0,x1,y1] or None (whole img)
        :return: 1D-array of (pixel_value, y, x) samples
    """

    y_steps, x_steps = steps

    if not rect:
        rect = [0, 0, img.shape[1] - 1, img.shape[0] - 1]

    x0 = rect[0]
    y0 = rect[1]
    x1 = rect[2]
    y1 = rect[3]

    X = np.around(np.linspace(x0, x1, x_steps)).astype(np.uint8)
    Y = np.around(np.linspace(y0, y1, y_steps)).astype(np.uint8)

    return np.asarray([np.array([img[y, x], y, x]) for x in X for y in Y])
