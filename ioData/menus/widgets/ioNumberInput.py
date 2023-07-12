from cspace import *
from blcelc import *
from pycel import *

import Menu
class ioNumberInput:
    api_version = 2
    def __init__(self,celEntity):
        self.message = ''
        self.owner = None
        self.entity = celEntity
        self.active = False
        self.index = 0
        self.bb = celBillboard(self.entity).Billboard
        self.bb.SetText('')
        #Keep the text in a list so we can do insertion at cursor position
        self.text = ['0']
        self.pcinput = celCommandInput(self.entity)
        self.pcinput.Bind('key', 'keypress')
        self.pcinput.SetCookedMode(True)
        self.pcinput.SetSendTrigger(True)
        
        fconst = Menu.GetFontConstant()
        pos = self.bb.GetPosition()
        size = self.bb.GetSize()
        self.bb.SetTextOffset(size[0] / 2 - 2000, 1000)
        self.bb.SetText('0')
        #Add the directional arrows
        self.arrows = Menu.ioMenu(self.entity)
        self.arrows.addElement('<', 'left_click', pos, [6000, 6000], fconst * 0.8, 'unselection')
        self.arrows.addElement('>', 'right_click', [pos[0] + size[0] - 3000, pos[1]], [6000, 6000], fconst * 0.8, 'unselection')
            
    def pcbillboard_select(self, pc, args):
        params = parblock({'sender':self.entity.Name})
        if self.owner:
            self.owner.Behaviour.SendMessage(self.message, None, params)
            
    def pcbillboard_unselect(self, pc, args):
        pass
    
    def pcbillboard_doubleclick(self, pc, args):
        pass
    
    def setactive(self, pc, args):
        if not self.active:
            self.active = True
            text = self.bb.GetText()
            if text:
                if len(text) > 0:
                    self.text = list(text)
                    self.index = len(text)
                else:
                    self.text = []

            #Insert the cursor
            newtext = ''
            for i, letter in enumerate(self.text):
                #Insert the cursor at right position
                if i is self.index:
                    newtext += '|'
                newtext += letter
            #Also allow cursor to be at the end
            if self.index is len(newtext):
                newtext += '|'
            self.bb.SetText(newtext)
        
    def setinactive(self, pc, args):
        if self.active:
            self.active = False
            #Remove the cursor
            newtext = ''
            for i, letter in enumerate(self.text):
                newtext += letter
            self.bb.SetText(newtext)
    
    def setparameters(self, pc, args):
        self.message = args[getid('cel.parameter.message')]
        self.owner = args[getid('cel.parameter.owner')]
        
    def pccommandinput_keypress1(self, pc, args):
        trigger = args[getid('cel.parameter.trigger')]
        if self.active:
            self.handlekey(trigger)
   
    def handlekey(self, trigger):
        #Move the cursor
        if trigger == 'Left' and self.index > 0:
            self.index -= 1
        if trigger == 'Right' and self.index < len(self.text):
            self.index += 1
         
        #Insert a character
        elif trigger in '1234567890':
            self.text.insert(self.index, trigger)
            self.index += 1

        #Delete a character
        elif trigger == 'Back':
            if len(self.text) > 0:
                self.index -= 1
                self.text.pop(self.index)
        newtext = ''
        for i, letter in enumerate(self.text):
            #Insert the cursor at right position
            if i is self.index:
                newtext += '|'
            newtext += letter
        #Also allow cursor to be at the end
        if self.index is len(newtext):
            newtext += '|'
        self.bb.SetText(newtext)
        
    def pccommandinput_keypress0(self, pc, args):
        pass
    
    def pccommandinput_keypress_(self, pc, args):
        trigger = args[getid('cel.parameter.trigger')]
        if self.active:
            self.handlekey(trigger)
    
    def destruct(self, pc, args):
        self.arrows.clear()
        self.entity.PropertyClassList.RemoveAll()
    
    def left_click(self, pc, args):
        newtext = ''
        for i, letter in enumerate(self.text):
            newtext += letter
        newint = int(newtext) - 1
        self.text = list(str(newint))
        self.bb.SetText(str(newint))
        
    def right_click(self, pc, args):
        newtext = ''
        for i, letter in enumerate(self.text):
            newtext += letter
        newint = int(newtext) + 1
        self.text = list(str(newint))
        self.bb.SetText(str(newint))
    
    #This message allows to change our value that we store and display
    def set_value(self, pc, args):
        text = str(args[parid('value')])
        self.text = list(text)
        self.bb.SetText(text)