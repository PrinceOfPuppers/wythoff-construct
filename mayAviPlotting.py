import numpy as np
from mayavi import mlab
from tvtk.api import tvtk

from helpers import findFaces

def getPolydata(pointList):
    faces = findFaces(pointList)

    scalars = []
    for face in faces:
        scalars.append(len(face))

    polydata = tvtk.PolyData(points = pointList, polys = faces)

    
    polydata.cell_data.scalars=scalars
    polydata.cell_data.scalars.name = "celldata" 

    return polydata