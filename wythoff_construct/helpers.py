import numpy as np
from os import path,mkdir

from scipy.spatial import ConvexHull
from scipy.linalg import null_space

from tvtk.api import tvtk

import wythoff_construct.config as cfg

def createDir(path):
    try:
        mkdir(path)
    except:
        pass

def areEqual(arr1, arr2):
    return np.allclose(arr1,arr2)

def isInList(arr,arrList):
    for otherArr in arrList:
        if areEqual(arr,otherArr):
            return True
    return False

def removeDupes(arr):
    """removes duplicate rows"""
    return np.unique(arr.round(5),axis=0)

def embed(big,small,x,y):
    """embeds smaller matrix in larger matrix starting at corner x,y. indices also wrap"""
    bigx,bigy = big.shape 
    smallx,smally = small.shape

    for a in range(smallx):
        for b in range(smally):

            big[(a+x)%bigx][(b+y)%bigy] = small[a][b]


def rotationMatrix(dim,ax,theta):
    c = np.cos(theta)
    s = np.sin(theta)
    if dim == 2:
        return np.array(((c,-s),(s,c)))

    dimOrder = 3**(dim-2)
    ax%=dimOrder
    subDimOrder = 3**(dim-3)
    subax = ax%subDimOrder

    rotMatrix = rotationMatrix(dim-1,subax,theta)
    ax = ax// subDimOrder

    eye = np.eye(dim)
    embed(eye,rotMatrix,ax,ax)

    return eye


def reflectionMatrix(normal):
    return np.identity(len(normal), dtype=np.float64) - 2*np.outer(normal,normal)

def unitVecAngle(v1,v2):
    return np.arccos(np.dot(v1,v2))


def subspaceCoords(point,basis):
    return np.array([np.dot(basisVec,point) for basisVec in basis])


def findFaces(pointList):
    """takes in polytope vertices and finds all flat convex 2d faces
    returns indices of face vertices"""

    #op = "C-0" # good for dim<5 and for [3,3,3,3], breaks with [3,3,3,4]
    op = "Q12" # works for [3,3,3,4]
    if len(pointList) == 0:
        return pointList
    hull = ConvexHull(pointList, qhull_options=op)
    #print("got hull")
    faces = []
    if pointList[0].size == 2:
        face = [hull.simplices[0][0],hull.simplices[0][1]]
 
        while True:
            for edge in hull.simplices[1:]:
                if edge[0]==face[-1]:
                    face.append(edge[1])

                elif edge[1] == face[-1]:
                    face.append(edge[0])
            
                if face[0]==face[-1]:
                    face.pop()
                    faces.append(face)
                    return faces
    
    eqs = removeDupes(hull.equations)
    
    #iterates through all hyperplanes
    for eq in eqs:
        normal = np.array((eq[:-1]))
        const = eq[-1]
        zeroVec = np.zeros(len(eq[:-1]))

        # generates a basis for hyperplane that we can use to reduce the dimension
        # of the problem (polytope to polyhedra to polygon) 
        # note i add a zeros vector because scipy's null_space doesnt like 1 dimensional arrays
        planesubspace = null_space( np.array( (normal, zeroVec) )).T

        pointsInPlane = []
        indices = []
        #print("hello")
        for i,point in enumerate(pointList):
            dist = abs(np.dot(point,normal) + const)/np.linalg.norm(normal)

            if dist<cfg.epsilon:
                #point is in plane
                pointsInPlane.append(subspaceCoords(point,planesubspace))
                indices.append(i)
        
        # these indices have to be converted, they are the indices for the pointsInPlane/indices list
        raws = findFaces(pointsInPlane)
        for rawFace in raws:
            face = [indices[raw] for raw in rawFace]
            faces.append(face)
    
    return faces

def findEdges(pointList):
    """takes in polytope vertices and connects them to create flat, convex cells
    returns indices of connected vertices"""


    if len(pointList) == 2:
        return [[0,1]]

    hull = ConvexHull(pointList)
    edges = []

    if pointList[0].size == 2:
        return hull.simplices

    
    eqs = [eq for eq in hull.equations]
    removeDupes(eqs)
    #iterates through all hyperplanes
    for eq in eqs:
        normal = np.array((eq[:-1]))
        const = eq[-1]
        zeroVec = np.zeros(len(eq[:-1]))

        # generates a basis for hyperplane that we can use to reduce the dimension
        # of the problem (polytope to polyhedra to polygon to individual line segment) 
        # note i add a zeros vector because scipy's null_space doesnt like 1 dimensional arrays
        planesubspace = null_space( np.array( (normal, zeroVec) )).T

        pointsInPlane = []
        indices = []

        for i,point in enumerate(pointList):
            dist = abs(np.dot(point,normal) + const)/np.linalg.norm(normal)

            if dist<cfg.epsilon:
                #point is in plane
                pointsInPlane.append(subspaceCoords(point,planesubspace))
                indices.append(i)
        
        # these indices have to be converted, they are the indices for the pointsInPlane/indices list
        raws = findEdges(pointsInPlane)

        for pair in raws:
            edges.append( [indices[pair[0]],indices[pair[1]]] )


    # dupe removal
    popped = 0

    i = 0
    while i < len(edges):
        j = 0
        while j < len(edges) - i - 1:
            conn1 = edges[i]
            conn2 = edges[j+i+1]
            #removes dupes and flipped dupes (ie [1,2] is the same as [2,1])
            if ((conn1[0]==conn2[0] and conn1[1]==conn2[1]) or (conn1[0]==conn2[1] and conn1[1]==conn2[0])):
                popped+=1
                edges.pop(j+i+1)
            else:
                j+=1
        i+=1
    
    return edges


def orthographicProjection(points,dim):
    if dim==3:
        return points
    basis = np.zeros((dim,3))
    basis[0][0] = basis[1][1] = basis[2][2] = 1
    return np.matmul(points,basis)



def perspectiveProjection(points,dim):
    if dim == 3:
        return points


    planePos = np.zeros(dim)
    planePos[0] = 3

    planeBasis = np.eye(dim)[1:]

    lightPos = np.zeros(dim)
    lightPos[0] = 1.8
    
    vs = points - lightPos
    cat = np.vstack((planeBasis,lightPos-planePos))

    sol =  np.linalg.solve(cat.T,vs.T)
    consts=sol[-1]
    points=sol[:-1]
    points/=consts

    return perspectiveProjection(points.T,dim-1)


def getPolydata(pointList,faces):
    scalars = []
    for face in faces:
        scalars.append(len(face))
    polydata = tvtk.PolyData(points = pointList, polys = faces)

    polydata.cell_data.scalars=scalars
    polydata.cell_data.scalars.name = "celldata" 

    return polydata