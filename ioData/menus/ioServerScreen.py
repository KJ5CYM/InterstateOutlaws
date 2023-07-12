from pycel import *
import cPickle

import ioLoader
import Menu
import ioScroller
import ioDataBin

class ioServerScreen:
    api_version = 2
    
    #The server interaction screen
    def __init__(self,celEntity):
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']
        self.fconst = Menu.GetFontConstant()
        self.fcolor = Menu.GetFontColor()
        
        self.gamedata = None
        bg = celAddBillboard(self.entity).Billboard
        bg.SetMaterialName('hostjoin-bg')
        bg.SetPosition(0,0)
        bg.SetSize(307200,307200)
        
        frame = celAddBillboard(self.entity).Billboard
        frame.SetMaterialName('window-frame')
        frame.SetPosition(40000,40000)
        frame.SetSize(227200,227200)
        
        windowbg = celAddBillboard(self.entity).Billboard
        windowbg.SetMaterialName('half-black')
        windowbg.SetPosition(42500,50000)
        windowbg.SetSize(221200,212200)
        
        games = celAddBillboard(self.entity).Billboard
        games.SetTextFont('/outlaws/fonts/lcd2.ttf', self.fconst * 1.25)
        games.SetText('Server')
        games.SetTextFgColor(self.fcolor)
        games.SetPosition(235000, 42000)

        self.label = celAddBillboard(self.entity).Billboard
        self.label.SetTextFont('/outlaws/fonts/lcd2.ttf', self.fconst)
        self.label.SetTextFgColor(self.fcolor)
        self.label.SetPosition(45000, 62000)

        self.labels = Menu.ioMenu(self.entity)
        
        self.buttons = Menu.ioMenu(self.entity)
        self.buttons.addElement('<<', 'Back_click', [42500, 42500], [6000, 6000], self.fconst * 0.7, 'back-bg')
        
        pcinput = celCommandInput(self.entity)
        pcinput.Bind('esc', 'exit')

    def pccommandinput_exit1(self, pc, args):
        pass

    def pccommandinput_exit_(self, pc, args):
        pass
    
    def pccommandinput_exit0(self, pc, args):
        pass
    
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
        self.buttons.clear()
        self.labels.clear()
        
    def Back_click(self, pc, args):
        netgame = Entities['ioNetMgrCl']
        netgame.Behaviour.SendMessage('leavegame', None, celGenericParameterBlock(0))
        name, behaviour = ioDataBin.Get('lastmenu', True)
        gamesel = CreateEntity(name, self.blpython, behaviour)
        RemoveEntity(self.entity)

    def setlabel(self, pc, args):
        text = args[getid('cel.parameter.text')]
        self.label.SetText(text)

    def setgameinfo(self, pc, args):
        data = cPickle.loads(args[getid('cel.parameter.data')])
        self.labels.clear()
        self.labels.addElement('Name: %s' % data[0], '', [0, 0], [0, 0], self.fconst, '')
        self.labels.addElement('Map: %s' % data[1], '', [0, 0], [0, 0], self.fconst, '')
        self.labels.addElement('Game Type: %s' % data[2], '', [0, 0], [0, 0], self.fconst, '')
        self.labels.addElement('Players: %s / %s' % (data[3], data[4]), '', [0, 0], [0, 0], self.fconst, '')
        self.labels.addElement('Max Score: %s' % data[5], '', [0, 0], [0, 0], self.fconst, '')
        self.labels.addElement('Password: %s' % data[6], '', [0, 0], [0, 0], self.fconst, '')
        self.labels.addElement('Notes: %s' % data[7], '', [0, 0], [0, 0], self.fconst, '')
        compatversion = data[8]
        versionname = data[9]
        self.labels.addElement('Version: %s' % versionname, '', [0, 0], [0, 0], self.fconst, '')
        self.labels.align([44000, 82000], [0, 8000])

    def maploaded(self, pc, args):
        self.entity.PropertyClassList.Remove(0)
        self.label.SetText('Map loaded')