import numpy as np
import config as cfg

from scipy.spatial import ConvexHull
from scipy.linalg import null_space

def mapArrayList(arr,arrList):
    for i,a in enumerate(arrList):
        arrList[i] = np.matmul(arr,a)

def mulList(arrList):
    result = arrList[0].copy()
    for arr in arrList[1:]:
        result = np.matmul(result,arr)
    return result

def areEqual(arr1, arr2):

    return (abs(arr1-arr2) < cfg.epsilon).all()

def isInList(arr,arrList):

    for otherArr in arrList:
        if areEqual(arr,otherArr):
            return True
    return False

def removeDupes(arr):
    """removes duplicate rows"""
    return np.unique(arr.round(5),axis=0)


def rotationMatrix(dim,ax,theta):
    """returns a rotation matrix around the axis number ax by theta radians in dimension dim.
    ie) dim=3 ax=0 theta=pi/2 returns a rotation about the x axis by 90 degrees"""

    rot = np.zeros((dim,dim))

    rot[0][0] = np.cos(theta)
    rot[0][ax+1] = ((-1)**(ax+1))*np.sin(theta)
    rot[ax+1][0] = ((-1)**(ax))*np.sin(theta)
    rot[ax][ax] = np.cos(theta)

    return rot


def reflectionMatrix(normal):
    return np.identity(len(normal), dtype=np.float64) - 2*np.outer(normal,normal)

def unitVecAngle(v1,v2):
    return np.arccos(np.dot(v1,v2))


def subspaceCoords(point,basis):
    return np.array([np.dot(basisVec,point) for basisVec in basis])


def findFaces(pointList):
    """takes in polytope vertices and finds all flat convex 2d faces
    returns indices of face vertices"""

    hull = ConvexHull(pointList,qhull_options="C-0")
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

def getProjection(scalars):
    """generates a projection matrix (orthonormal basis vectors for dim 3 subspace) given a set of scalars
    dim is assumed to be number of scalars + 1, method used is by generating normal of subspace and finding
    its nullspace"""

    dim = len(scalars)+1
    if dim <4:
        return None
    #generates vector on hyper sphere given by angles in scalars
    sines=1
    normal = np.zeros(dim)
    normal[0] = 1
    for i in range(1,dim):
        normal[i-1]*=np.cos(scalars[i-1])

        sines*=np.sin(scalars[i-1])

        normal[i]=sines

    zeroVec = np.zeros(dim)
    projection = null_space( np.array( (normal, zeroVec) )).T[:3]


    return projection

