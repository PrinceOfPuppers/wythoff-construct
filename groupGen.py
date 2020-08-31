import numpy as np
import config as cfg
from scipy.optimize import minimize

from helpers import mulList,areEqual,isInList,reflectionMatrix,unitVecAngle,findFaces,orthographicProjection,rotationMatrix,perspectiveProjection
from functools import reduce





#def generatePlanes(angleList):
#    angle1=angleList[0]
#    angle2=angleList[1]
#    """generates list of plane normals, given successive dihedral angles between planes.
#    first and last are orthogonal, dimension is 3"""
#    
#    #test if valid planes using spherical excess formula 
#    if angle1%(2*np.pi) < cfg.epsilon or angle2%(2*np.pi) < cfg.epsilon:
#        raise Exception("Planes Cannot be Colinear")
#
#    if angle1 + angle2 + np.pi <= np.pi:
#
#        raise Exception("Invalid plane Configuration")
#
#    
#    #normal1 is e_1, normal2 is rotated in direction of e_2 by specified angle
#    #normal3 is in y,z plane (orthogonal to normal1) and is at angle2 away from normal2
#    normal1 = np.array((1,0,0), dtype=np.float64)
#    normal2 = np.array( (np.cos(angle1), np.sin(angle1), 0), dtype=np.float64 ) 
#
#    a = np.cos(angle2)/np.sin(angle1)
#
#    normal3 = np.array( (0, a, np.sqrt(1-a*a)),dtype=np.float64 ) 
#
#    print(f"Plane Angles: π/{np.pi/unitVecAngle(normal1,normal2)}, π/{np.pi/unitVecAngle(normal2,normal3)}, π/{np.pi/unitVecAngle(normal3,normal1)}")
#
#    print("Normals")
#    for normal in (normal1,normal2,normal3):
#        print(tuple([round(x,3) for x in normal]))
#    return normal1,normal2,normal3

def generatePlanes(angleList):
    """generates list of plane normals, given successive dihedral angles between planes.
    first and last are orthogonal, works in any dimension"""
    dim = len(angleList)+1

    #normal1 is e_1, normal2 is rotated in direction of e_2 by specified angle
    #normal3 is in y,z plane (orthogonal to normal1) and is at angle2 away from normal2
    normal1 = np.zeros(dim, dtype=np.float64)
    normal1[0] = 1.
    normals=[normal1]
    
    for i in range(1,dim):
        n = np.zeros(dim)
        a = np.cos(angleList[i-1])/normals[-1][i-1]
        n[i-1] = a
        n[i] = np.sqrt(1-a**2)
        normals.append(n)

    message = "Plane Angles: "
    for i in range(dim-1):
        message+= f"π/{np.pi/unitVecAngle(normals[i],normals[i+1])}, "
    print(message)

    message = "normal lengths: "
    for i in range(dim):
        message+= f"{np.dot(normals[i],normals[i])}, "
    print(message)

    print("Normals")
    for normal in normals:
        print(tuple([round(x,3) for x in normal]))


    return normals

#def generateRep(generators,prevRep,n):
#    """makes coset representitive using generators and a number
#    should go on random walk though entire reflection space"""
#    if n > 10000:
#        raise Exception("Coset Generation Failed")
#    
#    rep = np.matmul( generators[-n%len(generators)] , prevRep)
#    #rep /= abs(np.linalg.det(rep))
#    return rep


