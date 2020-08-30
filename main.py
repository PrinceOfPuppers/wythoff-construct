import numpy as np
from mayavi import mlab

from traits.api import HasTraits, Range, Instance, List, Enum, observe
from traitsui.api import View, Item, Group, HGroup,RangeEditor,InstanceEditor,ListEditor,EnumEditor
from mayavi.core.ui.api import MayaviScene, SceneEditor, MlabSceneModel

import config as cfg

from groupGen import generatePlanes3D, orbitPoint,hyperplaneIntersections,findReflectionGroup,getSeedPoint
from helpers import reflectionMatrix

from mayAviPlotting import getPolydata

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

        self.seedSliders = SliderList(self.dim-1, 0.0, 1.0, 1/(self.dim-1)**2)


        kals = cfg.coxeterLookup(self.dim)
        kal = kals["[3,5]"]

        self.kalidoscope=DropDown(kals.keys())


        orbit = self.initalizeKalidoscope(kal)
        self.polydata = getPolydata(orbit)


        self.surfaceActor = mlab.pipeline.surface(self.polydata,opacity = 1,figure=self.scene.mayavi_scene).actor

        mlab.pipeline.surface(self.polydata,opacity = 1,representation='wireframe',color=(0,0,0),figure=self.scene.mayavi_scene)

        self.interactive = True
        
    def initalizeKalidoscope(self,kal):
        #normals = generatePlanes3D(np.pi/5,np.pi/3)
        normals = generatePlanes3D(kal.planeAngles[0],kal.planeAngles[1])
        generators = [reflectionMatrix(normal) for normal in normals]

        #self.group = findReflectionGroup(generators,120)
        self.group = findReflectionGroup(generators,kal.order)
        self.intersections = hyperplaneIntersections(normals)


        seed=getSeedPoint(iter(self.seedSliders),self.intersections)


        orbit = orbitPoint(seed,self.group)

        return orbit

    @observe("seedSliders:sliders:items")
    def seedSliders_changed(self,event):
        #interactive flag keeps slider from being recursivly updated due to mutation in this method
        if self.interactive:
            self.interactive = False
            sliderSum = self.seedSliders.getSum()
            if  sliderSum > 1:

                for i in range(len(self.seedSliders)):
                    if i!=event.index:
                        self.seedSliders[i]=round(self.seedSliders[i]-(sliderSum-1.0)/(len(self.seedSliders)-1.0),4)

            seed=getSeedPoint(iter(self.seedSliders),self.intersections)

            orbit = orbitPoint(seed,self.group)

            self.polydata.points = orbit

            self.interactive = True

    @observe("kalidoscope:enum")
    def kalidoscope_changed(self,event):
        self.interactive = False
        # saves slider values to return them after generation
        # we need to generate the shape in a configuration where all
        # polygons are visable (so we can connect them properly)
        sliderVals = []

        for i,sliderVal in enumerate(self.seedSliders):
            sliderVals.append(sliderVal)
            self.seedSliders[i]=(1/(self.dim))**2


        kal = cfg.coxeterLookup(self.dim)[event.new]

        orbit = self.initalizeKalidoscope(kal)

        newPolydata = getPolydata(orbit)
        self.polydata.polys = newPolydata.polys

        self.polydata.cell_data.scalars=newPolydata.cell_data.scalars
        self.polydata.cell_data.scalars.name = "celldata" 

        # we now generate the shape with the proper vertex configuration (with the
        # sliders in the configuartion they where before)
        for i in range(len(self.seedSliders)):
            self.seedSliders[i]=sliderVals[i]
        
        seed=getSeedPoint(iter(self.seedSliders),self.intersections)
        orbit = orbitPoint(seed,self.group)
        self.polydata.points = orbit

        self.interactive=True
    
    @observe("opacity")
    def opacity_changed(self,event):
        self.surfaceActor.property.opacity=event.new
    

    
if __name__ == "__main__":
    ui = UI()

    ui.configure_traits()
