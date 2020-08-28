import math 
import numpy as np 
import timeit

import config as cfg



#takes in unit normal and plane as np arrays 
#both must have same dimesion
def reflectInPlane(point,normal):
    """takes in unit normal and plane as np arrays"""
    return point - 2*np.dot(normal,point)*normal






    

if __name__ == '__main__':
    import timeit
    norm = np.array((1,0,0))
    point = np.array((1,1,1))

    point2 = reflectInPlane(point,norm)

    print(point,point2)