def generateRep(generators,prevRep,n):
    """counting algorithm for generating group elements using the least possible number of products"""
    # this counts up like regular numbers except the digits are the generators
    numGens = len(generators)

    base = 1

    rep = prevRep
    indices=[]
    while base<=n:
        index = (n//base)%numGens
        
        indices.append(index)
        gen = generators[index]
        rep = np.matmul(gen,rep)
        
        base*=numGens
    
    #print(indices)
    return rep


def findReflectionGroup(generators,groupOrder):
    """Takes in list of n by n reflection matrices which generate a symmetry group
    The method used is by finding a subgroup, then finding all of its cosets"""

    #generating subgroup
    subGen1 = generators[0]
    subGen2 = generators[1] #note subGen2 isnt in the subgroup, subGen2*subGen1 is, along with further products

    dim = subGen1.shape[0]
    identity = np.identity(dim)

    subgroup = [ identity, subGen1 ]

    subgroupElement = subGen1.copy()

    while True:
        subgroupElement = np.matmul(subGen2,subgroupElement)
        if areEqual(identity,subgroupElement):
            break
            
        subgroup.append(subgroupElement)

    
        subgroupElement = np.matmul(subGen1,subgroupElement)
        if areEqual(identity,subgroupElement):
            break
        subgroup.append(subgroupElement)


    
    subgroupOrder = len(subgroup)
    numCosets = groupOrder/subgroupOrder

    
    if numCosets == 1:
        return subgroup

    
    # Now we generate the whole group by finding all other cosets
    cosetReps = [identity]
    
    prevRep=identity.copy()

    i = 0

    while len(cosetReps)<numCosets:
        i+=1
        if not areEqual(identity,np.eye(dim)):
            raise Exception("identity mutated")

        rep = generateRep(generators,prevRep,i)
        prevRep=rep.copy()

        isNewRep = True
        for b in cosetReps:
            # checks if newRep*b^-1 is in the subgroup, if it is then the cosets represented by newRep and b are equal

            a=np.matmul( np.linalg.inv(rep),b)
            if isInList(a,subgroup):
                isNewRep=False
                break
        if isNewRep:
            #i=0
            cosetReps.append(rep)
            #print(f"{100*len(cosetReps)/numCosets}%")
        

    #at this point we have enough cosets to generate the entire group
    group = []
    for rep in cosetReps:
        for element in subgroup:
            group.append(np.matmul(rep,element))

    
    if len(group) != groupOrder:
        raise Exception("Failed To Generate Whole Symmetry Group")

    print(f"Group Order: {len(group)}, Subgroup Order: {subgroupOrder}, index: {numCosets}")
    return group


#def findReflectionGroup(generators,groupOrder):
#    group = []
#    i = 0
#
#    identity =  np.identity(generators[0].shape[0])
#    while len(group)<groupOrder:
#        print(i,len(group))
#        group.append(generateRep(generators,identity,i))
#        removeDupes(group)
#        i+=1
#    return group
        



def hyperplaneIntersections(normals):
    """Finds vertices of the simplex that makes the primary chamber of the kalidoscope
    that is to say it finds points which lay on the n-sphere and are also on all but one
    of the hyperplanes
    
    takes in normals of hyperplanes and returns vertices of simplex"""

    intersections = []
    dim = len(normals[0])
    for i in range(dim):
        coeffs = np.array( [normals[j] for j in range(dim) if j!=i], dtype=np.float64 )
        linearSystem = lambda x: np.absolute(np.dot( coeffs, x )).max()
        constraints = ( {'type': 'eq', 'fun': lambda x: np.linalg.norm(x)-1} )
        guess = np.zeros(dim)
        guess[-1] = 1
        guess[-2] = 0.1
        intersection = minimize( linearSystem, guess, method='SLSQP', constraints=constraints, options={'disp': False})
        intersections.append(intersection.x)
    


    #for intersection in intersections:
    #    print(tuple([round(x,3) for x in intersection]))
    #for i,intersection in enumerate(intersections[1:]):
#
    #    if np.dot(intersection,intersections[0])>np.pi/2:
    #        print("flippin")
    #        intersections[i]*=-1
    #TODO check distances between intersections, if one is too far from the others take its negative
    return intersections

def getSeedPoint(scalers,intersections):
    """uses the intersections from hyperplaneIntersections as a basis to get a seed point in the primary
    chamber of the kalidoscope, there should be one less scaler than there are intersections"""

    point = intersections[0].copy()
    for i,scaler in enumerate(scalers):
       
        point += scaler*( np.subtract(intersections[i+1],intersections[0]))

    return point




def orbitPoint(point,group):
    """Finds the orbit of the point under reflection in all planes and returns orbit"""
    points=np.empty((len(group),len(group[0])))

    for i,reflection in enumerate(group):
        np.matmul(reflection,point,points[i])

    return points

def getPointsAndFaces(point, group, projection, scalars = None):
    """wrapper for orbitPoints, find faces and project orbit onto 3 dimensions (useful due to order sensitivity)"""

    orbit = orbitPoint(point, group)
    print("orbited")
    faces = findFaces(orbit)
    print("got faces")

    dim = len(orbit[0])
    if scalars!= None:
        rot = np.eye(dim)
        for i,scalar in enumerate(scalars):
            np.matmul(rotationMatrix(dim,i,scalar),rot,rot)

        np.matmul(orbit,rot,orbit)
    orbit = projection(orbit,len(orbit[0]))
    return orbit,faces

def getPoints(point,group, projection,scalars=None):
    orbit=orbitPoint(point,group)
    dim = len(orbit[0])
    if scalars!= None:
        rot = np.eye(dim)
        for i,scalar in enumerate(scalars):
            np.matmul(rotationMatrix(dim,i,scalar),rot,rot)
    
        np.matmul(orbit,rot,orbit)
    orbit = projection(orbit,len(orbit[0]))
    #if type(projection)!= type(None):
    #    orbit = np.matmul(orbit,projection.T)
#
    return orbit