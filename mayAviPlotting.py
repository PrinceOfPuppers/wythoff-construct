import numpy as np
from mayavi import mlab
from tvtk.api import tvtk

from pprint import pprint

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

def surfacePlot(pointList):
    polydata = getPolydata(pointList)

    mlab.pipeline.surface(polydata,opacity = 0.5)
    mlab.pipeline.surface(polydata,opacity = 0.5,representation = 'wireframe',  color=(0, 0, 0))

    
    #from copy import deepcopy
    #pointListUnedited = deepcopy(pointList)
#
#
    #@mlab.animate(delay=10)
    #def anim():
    #    for i in range(0,10000):
    #        pointList[10] += np.sin(i/np.pi)*pointListUnedited[10]
    #        polydata.points = pointList
    #        #print(pointList[10], pointListUnedited[10])
    #        #polydata.modified()  # does not work
    #        #thing.parent.parent.update() # works
    #        yield
#
    #anim()
    mlab.show()

    # changing values https://github.com/enthought/mayavi/issues/482