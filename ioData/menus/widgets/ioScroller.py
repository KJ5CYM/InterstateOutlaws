from pycel import *
import Menu

#The scroller is not meant to be used as part of a menu
class ioScroller:
    def __init__(self, owner, pos, dims, name = ''):
        self.items = []
        self.names = []
        self.name = name
        self.blpython = BehaviourLayers['blpython']
        self.pos = pos
        self.dims = dims
        self.owner = owner
        self.fconst = Menu.GetFontConstant()
        self.fcolor = Menu.GetFontColor()
        self.selectedname = ''
        self.selectedindex = -1
        self.spacing = 10000
        #The amount from 0 to 1 which we have scrolled.
        self.scrolled = 0.0
        #The index of our topmost item
        self.topindex = 0
        
        #If false, we don't let two items with same name/text to be added
        self.allowdoubles = False
        
        #We use an ioMenu to store our buttons
        self.menu = Menu.ioMenu(owner)
        self.bsize = (7500, 7500)
        bx = self.pos[0] + self.dims[0] - self.bsize[0]
        bposup = (bx, self.pos[1])
        bposdown = (bx, self.pos[1] + self.dims[1] - self.bsize[1])
        fc = Menu.GetFontConstant()
        #The name is appended to the messages
        self.menu.addElement('', 'scroller_up' + name, bposup, self.bsize, fc, 'scroller-up')
        self.menu.addElement('', 'scroller_down' + name, bposdown, self.bsize, fc, 'scroller-down')
        
    #Add an item to the scroller     
    def additem(self, name, message):
        #Check that its not a dupe
        if (name not in self.names) or self.allowdoubles:
            button = pl.CreateEntity(name, self.blpython, 'ioButton')
            pars = parblock({'owner' : self.owner, 'message' : message})
            button.Behaviour.SendMessage('setparameters', None, pars)
            pcbb = celBillboard(button)
            pcbb.EnableEvents(True)
            buttonbb = pcbb.Billboard
            pcbb.x = self.pos[0]
            pcbb.width = self.dims[0] - self.bsize[0]
            pcbb.height = self.spacing
            pcbb.text_offset = csVector2(3000, 2000)
            pcbb.text_fg_color = self.fcolor
            pcbb.text_font_size = self.fconst
            pcbb.text_font = '/outlaws/fonts/lcd2.ttf'
            self.items.append(button)
            self.names.append(name)
            index = len(self.names) - 1
            self.isvisible(index)
            if self.isvisible(index):
                self.showitem(index)
            self.scrolled = self.topindex / len(self.items)
            
    #Show an item           
    def showitem(self, index):
        pcbb = celBillboard(self.items[index])
        buttonbb = pcbb.Billboard
        pcbb.y = self.getyposition(index)
        if index is self.selectedindex:
            mat = 'selection'
        else:
            mat = 'unselection'
        pcbb.materialnamefast = mat
        pcbb.text = self.names[index]

    #The most items our scroller can show at once
    def getmaxvisible(self):
        maxvisible = int(self.dims[1] / self.spacing) - 1
        if maxvisible < 1:
           maxvisible = 1
        return maxvisible
            
    #Hide an item
    def hideitem(self, index):
        pcbb = celBillboard(self.items[index])
        buttonbb = pcbb.Billboard
        pcbb.materialnamefast = ''
        pcbb.text = ''
        
    def destruct(self):
        self.menu.clear()
        self.clear()
        
    def clear(self):
        self.scrolled = 0.0
        self.topindex = 0.0
        self.names = []
        for i in xrange(len(self.items)):
            item = self.items.pop(0)
            RemoveEntity(item)
            
    #Select an item by its name.
    def selectname(self, name):
        self.selectedname = name
        for i, item in enumerate(self.items):
            bb = celBillboard(item).Billboard
            if bb.GetText() == name:
                self.selectedindex = i
                bb.SetMaterialName('selection')
            else:
                bb.SetMaterialName('unselection')
    
    #Select an item by its index.
    def selectindex(self, index):
        self.selectedindex = index
        for i, item in enumerate(self.items):
            bb = celBillboard(item).Billboard
            if index == i:
                bb.SetMaterialName('selection')
                self.selectedname = bb.GetText()
            else:
                bb.SetMaterialName('unselection')
                
    #Change the amount the scroller is scrolled, from 0 - 1
    def setscrolled(self, amount):
        if amount >= 0.0 and amount <= 1.0:
            self.scrolled = amount
            self.topindex =  int(self.scrolled * len(self.items))
            self.update()
     
     #Show all items that can be shown within our boundaries
    def update(self):
        for i in xrange(len(self.items)):
            if self.isvisible(i):
                self.showitem(i)
            else:
                self.hideitem(i)
                
    #Scroll down by 1 item
    def scrolldown(self):
        if self.topindex + self.getmaxvisible() < len(self.items) - 1:
            self.topindex += 1
            self.update()
            
    #Scroll up by 1 item
    def scrollup(self):
        if self.topindex >  0:
            self.topindex -= 1
            self.update()
    
    #Work out the y coordinate of an item, taking into account our scrollage
    def getyposition(self, index):
        return int(self.pos[1] + ((index - self.topindex ) * self.spacing))
    
    #Work out whether an item is able to be seen in this scroller.
    def isvisible(self, index):
        return (index >= self.topindex) and (index <= self.topindex + self.getmaxvisible())
