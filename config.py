from numpy import pi
from math import factorial

epsilon = 10e-3
enableH_4 = False # too many edges to look nice with projection

exponents=["⁰", "¹","²", "³", "⁴", "⁵", "⁶","⁷",  "⁸", "⁹"]
def expStr(num):
    exp=""
    for char in str(num):
        exp+=exponents[int(char)]
    return exp

class Kalidoscope:
    def __init__(self, order, planeAngles, label):
        self.order= order
        self.planeAngles = planeAngles
        self.label = label

# special familes of kalidoscopes

I_h = Kalidoscope(120,[pi/5,pi/3],"[3,5]")
H_4 = Kalidoscope(14400,[pi/5,pi/3,pi/3],f"[3{expStr(2)},5]") 

# 2 Infinite familys of kalidoscopes
def getFamily(dim,familyNum):
    planeAngles=[]

    #simplex
    if familyNum==0:
        order = factorial((dim+1)) # order of S_n+1
        for _ in range(dim-1):
            planeAngles.append(pi/3)

        label = f"[3{expStr(dim-1)}]"

    #hypercube and cross polytope
    else:
        order = (2**dim)*factorial(dim)

        planeAngles.append(pi/4)
        for _ in range(dim-2):
            planeAngles.append(pi/3)

        if dim==3:
            subString = "3"
        else:
            subString =f"3{expStr(dim-2)}"

        label = f"[{subString},4]"
    return Kalidoscope(order,planeAngles,label)


def coxeterLookup(dim):
    k1 = getFamily(dim,0)
    k2 = getFamily(dim,1)

    if dim == 3:
        kals = (k1,k2,I_h)

    elif dim == 4:
        if enableH_4: #H_4 symmetry group is so large it looks like a black ball
            kals= (k1,k2,H_4)
        else:
            kals=(k1,k2)

    else:
        kals = [k1] # B_5 crashes convexhull so only A_5 is avalible
        
    return {kal.label:kal for kal in kals}