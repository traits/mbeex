import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pytraits",
    version="0.0.1",
    author="mbee",
    author_email="python@traits.de",
    description="traits.de - common stuff",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://depot.traits.de",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)