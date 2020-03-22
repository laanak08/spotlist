import setuptools

setuptools.setup(
    name="spotlist",
    version="0.0.1",
    author="Marcelle Bonterre",
    author_email="laanak@gmail.com",
    description="CLI playlist creation app ",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=['spotipy', 'bottle', 'dask[bag]'],
    entry_points={
        "console_scripts": ["spotlist = spotlist.cli:main"]}
)
