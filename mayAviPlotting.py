import numpy as np
from mayavi import mlab
from tvtk.api import tvtk

from pprint import pprint

from helpers import findFaces
from scipy.spatial import ConvexHull

def surfacePlot(pointList):
    faces = findFaces(pointList)

    mlab.figure(fgcolor=(0, 0, 0), bgcolor=(1, 1, 1))

    scalars = []
    for face in faces:
        scalars.append(len(face))

    polydata = tvtk.PolyData(points = pointList, polys = faces)
 
    polydata.cell_data.scalars=scalars
    polydata.cell_data.scalars.name = "celldata" 

    mlab.pipeline.surface(polydata,opacity = 0.5)
    mlab.pipeline.surface(polydata,opacity = 0.5,representation = 'wireframe',  color=(0, 0, 0))
    mlab.show()

    