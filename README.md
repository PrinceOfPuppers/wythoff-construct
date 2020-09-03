<img src="https://drive.google.com/uc?id=1nsABHRojHFkD2RycnrKheTq5WSyvzfN2" />

# wythoff-construct

> Constructs and visualizes hyperdimensional polytopes created using Wythoff construction 

## Setup
### Linux:  
Install Package With PIP
```
$ git clone https://github.com/PrinceOfPuppers/wythoff-construct.git
$ cd wythoff-construct
$ pip3 install .
```
### Windows: 
to install VTK and traits on windows through pypi requires both 64 bit python and Build Tools for Visual Studio.
however you can also get versions precomipled for 32 bit python from https://www.lfd.uci.edu/~gohlke/pythonlibs/
download the appropriate ones for your python version (ie for python 3.6 look for the whl with cp36) and install
using pip, ie)
```
pip3 install VTK‑9.0.1‑cp36‑cp36m‑win32.whl
pip3 install traits‑6.1.1‑cp39‑cp39‑win32.whl
```
while in the same directory as the downloaded files. Then simply run
```
git clone https://github.com/PrinceOfPuppers/wythoff-construct.git
cd wythoff-construct
pip3 install .
```

### To Uninstall...  
```pip3 uninstall wythoff-construct```

## Usage
Once installed using pip the following command can be exacuted from any working directory
```wythoff-construct.py```  
the .py extension is required for windows compatibility.

for general infomration regarding Wythoff Construction see https://en.wikipedia.org/wiki/Wythoff_construction

### Seed Point Selection
Basic: Use the sliders smoothly transistion between shapes.

Advanced: These sliders select the point which is reflected in the kalidoscope mirrors to get all 
the vertices of the polytope. Each slider scales a vector pointing from one intersection of the kalidoscope
mirrors to all other intersections (the point of intersection are between all but one of the mirrors, and 
the unit sphere). They are essentially the coordinates on the spherical triangle which tile sphere (hence their sum is kept to 1). 
In higher dimensions the picure is similar, except there are more mirrors and more intersections and more vectors.

### Dimension
Simply used to change the number of spatial dimensions and hence which kalidoscopes are avalible 
(3,4 and 5 are currently supported).

### Kalidoscope
Basic: Determines what shapes are created using the seed point selection sliders.

Advanced: the coxeter notation for which refelction group (kalidoscope) is active. For dimension 3 I excluded all
but one dihedral group as to not clutter the UI (the others are very similar).

All kalidoscopes save after the first time they are generated to allow for faster switching between them afterwards.
I also pre-generated [3²,5] and [3³,4] due to long generation times.

### Rotation
Rotation in 3 dimensions is done by clicking and dragging the mouse, In higher dimensions I included sliders for the 
additional rotations not possible in 3 dimenisons there will be 3ⁿ-3 sliders where n is the number of dimensions.

### Projection
Controls how the program renders n dimensional shapes in 3 dimensions (3 to 2 dimensions is handled by the ui program 
which can be changed using the toggle parallel projection button on top).

Perspective: Things closer in higher dimensions appear bigger.

Orthographic: Size does not depend on distance.

For a clear example, load [3²,4], the smaller inner cube when on Perspective projection is further from you in the 4th dimension.

### Opacity
Controls how opaque the faces (2D cells) are on the polytope. automatically scales down with dimension to compete with the 
growing number of faces.
