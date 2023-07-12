from cspace import *
from blcelc import *
from pycel import *
import Menu
class ioDropDown:
    api_version = 2
    def __init__(self, celEntity):
        self.message = ''
        self.owner = None
        self.entity = celEntity
        self.items = []
        self.active = False
        self.bb = celBillboard(self.entity).Billboard
        self.bb.SetText('')
        self.fconst = Menu.GetFontConstant()
        self.menu = Menu.ioMenu(self.entity)
        self.locked = False
            
    def pcbillboard_select(self, pc, args):
        params = parblock({'sender':self.entity.Name})
        if self.owner:
            self.owner.Behaviour.SendMessage(self.message, None, params)
            
    def pcbillboard_unselect(self,celEntity,args):
        pass
    
    def pcbillboard_doubleclick(self, pc, args):
        pass
    
    def setparameters(self, pc, args):
        self.message = args[getid('cel.parameter.message')]
        self.owner = args[getid('cel.parameter.owner')]
        
    def additem(self, pc, args):
        name = args[getid('cel.parameter.Name')]
        self.items.append(name)
        
    def setactive(self, pc, args):
        if not self.locked:
            if not self.active:
                for item in self.items:
                    self.menu.addElement(item, 'item_clicked', [0, 0], [67000, 8000], self.fconst * 0.8, 'dropdown-bg')
                x, y = self.bb.GetPosition()
                self.menu.align([x, y], [0, 7000])
                self.active = True
        
    def setinactive(self, pc, args):
        self.active = False
        self.menu.clear()
        
    def item_clicked(self, pc, args):
        name = args[getid('cel.parameter.sender')]
        self.active = False
        self.menu.clear()
        self.bb.SetText(name)
        params = parblock({'sender':self.entity.Name})
        if self.owner:
            self.owner.Behaviour.SendMessage(self.message + '_item', None, params)
        
    def selectindex(self, pc, args):
        if not self.locked:
            index = int(args[getid('cel.parameter.index')])
            self.active = False
            self.menu.clear()
            self.bb.SetText(self.items[index])
        
    def destruct(self, pc, args):
        self.menu.clear()
        self.entity.PropertyClassList.RemoveAll()

    def setlocked(self, pc, args):
        self.locked = True

    def setunlocked(self, pc, args):
        self.locked = False