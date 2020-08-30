import numpy as np
from mayavi import mlab

from traits.api import HasTraits, Range, Instance,List,observe
from traitsui.api import View, Item, Group,RangeEditor,InstanceEditor,ListEditor
from mayavi.core.ui.api import MayaviScene, SceneEditor, MlabSceneModel

import config as cfg

from groupGen import generatePlanes3D, orbitPoint,hyperplaneIntersections,findReflectionGroup,getSeedPoint
from helpers import reflectionMatrix

from mayAviPlotting import getPolydata


class SliderList(HasTraits):
    sliders = List(comparison_mode=1)
    #used for iterating
    index = 0

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
                            orientation='vertical',
                            scrollable=True,
                            show_labels=False),
                            #resizable = True,
                            )

class UI(HasTraits):
    seedSliders=Instance(SliderList)
    scene = Instance(MlabSceneModel, ())
    view = View(Group(Item('scene', editor=SceneEditor(scene_class=MayaviScene),springy=True),
                Item('seedSliders',editor = InstanceEditor(),style='custom',),
                show_labels=False,),
                resizable = True
                )


    def __init__(self):
        HasTraits.__init__(self)
        self.interactive=False

        self.seedSliders = SliderList()
        self.seedSliders.addSlider(0.0,1.0, 0.25)
        self.seedSliders.addSlider(0.0,1.0, 0.25)


        #self.s = mlab.surf(x, y, np.asarray(x*1.5, 'd'), figure=self.scene.mayavi_scene)

        kalidoscopes = cfg.coxeterLookup(3)
        
        kal = kalidoscopes[2]

        #normals = generatePlanes3D(np.pi/5,np.pi/3)
        normals = generatePlanes3D(kal.planeAngles[0],kal.planeAngles[1])
        generators = [reflectionMatrix(normal) for normal in normals]

        #self.group = findReflectionGroup(generators,120)
        self.group = findReflectionGroup(generators,kal.order)
        self.intersections = hyperplaneIntersections(normals)


        seed=getSeedPoint(iter(self.seedSliders),self.intersections)


        orbit = orbitPoint(seed,self.group)

        
        self.polydata = getPolydata(orbit)
        

        mlab.pipeline.surface(self.polydata,opacity = 1,figure=self.scene.mayavi_scene)
        mlab.pipeline.surface(self.polydata,opacity = 1,representation='wireframe',color=(0,0,0),figure=self.scene.mayavi_scene)

        self.interactive = True
        
        
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


if __name__ == "__main__":
    ui = UI()

    ui.configure_traits()
