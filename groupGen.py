import numpy as np
import config as cfg
from scipy.optimize import minimize


from mplPlotting import scatterPlot,wireframePlot,surfacePlot

from mayAviPlotting import surfacePlot as sp
from helpers import mulList,areEqual,isInList,removeDupes,reflectionMatrix,unitVecAngle



def generatePlanes3D(angle1, angle2):
    """generates list of plane normals, given successive dihedral angles between planes.
    first and last are orthogonal, dimension is 3"""

    #test if valid planes using spherical excess formula 
    if angle1%(2*np.pi) < cfg.epsilon or angle2%(2*np.pi) < cfg.epsilon:
        raise Exception("Planes Cannot be Colinear")

    if 1/angle1+1/angle2+2/np.pi < np.pi:
        raise Exception("Invalid plane Configuration")

    
    #normal1 is e_1, normal2 is rotated in direction of e_2 by specified angle
    #normal3 is in y,z plane (orthogonal to normal1) and is at angle2 away from normal2
    normal1 = np.array((1,0,0), dtype=np.float64)
    normal2 = np.array( (np.cos(angle1), np.sin(angle1), 0), dtype=np.float64 ) 

    a = np.cos(angle2)/np.sin(angle1)

    normal3 = np.array( (0, a, np.sqrt(1-a*a)),dtype=np.float64 ) 

    print(f"Plane Angles: π/{np.pi/unitVecAngle(normal1,normal2)}, π/{np.pi/unitVecAngle(normal2,normal3)}, π/{np.pi/unitVecAngle(normal3,normal1)}")

    return normal1,normal2,normal3


def generateRep(generators,prevRep,n):
    """makes coset representitive using generators and a number
    should go on random walk though entire reflection space"""
    if n > 1000:
        raise Exception("Coset Generation Failed")
    
    rep = np.matmul( generators[-n%len(generators)] , prevRep)
    #rep /= abs(np.linalg.det(rep))
    return rep


#def generateRep(generators,identity,n):
#    """counting algorithm for generating group elements using the least possible number of products"""
#    # this counts up like regular numbers except the digits are the generators
#    numGens = len(generators)
#
#    base = 1
#
#    rep = identity
#    indices=[]
#    while base<=n:
#        index = (n//base)%numGens
#        
#        indices.append(index)
#        gen = generators[index]
#        rep = np.matmul(gen,rep)
#        
#        base*=numGens
#    
#    print(indices)
#    return rep


def findReflectionGroup(generators,groupOrder):
    """Takes in list of n by n reflection matrices which generate a symmetry group
    The method used is by finding a subgroup, then finding all of its cosets"""

    #generating subgroup
    subGen1 = generators[0]
    subGen2 = generators[1] #note subGen2 isnt in the subgroup, subGen2*subGen1 is, along with further products
    identity = np.identity(subGen1.shape[0])

    subgroup = [ identity, subGen1 ]

    subgroupElement = subGen1.copy()

    while True:
        subgroupElement = np.matmul(subGen2,subgroupElement)
        if areEqual(identity,subgroupElement):
            print(subgroupElement)
            break
            
        subgroup.append(subgroupElement)

    
        subgroupElement = np.matmul(subGen1,subgroupElement)
        if areEqual(identity,subgroupElement):
            print(subgroupElement)
            break
        subgroup.append(subgroupElement)


    
    subgroupOrder = len(subgroup)
    numCosets = groupOrder/subgroupOrder

    
    if numCosets == 1:
        return subgroup

    
    # Now we generate the whole group by finding all other cosets
    cosetReps = [identity]
    
    prevRep=identity.copy()

    i = 1
    while len(cosetReps)<numCosets:

        if not areEqual(identity,np.eye(3)):
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
            cosetReps.append(rep)
        
        i+=1

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
        


#finds hyperplane intersections that are on the unit hypersphere
def hyperplaneIntersections(normals):
    intersections = []
    for i,n1 in enumerate(normals):
        for n2 in normals[i+1:]:
            coeffs = np.array( (n1,n2), dtype=np.float64 )
            linearSystem = lambda x: np.absolute(np.dot( coeffs, x )).max()
            constraints = ( {'type': 'eq', 'fun': lambda x: np.linalg.norm(x)-1} )

            intersection = minimize( linearSystem, np.zeros(len(n1)), method='SLSQP', constraints=constraints, options={'disp': False})
            intersections.append(intersection.x)
    
    #TODO check distances between intersections, if one is too far from the others take its negative
    return intersections

def getSeedPoint(scalers,intersections):
    """uses the intersections from hyperplaneIntersections as a basis to get a seed point in the primary
    chamber of the kalidoscope, there should be one less scaler than there are intersections"""

    point = intersections[0].copy()
    for i in range(0,len(scalers)):
       
        point += scalers[i]*( np.subtract(intersections[i+1],intersections[0]))

    return point

def orbitPoint(point,group):
    """Finds the orbit of the point under reflection in all planes"""
    points=[]
    
    for reflection in group:
        points.append(np.matmul(reflection,point))
    return points

    

