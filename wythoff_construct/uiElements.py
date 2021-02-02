
from traits.api import HasTraits, Range, List, Enum, Int
from traitsui.api import View, Item, Group, ListEditor,RangeEditor



class SliderList(HasTraits):

    #used for iterating
    index = 0
    low = 0.
    high = 1.
    
    listedit= ListEditor(columns = 3)
    sliders = List( 
                    Range(low="low",high="high",editor = RangeEditor(low_label = "​", high_label = "​") ), 
                    editor = listedit,
                    comparison_mode=1, 
                    cols= 3
                    )

    def __init__(self,numEntries,val,numColumns = 1):
        HasTraits.__init__(self)
        for _ in range(numEntries):
            self.listedit.columns = numColumns
            self.addSlider(val)

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
        if type(element)==float or type(element)==int:
            return element
        return element.value

    def __setitem__(self,i,val):
        self.sliders[i] = round(val,4)

    def getSum(self):
        n = 0
        for i in range(len(self)):
            n+=self[i]
        return n

    def addSlider(self,val):
        self.sliders.append(val)
        self[-1] = val

    def removeSlider(self):
        self.sliders.pop()

    view = View(Group(
                Item('sliders',
                       #style='custom',

                       style='readonly'
                       ),
                    orientation='vertical',
                    scrollable=True,
                    
                    show_labels=False
                    ),
                resizable = True,
                )

class DropDown(HasTraits):
    entries=()
    enum = Enum(values='entries',cols=5)
    traits_view = View(Group(Item('enum',style='custom'),orientation='vertical',show_labels=False))

    def __init__(self,entries):
        HasTraits.__init__(self)
        self.entries = [entry for entry in entries]
    
    def __setitem__(self,i,entry):
        self.entries[i] = entry

    def __getitem__(self,i):
        self.enum = self.entries[i]
        return self.entries[i]
    
    def reset(self,entries):
        self.entries = [entry for entry in entries]


        