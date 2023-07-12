from pycel import *
import cPickle

import ioLoader
import Menu
import ioScroller
import ioDataBin

#The base stats screen which is shown when a game is finished
class ioStatsBase:
    api_version = 2
    
    #The server interaction screen
    def __init__(self,celEntity):
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']
        self.fconst = Menu.GetFontConstant()
        self.fcolor = Menu.GetFontColor()
  
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
        games.SetText('Game Finished')
        games.SetTextFgColor(self.fcolor)
        games.SetPosition(215000, 42000)

        self.buttons = Menu.ioMenu(self.entity)
        #self.buttons.addElement('<<', 'Back_click', [42500, 42500], [6000, 6000], self.fconst * 0.7, 'back-bg')
        mpgame = ioDataBin.Get('mpgame')
        if mpgame:
            txt = 'Return to Lobby'
            msg = 'Lobby_Click'
        else:
            txt = 'Return to Menu'
            msg = 'Menu_Click'
        self.buttons.addElement(txt, msg, (220000, 250000), (30000, 10000), self.fconst, 'button-bg')
    
    def leave(self):
        netgameclient = Entities['ioNetMgrCl']
        if netgameclient:
            netgameclient.Behaviour.SendMessage('leavegame', None, args)
        RemoveEntity(self.entity)

    def Lobby_Click(self, pc, args):
        self.leave()
        CreateEntity('ioGameSelect', self.blpython, 'ioGameSelect')
        
    def Menu_Click(self, pc, args):
        self.leave()
        CreateEntity('ioMainMenu', self.blpython, 'ioMainMenu')
        
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
        self.buttons.clear()
        
    def fillstats(self, pc, args):
        stats = cPickle.loads(args[parid('stats')])
    
    def Back_click(self, pc, args):
        netgame = Entities['ioNetMgrCl']
        netgame.Behaviour.SendMessage('leavegame', None, celGenericParameterBlock(0))
        name, behaviour = ioDataBin.Get('lastmenu', True)
        gamesel = CreateEntity(name, self.blpython, behaviour)
        RemoveEntity(self.entity)