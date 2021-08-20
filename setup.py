import setuptools
from sys import platform

if platform == 'win32':
    print("Wythoff Construct Requires 64 Bit Python")
    exit()

with open('README.md', 'r') as f:
    longDescription = f.read()

setuptools.setup(
    name="wythoff-construct",
    version="0.2.3",
    author="Joshua McPherson",
    author_email="joshuamcpherson5@gmail.com",
    description="Constructs and visualizes hyperdimensional polytopes created using Wythoff construction",
    long_description = longDescription,
    long_description_content_type = 'text/markdown',
    url="https://github.com/PrinceOfPuppers/wythoff-construct",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=['numpy', 'scipy', 'PyQt5', 'mayavi'],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires='>=3.6, <3.10',
    scripts=["bin/wythoff-construct"],
    entry_points={
        'console_scripts': ['wythoff-construct = wythoff_construct:main'],
    },
)
