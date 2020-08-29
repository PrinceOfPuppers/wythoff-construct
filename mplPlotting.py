
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.collections import PolyCollection
import matplotlib.pyplot as plt

from helpers import findEdges,findFaces,removeDupes
import numpy as np

def axisEqual3D(ax):
    extents = np.array([getattr(ax, 'get_{}lim'.format(dim))() for dim in 'xyz'])
    sz = extents[:,1] - extents[:,0]
    centers = np.mean(extents, axis=1)
    maxsize = max(abs(sz))
    r = maxsize/2
    for ctr, dim in zip(centers, 'xyz'):
        getattr(ax, 'set_{}lim'.format(dim))(ctr - r, ctr + r)


def surfacePlot(pointList):
    faces = findFaces(pointList)
    fig = plt.figure()
    ax  = fig.add_subplot(111, projection = '3d')
    

    decimalPlaces = 5
    for face in faces:
        verts = [pointList[i] for i in face]

        #poly = Poly3DCollection(verts,alpha=0.1, color='red')
        #ax.add_collection3d(poly)
        xs=[round(vert[0],decimalPlaces) for vert in verts]
        ys=[round(vert[1],decimalPlaces) for vert in verts]
        zs=[round(vert[2],decimalPlaces) for vert in verts]

        try:
            ax.plot_trisurf(xs,ys,zs,alpha=0.3)

        except:
            print("\nError: ",verts,"\n")


        ax.plot(xs+[round(verts[0][0],decimalPlaces)],
                ys+[round(verts[0][1],decimalPlaces)],
                zs+[round(verts[0][2],decimalPlaces)], color='black')



    axisEqual3D(ax)
    plt.show()

def wireframePlot(pointList):
    conns = findEdges(pointList)
    print("Edges: ",len(conns))
    
    fig = plt.figure()
    ax  = fig.add_subplot(111, projection = '3d')

    for conn in conns:
        pnt1 = pointList[conn[0]]
        pnt2 = pointList[conn[1]]
        ax.plot( (pnt1[0], pnt2[0]), (pnt1[1], pnt2[1]), (pnt1[2],pnt2[2]), color='r' )

    axisEqual3D(ax) 
    plt.show()

def scatterPlot(pointList):

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    #fig = plt.figure(figsize=plt.figaspect(0.5)*1.5) #Adjusts the aspect ratio and enlarges the figure (text does not enlarge)
    #ax = fig.gca(projection='3d')

    xs,ys,zs=[],[],[]
    for point in pointList:
        xs.append(point[0])
        ys.append(point[1])
        zs.append(point[2])
    ax.scatter(xs,ys,zs)
    ax.scatter(0,0,0,marker="^")
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')


    axisEqual3D(ax)
    plt.show()
