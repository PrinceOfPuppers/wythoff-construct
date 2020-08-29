import math 
import numpy as np 
import timeit

import config as cfg
from groupGen import generatePlanes3D, orbitPoint,hyperplaneIntersections,findReflectionGroup,getSeedPoint
from helpers import reflectionMatrix,areEqual

from mayAviPlotting import surfacePlot

def main():

    normals = generatePlanes3D(np.pi/5,np.pi/3)
    generators = [reflectionMatrix(normal) for normal in normals]

    group = findReflectionGroup(generators,120)

    intersections = hyperplaneIntersections(normals)

    centeroid=getSeedPoint([0.7,0],intersections)

    orbit = orbitPoint(centeroid,group)
    
    surfacePlot(orbit)

if __name__ == '__main__':
    main()