import numpy as np
from os import listdir
from scipy.optimize import minimize
import pickle

import wythoff_construct.config as cfg
from wythoff_construct.helpers import (areEqual,isInList,reflectionMatrix,unitVecAngle,findFaces,orthographicProjection,
                            rotationMatrix,perspectiveProjection,getPolydata,createDir)



def generatePlanes(angleList):
    """generates list of plane normals, given successive dihedral angles between planes.
    first and last are orthogonal, works in any dimension"""
    dim = len(angleList)+1

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

    return normals

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
    
    return rep


def findReflectionGroup(generators,groupOrder):
    """Takes in list of n by n reflection matrices which generate a symmetry group
    The method used is by finding a subgroup, then finding all of its cosets"""

    print("Generating Group...")
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
    return np.array(group)


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

    return np.array(intersections)

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




# Wrappers
def getPointsAndFaces(point, group, projection, scalars = None):
    """wrapper for orbitPoints, find faces and project orbit onto 3 dimensions (useful due to order sensitivity)"""
    print("Orbiting Point...")
    orbit = orbitPoint(point, group)
    print("Getting Faces...")
    faces = findFaces(orbit)
    print("Got Faces")

    dim = len(orbit[0])
    if scalars!= None:
        rot = np.eye(dim)
        for i,scalar in enumerate(scalars):
            np.matmul(rotationMatrix(dim,i,2*np.pi*scalar),rot,rot)

        np.matmul(orbit,rot,orbit)
    

    orbit = projection(orbit,len(orbit[0]))
    return orbit,faces

def getPoints(point,group, projection,scalars=None):
    orbit=orbitPoint(point,group)
    dim = len(orbit[0])
    if scalars!= None:
        rot = np.eye(dim)
        for i,scalar in enumerate(scalars):
            np.matmul(rotationMatrix(dim,i,2*np.pi*scalar),rot,rot)
    
        np.matmul(orbit,rot,orbit)

    orbit = projection(orbit,len(orbit[0]))

    return orbit





class KalidoscopeGenerator:
    def __init__(self): #kal is inital kalidoscope when the application first loads up
        createDir(cfg.savePath)

        self.saves = []
        
        self.savedGroups = {}
        self.savedIntersections = {}
        self.savedFaces = {}
        
        for save in listdir(cfg.savePath):
            try:
                
                group =  np.load(f"{cfg.savePath}/{save}/group.npy",allow_pickle=True)
                intersection = np.load(f"{cfg.savePath}/{save}/intersections.npy",allow_pickle=True)
                faces = pickle.load(open(f"{cfg.savePath}/{save}/faces.pkl", 'rb'))

            except:
                continue
                
            self.saves.append(save)
            self.savedGroups[save] = group 
            self.savedIntersections[save] =  intersection
            self.savedFaces[save] =  faces
        
        self.projection = perspectiveProjection
    
    def initalizeKalidoscope(self,kal,seedSliders,rotationSliders):
        if kal.label in self.saves:
            self.group = self.savedGroups[kal.label]
            self.intersections = self.savedIntersections[kal.label]
            faces = self.savedFaces[kal.label]
            vertices = self.updatePoints(seedSliders,rotationSliders)
        else:
            normals = generatePlanes(kal.planeAngles)
            generators = [reflectionMatrix(normal) for normal in normals]
            
            self.group = findReflectionGroup(generators,kal.order)
            self.intersections = hyperplaneIntersections(normals)

            seed=getSeedPoint(seedSliders,self.intersections)
            vertices,faces = getPointsAndFaces(seed,self.group,self.projection,rotationSliders)

            #saves results
            createDir(f"{cfg.savePath}/{kal.label}")
            np.save(f"{cfg.savePath}/{kal.label}/group",self.group)
            np.save(f"{cfg.savePath}/{kal.label}/intersections",self.intersections)
            pickle.dump(faces,open(f"{cfg.savePath}/{kal.label}/faces.pkl", 'wb'))

            self.saves.append(kal.label)
            self.savedGroups[kal.label] = self.group
            self.savedIntersections[kal.label] = self.intersections
            self.savedFaces[kal.label] = faces
        
        newPolydata = getPolydata(vertices,faces)

        return newPolydata


    def updatePoints(self,seedSliders,rotationSliders):
        """ Used to update Points of the polytope using the same kalidoscope""" 
        seed=getSeedPoint(seedSliders,self.intersections)
        vertices = getPoints(seed,self.group,self.projection,rotationSliders)

        return vertices
    
    def changeProjection(self,typeStr):
        if typeStr == "orthographic":
            self.projection = orthographicProjection
        else:
            self.projection = perspectiveProjection