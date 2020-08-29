import numpy as np
from mayavi import mlab

from traits.api import HasTraits, Range, Instance,on_trait_change,List,observe
from traitsui.api import View, Item, Group,RangeEditor,InstanceEditor,ListEditor
from mayavi.core.ui.api import MayaviScene, SceneEditor, MlabSceneModel

from groupGen import generatePlanes3D, orbitPoint,hyperplaneIntersections,findReflectionGroup,getSeedPoint
from helpers import reflectionMatrix,areEqual

from mayAviPlotting import getPolydata


class SliderList(HasTraits):
    sliders = List()
    
    def __len__(self):
        return len(self.sliders)

    def getVal(self,i):
        element = self.sliders[i]
        if type(element)==float:
            return element
        return element.value
            
    def getVals(self):
        return [self.getVal(i) for i in range(len(self))]
    
    def getSum(self):
        n = 0
        for i in range(len(self)):
            n+=self.getVal(i)
        return n

    def addSlider(self,low,high,val):
        self.sliders.append(Range(low,high))
        self.sliders[-1] = val

    def setSlider(self,i,val):
        self.sliders[i] = val

    def moveSlider(self,i,delta):
        self.sliders[i] = delta + self.getVal(i)

    traits_view = View(Group(Item('sliders',
                                style='custom',
                                editor=ListEditor(editor=RangeEditor())),
                            orientation='vertical',
                            scrollable=True,
                            show_labels=False),
                            #resizable = True,

                            )

class MyModel(HasTraits):
    sliders=Instance(SliderList)
    scene = Instance(MlabSceneModel, ())
    view = View(Group(Item('scene', editor=SceneEditor(scene_class=MayaviScene),springy=True),
                Item('sliders',editor = InstanceEditor(),style='custom',),
                show_labels=False,),
                
                resizable = True
                )


    def __init__(self):
        HasTraits.__init__(self)
        self.sliders = SliderList()
        self.sliders.addSlider(0.0,1.0, 0.25)
        self.sliders.addSlider(0.0,1.0, 0.25)


        #self.s = mlab.surf(x, y, np.asarray(x*1.5, 'd'), figure=self.scene.mayavi_scene)

        normals = generatePlanes3D(np.pi/5,np.pi/3)
        generators = [reflectionMatrix(normal) for normal in normals]

        self.group = findReflectionGroup(generators,120)

        self.intersections = hyperplaneIntersections(normals)


        seed=getSeedPoint(self.sliders.getVals(),self.intersections)


        orbit = orbitPoint(seed,self.group)

        
        self.polydata = getPolydata(orbit)
        

        mlab.pipeline.surface(self.polydata,opacity = 1,figure=self.scene.mayavi_scene)
        mlab.pipeline.surface(self.polydata,opacity = 1,representation='wireframe',color=(0,0,0),figure=self.scene.mayavi_scene)
        
        
    @observe("sliders:sliders:items")
    def slider_changed(self,event):
        seed=getSeedPoint(self.sliders.getVals(),self.intersections)

        orbit = orbitPoint(seed,self.group)

        self.polydata.points = orbit

my_model = MyModel()

#mlab.show()
my_model.configure_traits()
