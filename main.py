import numpy as np
from mayavi import mlab

from traits.api import HasTraits, Range, Instance, List, observe
from traitsui.api import View, Item, Group, HGroup,RangeEditor,InstanceEditor
from mayavi.core.ui.api import MayaviScene, SceneEditor, MlabSceneModel

import config as cfg

from groupGen import generatePlanes,hyperplaneIntersections,findReflectionGroup,getSeedPoint,getPoints,getPointsAndFaces
from helpers import reflectionMatrix,getProjection

from mayAviPlotting import getPolydata
from uiElements import DropDown,SliderList

from datetime import datetime, timezone, timedelta

def getMili():
    return (datetime.now(timezone.utc) + timedelta(days=3)).timestamp() * 1e3



class UI(HasTraits):
    opacity = Range(0.,1.,1.)
    dimension = Range(3,5,3,mode='spinner')
    seedSliders=Instance(SliderList)
    rotationSliders = Instance(SliderList)
    kalidoscope = Instance(DropDown)
    scene = Instance(MlabSceneModel, ())

    rotationStr=""
    blank=''
    seedPointStr="Seed Point Selection:"

    view = View(Group(

                Item('scene', editor=SceneEditor(scene_class=MayaviScene),springy=True,show_label=False),
                Item('seedPointStr',show_label=False,style='readonly'),
                Item('seedSliders',editor = InstanceEditor(),style='custom',springy=False,show_label=False),
                Item('rotationStr',show_label=False,style='readonly'),
                Item('rotationSliders',editor = InstanceEditor(),style='custom',springy=False,show_label=False),
                
                HGroup(
                    Item('dimension',springy=True),
                    Item('blank',style='readonly',show_label=False,springy=True),
                    Item('kalidoscope',editor=InstanceEditor(),style='custom',springy=True),
                    ),
                Item('opacity',editor=RangeEditor())
                ),
                resizable = True,
            )

    def __init__(self):
        HasTraits.__init__(self)
        self.interactive=False
        
        
        self.projection = None
        self.seedSliders = SliderList(self.dimension-1, 0.0, 1.0, 1/(self.dimension-1)**2)

        if self.dimension>3:
            self.rotationStr="Rotation:"

            self.rotationSliders = SliderList(self.dimension-1,0.0,round(2*np.pi,4),0.0)
            self.projection = getProjection(iter(self.rotationSliders))
        else:
            self.rotationSliders = None

            

        kals = cfg.coxeterLookup(self.dimension)


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
    
    @observe("dimension")
    def dimension_changed(self,event):
        if self.interactive:
            self.interactive=False
            dim = event.new
            dimChange = event.new-event.old


            #add and adjust seed sliders
            self.seedSliders = SliderList(dim-1, 0.0, 1.0, 1/(dim-1)**2)

            #add and adjust rotation sliders
            if dim>3:
                #makes objects automaticaly transparent in higher dimensions
                if 1 - self.opacity <cfg.epsilon:
                    self.opacity = 0.4
                    
                self.rotationStr="Rotation:"
                self.rotationSliders = SliderList(dim-1,0.0,round(2*np.pi,4),0.0)
                self.projection = getProjection(iter(self.rotationSliders))
                
            else:
                self.rotationStr=""
                self.rotationSliders = None
                self.projection = None
            
            kals = cfg.coxeterLookup(dim)

            self.kalidoscope = DropDown(kals.keys())
            kal = kals[self.kalidoscope[0]]

            seed = self.initalizeKalidoscope(kal)

            vertices,faces = getPointsAndFaces(seed,self.group,self.projection)

            newPolydata = getPolydata(vertices,faces)

            self.polydata.points = newPolydata.points
            self.polydata.polys = newPolydata.polys

            self.polydata.cell_data.scalars=newPolydata.cell_data.scalars
            self.polydata.cell_data.scalars.name = "celldata" 

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

                        self.seedSliders[i]=self.seedSliders[i]-(sliderSum-1.0)/(nonZeroSliders-1.0)


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

    @observe("rotationSliders:sliders:items")
    def rotationSliders_changed(self,event):
        
        if self.interactive:
            self.interactive = False
            self.projection = getProjection(event.object)
            
            #updates points
            seed=getSeedPoint(iter(self.seedSliders),self.intersections)
            vertices = getPoints(seed,self.group,self.projection)

            self.polydata.points=vertices
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


            kal = cfg.coxeterLookup(self.dimension)[event.new]
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
