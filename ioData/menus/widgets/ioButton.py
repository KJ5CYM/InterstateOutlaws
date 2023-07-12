from pycel import *

import Menu
class ioButton:
    api_version = 2
    def __init__(self,celEntity):
        self.message = ''
        self.owner = None
        self.entity = celEntity
        self.active = True
            
    def pcbillboard_select(self,pc,args):
        if self.active:
            params = parblock({'sender':self.entity.Name})
            if self.owner:
                self.owner.Behaviour.SendMessage(self.message, None, params)
            
    def pcbillboard_unselect(self,pc, args):
        pass
    
    def pcbillboard_doubleclick(self, pc, args):
        pass
    
    def setparameters(self, pc, args):
        self.message = args[getid('cel.parameter.message')]
        self.owner = args[getid('cel.parameter.owner')]

    def setactive(self, pc, args):
        if not self.active:
            self.active = True
            bb = celBillboard(self.entity).Billboard
            bb.SetTextFgColor(Menu.GetFontColor())
    
    def setinactive(self, pc, args):
        if self.active:
            self.active = False
            bb = celBillboard(self.entity).Billboard
            bb.SetTextFgColor(csColor(0, 0, 0))
    
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()