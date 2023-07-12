from pycel import *

import Menu
class ioTextInput:
    api_version = 2
    def __init__(self, celEntity):
        self.message = ''
        self.owner = None
        self.entity = celEntity
        self.active = False
        self.index = 0
        self.bb = celBillboard(self.entity).Billboard
        self.bb.SetText('')
        #Keep the text in a list so we can do insertion at cursor position
        self.text = []
        self.pcinput = celCommandInput(self.entity)
        self.pcinput.Bind('key', 'keypress')
        self.pcinput.SetCookedMode(True)
        self.pcinput.SetSendTrigger(True)
        #Maps shift + letter to cap(letter) and other symbols
        self.shiftmap = {
                        '`' : '~',
                        '1' : '!',
                        '2' : '@',
                        '3' : '#',
                        '4' : '$',
                        '5' : '%',
                        '6' : '^',
                        '7' : '&',
                        '8' : '*',
                        '9' : '(',
                        '0' : ')',
                        '-' : '_',
                        '=' : '+',
                        '[' : '{',
                        ']' : '}',
                        ';' : ':',
                        "'" : '"',
                        ',' : '<',
                        '.' : '.',
                        '/' : '?'
                        }
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            self.shiftmap[letter] = letter.upper()
        
        #Used for the skipnext message
        self.skip = False
            
    #If a keypress was used to activate the input, that key will also get triggered.
    #We ignore that here
    def skipnext(self, pc, args):
        self.skip = True
        
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
            self.updatebb()
        
    def setinactive(self, pc, args):
        if self.active:
            self.active = False
            #Remove the cursor
            newtext = ''
            self.bb.SetText(newtext.join(self.text))
    
    def setparameters(self, pc, args):
        self.message = args[getid('cel.parameter.message')]
        self.owner = args[getid('cel.parameter.owner')]
        
    def pccommandinput_keypress1(self, pc, args):
        trigger = args[getid('cel.parameter.trigger')]
        if self.active and not self.skip:
            self.handlekey(trigger)
        else:
            self.skip = False
   
    def handlekey(self, trigger):
        #Check if shift is pressed
        shifttest = trigger[1:]
        if shifttest.startswith('Shift'):
            key = trigger[7:]
            if len(key) == 1:
                trigger = self.shiftmap.get(key)

        if trigger:                
            #Move the cursor
            if trigger == 'Left' and self.index > 0:
                self.index -= 1
            if trigger == 'Right' and self.index < len(self.text):
                self.index += 1
            
            allowed = 'abcdefghijklmnopqrstuvwxyz'
            allowed += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            allowed += '0123456789'
            allowed += '`~!@#$%^&*()-_=+\{[}];:",<.>/?'
            
            #Insert a character
            if trigger in allowed:
                self.text.insert(self.index, trigger)
                self.index += 1
            #Insert a space
            elif trigger == 'Space':
                self.text.insert(self.index, ' ')
                self.index += 1
            #Delete a character
            elif trigger == 'Back':
                if len(self.text) > 0:
                    self.index -= 1
                    self.text.pop(self.index)
            #Enter was pressed, tell our owner
            elif trigger == 'Enter':
                params = parblock({'sender':self.entity.Name})
                self.owner.Behaviour.SendMessage('textinput_enter', None, params)
            self.updatebb()
        
    def updatebb(self):
        newtext = ''
        for i, letter in enumerate(self.text):
            #Insert the cursor at right position
            if self.active and (i is self.index):
                newtext += '|'
            newtext += letter
        #Also allow cursor to be at the end
        if self.active and (self.index is len(newtext)):
            newtext += '|'
        self.bb.SetText(newtext)
    
    #Clear our text
    def clear(self, pc, args):
        self.text = []
        self.index = 0
        self.bb.SetText('')
        
    def pccommandinput_keypress0(self, pc, args):
        pass
    
    def pccommandinput_keypress_(self, pc, args):
        trigger = args[getid('cel.parameter.trigger')]
        if self.active:
            self.handlekey(trigger)
    
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()