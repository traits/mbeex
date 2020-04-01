import numpy as np
import matplotlib.pyplot as plt
import copy

from pytraits.base import Size2D


"""
Shapes, ROI's and operations on them and
containers containing shapes
"""


def get_kernel_border_coordinates(d):
    '''
    Generate coordinate pairs for the border of a d*d kernel. d must be odd
    '''
    border = d // 2
    primitive = list(range(-border, border + 1))
    return [(x, y) for x in primitive for y in primitive if (abs(x) == border or abs(y) == border)]


def random_grid(size, classes, instances = 0):
    """
    Creates a black gray image of randomly seeded pixels with values > 0
    from [1,...,classes] (so it is limited to 254 classes)
    For instances > classes, multiple seeds of the same class are allowed
    (but non-connected areas in general might nevertheless appear for
    non-deflecting boundary conditions and other reasons)
    
    The function also returns an array of coordinate tupels (x,y) for every
    coordinate without seeded pixels (black resp. zero) 
    
    Parameters:
        :size:      image size
        :classes:   number of classes
        :instances: number of instances
        
        :return: gray image with seeded pixels; coordinate array
    """

    coords = None
    if instances < classes:
        coords = np.random.choice(size.x * size.y, classes, replace=False)
    else:
        coords = np.random.choice(size.x * size.y, instances, replace=True)

    grid = np.zeros(size.x * size.y, dtype=int)
    i = 1
    for c in coords:
        grid[c] = i
        i = i + 1

    grid = grid.reshape(size.y, size.x)
    X = np.arange(size.x, dtype=int)
    Y = np.arange(size.y, dtype=int)
    grid_coords = [(x, y) for x in X for y in Y if grid[y, x] == 0]
    return grid, grid_coords


class VicinityIteratorException(Exception):
    '''To break deep iteration cycles'''
    pass


class VicinityIterator:
    '''
    Vicinity Iterator - surrounds a pixel and sets new pixels
    dependent on some condition
    '''

    def __init__(self, grid):
        self._grid = grid
        self._size = Size2D(self._grid.shape[1], self._grid.shape[0])
        self.setVicinity(get_kernel_border_coordinates(3))  # 3x3 kernel border

    def setVicinity(self, vic):
        self._vic = vic

    def execute(self, x, y, grid):
        np.random.shuffle(self._vic)
        for dx, dy in self._vic:
            yy = (y + dy) % self._size.y
            xx = (x + dx) % self._size.x
            if self._grid[yy, xx] != 0:
                grid[y, x] = self._grid[yy, xx]
                raise VicinityIteratorException()  # signal when pixel has been set


class Generator:
    def __init__(self, size):
        self._grid = np.zeros(size.x * size.y, dtype=int).reshape(size.y, size.x)
        self._size = self._grid.shape
        self._coords = None

    def execute(self):
        pass


class Generator_1(Generator):
    '''
    Creates decompositions with slightly random boundaries
    '''

    def __init__(self, size, number_of_classes):
        super().__init__(size)
        self._grid, self._coords = random_grid(size, number_of_classes)
        self._vic = get_kernel_border_coordinates(5)

    def execute(self):
        '''Calculates pixel creation on the whole grid'''
        np.random.shuffle(self._coords)
        vic = copy.deepcopy(self._vic)  # this might be shuffled etc.
        vic_it = VicinityIterator(self._grid)
        vic_it.setVicinity(vic)

        new_grid = None
        skips = 3
        i = 0
        fig, ax = plt.subplots()
        h = ax.imshow(self._grid, interpolation = 'none', cmap='Spectral')

        class Checker:
            '''
            Provides state maintaining callable for list comprehension filter,
            speeding up removing elements from Generator._coords
            '''

            def __init__(self, i, skips, grid, it, check):
                self._i = i
                self._skips = skips
                self._grid = grid
                self._it = it
                self._check = check

            def setGrid(self, grid):
                self._grid = grid

            def __call__(self, x, y):
                self._i = (self._i + 1) % self._skips
                return not self._check(self._i, self._skips, self._grid, self._it, x, y)

        cc = Checker(i, skips, None, vic_it, self.checkPixel)
        plt.ion()
        while self._coords:
            new_grid = self._grid
            cc.setGrid(new_grid)
            self._coords[:] = [(x, y) for (x, y) in self._coords if cc(x, y)]
            self._grid[:] = new_grid[:]

            h.set_data(new_grid)
            plt.draw()
            plt.pause(1e-3)
            print(f'remaining: {len(self._coords)}')

        return new_grid

    def checkPixel(self, i, skips, new_grid, vic_it, x, y):
        try:
            if not i % skips or len(self._coords) < skips:
                vic_it.execute(x, y, new_grid)
                return False
        except VicinityIteratorException:
            return True


class Generator_2(Generator):
    '''
    Generates a spiral decomposition
    '''

    def __init__(self, size):
        super().__init__(size)

    def execute(self):
        '''---'''

        new_grid = copy.deepcopy(self._grid)

        p = np.array(new_grid.shape) / 2  # center point as (c_y, c_x)
        b = 1.8 / (np.pi)
        phi = 1
        i = 1
        cnt = 0
        while i:
            x = np.sqrt(phi)
            phi = i * np.pi / 100 / x
            y, x = (np.rint([b * phi * np.cos(phi), b * phi * np.sin(phi)]) + p).astype(int)
            if (x >= 0 and x < new_grid.shape[1] and y >= 0 and y < new_grid.shape[0]):
                new_grid[y, x] = 100
                cnt = 0
            if cnt > new_grid.shape[0] * new_grid.shape[1]:
                break
            cnt += 1
            i += 1

        self._grid[:] = new_grid[:]
        return new_grid


