import numpy as np
from mayavi import mlab

from traits.api import HasTraits, Range, Instance, List, observe,Enum,String
from traitsui.api import View, Item, Group, HGroup,RangeEditor,InstanceEditor
from mayavi.core.ui.api import MayaviScene, SceneEditor, MlabSceneModel

import wythoff_construct.config as cfg

from wythoff_construct.coxeter import coxeterLookup
from wythoff_construct.groupGen import KalidoscopeGenerator



from wythoff_construct.uiElements import DropDown,SliderList

from datetime import datetime, timezone, timedelta

def getMili():
    return (datetime.now(timezone.utc) + timedelta(days=3)).timestamp() * 1e3



class Ui(HasTraits):
    opacity = Range(0.,1.,1.)
    
    dimension = Range(3,5,3,mode='enum')


    seedSliders=Instance(SliderList)
    rotationSliders = Instance(SliderList)
    kalidoscope = Instance(DropDown)
    scene = MlabSceneModel()

    projTypeValues = ("perspective","orthographic")
    projectionType = Enum(values = "projTypeValues")
    rotationStr=String("")
    seedPointStr="Seed Point Selection:"

    view = View(Group(

                Item('scene', editor=SceneEditor(scene_class=MayaviScene),springy=True,show_label=False),
                Item('seedPointStr',show_label=False,style='readonly'),
                Item('seedSliders',editor = InstanceEditor(),style='custom',springy=False,show_label=False),
                Item('rotationStr',show_label=False, style = 'readonly'),
                Item('rotationSliders',editor = InstanceEditor(),style='custom',springy=False,show_label=False,height=0.0),
                
                HGroup(
                    Item('dimension',springy=True,width=0.2),
                    
                    
                    Item('kalidoscope',editor=InstanceEditor(),style='custom',springy=True),
                    ),
                HGroup(
                    Item('projectionType',style = "simple"),
                    Item('opacity',editor=RangeEditor(low_label = "​", high_label = "​")),
                    )
                ),
                resizable = True,
                width = 0.5,
                height = 0.9,
                title= "Wythoff Construct"
            )

    def __init__(self):
        HasTraits.__init__(self)
        self.interactive=False
        
        self.seedSliders = SliderList(self.dimension-1,1/(self.dimension-1)**2)
        self.perspectiveEnum = "projection"

        

        if self.dimension>3:
            self.rotationStr="Rotation (multiple of 2π): "

            self.rotationSliders = SliderList(3**(self.dimension-2) - 3,0.0,self.dimension-2)
        else:
            self.rotationSliders = None

        kals = coxeterLookup(self.dimension)

        self.kalidoscope=DropDown(kals.keys())
        kal = kals[self.kalidoscope[0]]

        self.kalGen = KalidoscopeGenerator()
        self.polydata = self.kalGen.initalizeKalidoscope(kal,self.seedSliders,self.rotationSliders)

        self.surfaceActor = mlab.pipeline.surface(self.polydata, name="faces", opacity = 1,figure=self.scene.mayavi_scene,colormap = cfg.cmap).actor

        mlab.pipeline.surface(self.polydata, name="wireframe", opacity = 1,representation='wireframe',color=(0,0,0),figure=self.scene.mayavi_scene)

        self.interactive = True
        


    def updatePolydata(self,newPolydata):
        self.polydata.points = newPolydata.points
        self.polydata.polys = newPolydata.polys

        self.polydata.cell_data.scalars=newPolydata.cell_data.scalars
        self.polydata.cell_data.scalars.name = "celldata" 

    @observe("projectionType")
    def perspective_changed(self,event):
        self.kalGen.changeProjection(event.new)

        self.polydata.points = self.kalGen.updatePoints(self.seedSliders,self.rotationSliders)
    
    @observe("dimension")
    def dimension_changed(self,event):
        if self.interactive:
            self.interactive=False
            dim = event.new

            #add and adjust seed sliders
            self.seedSliders = SliderList(dim-1,1/(dim-1)**2)

            
            if dim>3:
                #adjust opacity
                self.opacity = 8/dim**2 - 0.1

                #add and adjust rotation sliders
                self.rotationStr="Rotation (multiple of 2π): "
                self.rotationSliders = SliderList(3**(dim-2) - 3,0.0,dim - 2)
                
            else:
                self.opacity = 1.0
                self.rotationStr=""
                self.rotationSliders = None
            
            kals = coxeterLookup(dim)

            self.kalidoscope = DropDown(kals.keys())
            kal = kals[self.kalidoscope[0]]

            newPolydata = self.kalGen.initalizeKalidoscope(kal,self.seedSliders,self.rotationSliders)
            self.updatePolydata(newPolydata)

            self.interactive = True

    
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
                        val = self.seedSliders[i]-(sliderSum-1.0)/(nonZeroSliders-1.0)

                        val = max(0,min(1,val)) #clamps value to between 0,1

                        self.seedSliders[i] = val


            self.polydata.points = self.kalGen.updatePoints(self.seedSliders,self.rotationSliders)

            self.interactive = True

    @observe("rotationSliders:sliders:items")
    def rotationSliders_changed(self,event):
        if self.interactive:
            self.interactive = False
            
            self.polydata.points = self.kalGen.updatePoints(self.seedSliders,self.rotationSliders)

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
                self.seedSliders[i]=(1/(self.dimension))**2


            kal = coxeterLookup(self.dimension)[event.new]
            t = getMili()

            newPolydata = self.kalGen.initalizeKalidoscope(kal,self.seedSliders,self.rotationSliders)
            self.updatePolydata(newPolydata)

            print("Generation Time: ",getMili()-t, " miliseconds")
            # we now generate the shape with the proper vertex configuration (with the
            # sliders in the configuartion they where before)
            for i in range(len(self.seedSliders)):
                self.seedSliders[i]=sliderVals[i]

            self.polydata.points = self.kalGen.updatePoints(self.seedSliders,self.rotationSliders)

            self.interactive=True
    
    @observe("opacity")
    def opacity_changed(self,event):
        #exponenet is to make the slider have a more linear feel
        self.surfaceActor.property.opacity= event.new**3
    