from pycel import *
import cPickle
import urllib2
import socket

import Menu
import ioScroller
import ioDataBin

#The options screen which containers video options + others (later, anyway)
class ioOptionsScreen:
    api_version = 2

    def __init__(self,celEntity):
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']
        self.fconst = Menu.GetFontConstant()
        self.fcolor = Menu.GetFontColor()

        bg = celAddBillboard(self.entity)
        bg.materialnamefast = 'game-bg'
        bg.x = 0
        bg.y = 0
        bg.width = 307200
        bg.height = 307200
        
        frame = celAddBillboard(self.entity)
        frame.materialnamefast = 'window-frame'
        frame.x = 40000
        frame.y = 40000
        frame.width = 227200
        frame.height = 227200
        
        windowbg = celAddBillboard(self.entity)
        windowbg.materialnamefast = 'options-window-bg'
        windowbg.x = 42500
        windowbg.y = 50000
        windowbg.width = 221200
        windowbg.height = 212200
        
        options = celAddBillboard(self.entity)
        options.text_font ='/outlaws/fonts/lcd2.ttf'
        options.text_font_size = self.fconst * 1.25
        options.text = 'Options'
        options.text_fg_color = self.fcolor
        options.x = 230000 
        options.y = 42000
 
        self.currentscreen = None
        
        self.menu = Menu.ioMenu(self.entity)
        back = self.menu.addElement('<<', 'Back_click', (42500, 42500), (6000, 6000), self.fconst * 0.7, 'back-bg')
        saved = self.menu.addElement('Save Page', 'Save_clicked', (228500, 247500), (30000, 8000), self.fconst, 'button-bg')
        self.saved = celBillboard(saved)
        
        self.scroller = ioScroller.ioScroller(self.entity, (42500, 62500), (42000, 185000))
        self.scroller.additem('Video', 'Video_click')
        #This will kill the scroll buttons
        self.scroller.menu.clear()
        self.Video_click(None, None)
   
        pcinput = celCommandInput(self.entity)
        pcinput.Bind('esc', 'exit')
        
    def Video_click(self, pc, args):
        self.scroller.selectname('Video')
        if self.currentscreen:
            RemoveEntity(self.currentscreen)
        self.currentscreen = CreateEntity('ioVideoOptions', self.blpython, 'ioVideoOptions')
        
    def pccommandinput_exit1(self, pc, args):
        q = CS_QUERY_REGISTRY (oreg, iEventQueue)
        if q:
            q.GetEventOutlet().Broadcast (csevQuit (oreg))

    def pccommandinput_exit_(self, pc, args):
        pass
    
    def pccommandinput_exit0(self, pc, args):
        pass

    #The user clicked on one of our items
    def scroller_select(self, pc, args):
        name = args[getid('cel.parameter.sender')]
        self.scroller.selectname(name)
    
    def destruct(self, pc, args):
        self.scroller.destruct()
        self.menu.clear()
        self.entity.PropertyClassList.RemoveAll()
        if self.currentscreen:
            RemoveEntity(self.currentscreen)
            
    def Back_click(self, pc, args):
        CreateEntity('ioMainMenu', self.blpython, 'ioMainMenu')
        RemoveEntity(self.entity)
        
    def Save_clicked(self, pc, args):
        self.currentscreen.Behaviour.SendMessage('save', None, None)
        #Temporarily write 'changes saved' to the button for feedback
        self.saved.text = 'Saved!'
        celTimer(self.entity).WakeUp(1000, False)
        
    def pctimer_wakeup(self, pc, args):
        celTimer(self.entity).Clear()
        self.saved.text = 'Save Page'