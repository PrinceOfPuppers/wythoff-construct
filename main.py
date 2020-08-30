import numpy as np
from mayavi import mlab

from traits.api import HasTraits, Range, Instance, List, Enum, observe
from traitsui.api import View, Item, Group, HGroup,RangeEditor,InstanceEditor,ListEditor,EnumEditor
from mayavi.core.ui.api import MayaviScene, SceneEditor, MlabSceneModel

import config as cfg

from groupGen import generatePlanes,hyperplaneIntersections,findReflectionGroup,getSeedPoint,getPoints,getPointsAndFaces
from helpers import reflectionMatrix,mapArrayList

from mayAviPlotting import getPolydata
from datetime import datetime, timezone, timedelta
def getMili():
    return (datetime.now(timezone.utc) + timedelta(days=3)).timestamp() * 1e3

class SliderList(HasTraits):
    sliders = List(comparison_mode=1)
    #used for iterating
    index = 0
    def __init__(self,num,low,high,val):
        HasTraits.__init__(self)
        for _ in range(num):
            self.addSlider(low,high,val)

    def __len__(self):
        return len(self.sliders)

    def __next__(self):
        if self.index<len(self):
            val = self[self.index]
            self.index+=1
            return val
        else:
            self.index = 0
            raise StopIteration

    def __iter__(self):
        return self

    def __getitem__(self,i):
        element = self.sliders[i]
        if type(element)==float:
            return element
        return element.value

    def __setitem__(self,i,val):
        self.sliders[i] = val

    def getSum(self):
        n = 0
        for i in range(len(self)):
            n+=self[i]
        return n

    def addSlider(self,low,high,val):
        self.sliders.append(Range(low,high))
        self.sliders[-1] = val


    traits_view = View(Group(Item('sliders',
                                style='custom',
                                editor=ListEditor(editor=RangeEditor())
                                ),
                            #orientation='vertical',
                            #scrollable=True,
                            show_labels=False),
                            #resizable = True,
                            )

class DropDown(HasTraits):
    entries=()
    enum = Enum(values='entries')
    traits_view = View(Group(Item('enum',style='custom'),orientation='vertical',show_labels=False))

    def __init__(self,entries):
        HasTraits.__init__(self)
        self.entries = [entry for entry in entries]
    
    def __setitem__(self,i,entry):
        self.entries[i] = entry

    def __getitem__(self,i):
        self.enum = self.entries[i]
        return self.entries[i]

        

class UI(HasTraits):
    opacity = Range(0.,1.,1.)
    seedSliders=Instance(SliderList)
    kalidoscope = Instance(DropDown)
    scene = Instance(MlabSceneModel, ())
    view = View(Group(
                Group(Item('scene', editor=SceneEditor(scene_class=MayaviScene),springy=True),
                Item('seedSliders',editor = InstanceEditor(),style='custom',),show_labels=False,),
                HGroup(
                    Item('kalidoscope',editor=InstanceEditor(),style='custom'),
                    Item('opacity',editor=RangeEditor())
                    ),
                ),
                resizable = True,
    )

    def __init__(self):
        HasTraits.__init__(self)
        self.interactive=False
        self.dim = 3
        
        #self.projection = np.array([(1,1,-1,-1),(-1,1,-1,1),(1,-1,-1,1)])
        self.projection = None
        self.seedSliders = SliderList(self.dim-1, 0.0, 1.0, 1/(self.dim-1)**2)


        kals = cfg.coxeterLookup(self.dim)


        self.kalidoscope=DropDown(kals.keys())
        kal = kals[self.kalidoscope[0]]

        seed = self.initalizeKalidoscope(kal)

        vertices,faces = getPointsAndFaces(seed,self.group,self.projection)
        self.polydata = getPolydata(vertices,faces)

        self.surfaceActor = mlab.pipeline.surface(self.polydata, name="faces", opacity = 1,figure=self.scene.mayavi_scene).actor
        mlab.pipeline.surface(self.polydata, name="wireframe", opacity = 1,representation='wireframe',color=(0,0,0),figure=self.scene.mayavi_scene)

        self.interactive = True
        
    def initalizeKalidoscope(self,kal):
        normals = generatePlanes(kal.planeAngles)
        generators = [reflectionMatrix(normal) for normal in normals]

        self.group = findReflectionGroup(generators,kal.order)
        self.intersections = hyperplaneIntersections(normals)
        seed=getSeedPoint(iter(self.seedSliders),self.intersections)

        return seed

    @observe("seedSliders:sliders:items")
    def seedSliders_changed(self,event):
        #interactive flag keeps slider from being recursivly updated due to mutation in this method

        if self.interactive:
            self.interactive = False

            #drops other sliders if sum is greater than 1
            sliderSum = self.seedSliders.getSum()
            if  sliderSum > 1:

                nonZeroSliders = len(self.seedSliders)
                for slider in self.seedSliders:
                    if slider<=0:
                        nonZeroSliders-=1
                    
                for i in range(len(self.seedSliders)):
                    if i!=event.index and self.seedSliders[i]>0:

                        self.seedSliders[i]=round(self.seedSliders[i]-(sliderSum-1.0)/(nonZeroSliders-1.0),4)


            #updates points
            seed=getSeedPoint(iter(self.seedSliders),self.intersections)
            vertices = getPoints(seed,self.group,self.projection)
            
            self.polydata.points=vertices

            #clamps sliders to between 0 and 1
            for i in range(len(self.seedSliders)):
                if self.seedSliders[i]>1.:
                    self.seedSliders[i]=1.

                elif self.seedSliders[i]<0.:
                    self.seedSliders[i]=0.

            self.interactive = True

    @observe("kalidoscope:enum")
    def kalidoscope_changed(self,event):
        if self.interactive:
            self.interactive = False
            # saves slider values to return them after generation
            # we need to generate the shape in a configuration where all
            # polygons are visable (so we can connect them properly)
            sliderVals = []

            for i,sliderVal in enumerate(self.seedSliders):
                sliderVals.append(sliderVal)
                self.seedSliders[i]=(1/(self.dim))**2


            kal = cfg.coxeterLookup(self.dim)[event.new]
            t = getMili()
            seed = self.initalizeKalidoscope(kal)

            vertices,faces = getPointsAndFaces(seed,self.group,self.projection)

            newPolydata = getPolydata(vertices,faces)

            self.polydata.polys = newPolydata.polys

            self.polydata.cell_data.scalars=newPolydata.cell_data.scalars
            self.polydata.cell_data.scalars.name = "celldata" 

            print("gentime: ",getMili()-t, " miliseconds")
            # we now generate the shape with the proper vertex configuration (with the
            # sliders in the configuartion they where before)
            for i in range(len(self.seedSliders)):
                self.seedSliders[i]=sliderVals[i]

            seed=getSeedPoint(iter(self.seedSliders),self.intersections)
            vertices = getPoints(seed,self.group,self.projection)


            self.polydata.points = vertices

            self.interactive=True
    
    @observe("opacity")
    def opacity_changed(self,event):
        #exponenet is to make the slider have a more linear feel
        self.surfaceActor.property.opacity= event.new**3
    


if __name__ == "__main__":
    ui = UI()

    ui.configure_traits()
