from pytraits.base import Vector2D
import pytraits.base.directory as ds
import pytraits.image.base as image


def main():
    def f(fname):
        return len(fname) < 20
    fl = ds.filterDirectory('../', f)
    src_size = Vector2D(x = 300, y = 200)

    img = image.create_mono_colored_image(src_size, 1, 100)
    image.write_image("gray.png", img)
    img = image.create_mono_colored_image(src_size, 3, (100, 0, 0))  # bgr
    image.write_image("col.png", img)
    img = image.create_noisy_image(src_size, 4)
    image.write_image("noise_alpha.png", img)

    print(fl)


if __name__ == '__main__':
    main()
