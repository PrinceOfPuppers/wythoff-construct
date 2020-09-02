import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wythoff-construct", # Replace with your own username
    version="0.0.1",
    author="Joshua McPherson",
    author_email="joshuamcpherson5@gmail.com",
    description="Constructs and visualizes hyperdimensional polytopes created using Wythoff construction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PrinceOfPuppers/wythoff-construct",
    packages=setuptools.find_packages(),
    install_requires=['numpy','scipy','PyQt5',"mayavi"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires='>=3.6',
    scripts=["wythoff-construct.py"]
)