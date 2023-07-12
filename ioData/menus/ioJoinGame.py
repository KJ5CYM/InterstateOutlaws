from pycel import *
import cPickle
import os

import ioLoader
import Menu
import ioScroller
import ioDataBin
import ioNetHelper

#The screen which lets you choose if you want to join a game before actually doing it.
class ioJoinGame:
    api_version = 2
    #The server selection screen
    def __init__(self,celEntity):
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']
        self.fconst = Menu.GetFontConstant()
        self.fcolor = Menu.GetFontColor()
        self.lobbyserver = None
        self.gameserver = [None, None]
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
        windowbg.SetMaterialName('join-window-bg')
        windowbg.SetPosition(42500,50000)
        windowbg.SetSize(221200,212200)
        
        games = celAddBillboard(self.entity).Billboard
        games.SetTextFont('/outlaws/fonts/lcd2.ttf', self.fconst * 1.25)
        games.SetText('Host')
        games.SetTextFgColor(self.fcolor)
        games.SetPosition(245000, 42000)


        spacing = 8000
        #Initial y position of labels which keeps getting stacked on
        pos = 52000
        ypos = []
        xpos = 44000
        for i in xrange(8):
            ypos.append(pos)
            pos += spacing
        #How awesome am I! Store the positions in a dictionary.
        labels = []
        labels = {}
        labels['Notes'] = [150000, ypos[0]]
        labels['Game Name'] = [xpos, ypos[0]]
        labels['Location'] = [xpos, ypos[1]]
        labels['Game Type'] = [xpos, ypos[2]]
        labels['Players'] = [xpos, ypos[3]]
        labels['Max Score'] = [90000, ypos[3]]
        labels['Password'] = [xpos, ypos[4]]
        
        labels['Join With Name'] = [xpos, ypos[6]]
        labels['Join With Password'] = [xpos, ypos[7]]
        for name, pos in labels.items():
            bb = celAddBillboard(self.entity).Billboard
            bb.SetTextFont('/outlaws/fonts/lcd2.ttf', self.fconst * 0.8)
            bb.SetText(name)
            bb.SetTextFgColor(self.fcolor)
            bb.SetPosition(pos[0], pos[1])
        
        self.buttons = Menu.ioMenu(self.entity)
        self.buttons.addElement('<<', 'Back_click', [42500, 42500], [6000, 6000], self.fconst * 0.7, 'back-bg')
        self.buttons.addElement('Garage', 'Garage_click', [44000, 186000], [19000, 8000], self.fconst, 'button-bg')
        launch = self.buttons.addElement('Launch', 'Launch_click', [244000, 186000], [19000, 8000], self.fconst, 'button-bg')
        launch.Behaviour.SendMessage('setinactive', None, celGenericParameterBlock(0))
        
        #These aren't really inputs, i'm just reusing code from the host game screen
        self.inputs = Menu.ioMenu(self.entity)
        self.inputs.addElement('name', '', [68000, ypos[0]], [65000, 6000], self.fconst * 0.8, 'unselection')
        self.inputs.addElement('location', '', [68000, ypos[1]], [65000, 6000], self.fconst * 0.8, 'unselection')
        self.inputs.addElement('gametypes', '', [68000, ypos[2]], [65000, 6000], self.fconst * 0.8, 'unselection')
        self.inputs.addElement('players', '', [68000, ypos[3]], [18000, 6000], self.fconst * 0.8, 'unselection')
        self.inputs.addElement('maxscore', '', [114000, ypos[3]], [18000, 6000], self.fconst * 0.8, 'unselection')
        self.inputs.addElement('password', '', [68000, ypos[4]], [65000, 6000], self.fconst * 0.8, 'unselection')
        self.inputs.addElement('notes', '', [150000, ypos[1]], [100000, 8000], self.fconst * 0.8, 'button-bg')
        
        #The ones which are really inputs, the user can change these
        self.nameinp = self.inputs.addElement('myname', 'name_click', [88000, ypos[6]], [45000, 6000], self.fconst * 0.8, 'half-black', 'ioTextInput')
        self.passinp = self.inputs.addElement('mypass', 'pass_click', [88000, ypos[7]], [45000, 6000], self.fconst * 0.8, 'half-black', 'ioTextInput')  
        celBillboard(self.nameinp).text = Config.GetStr('Outlaws.Player.Name')
        celBillboard(self.passinp).text = ''
        self.inputs.activate('myname')
        
        pcinput = celCommandInput(self.entity)
        pcinput.Bind('esc', 'exit')
         
        lobbyname, self.lobbyserver = ioDataBin.Get('lobbyserver', True)
        gamename, self.gameserver = ioDataBin.Get('gameserver', True)
        
        self.net = ioNetHelper.ioNetHelper()
        netcl = Entities[ioDataBin.Get('socketent')]
        pars = parblock({'server' : cPickle.dumps(self.gameserver, 0)})
        netcl.Behaviour.SendMessage('setserver', None, pars)
        
        self.net.sendData('ioGSrv', 'getinfo', [self.entity.Name])       
        
    def pccommandinput_exit1(self, pc, args):
        q = CS_QUERY_REGISTRY (oreg, iEventQueue)
        if q:
            q.GetEventOutlet().Broadcast (csevQuit (oreg))
            
    def name_click(self, pc, args):
        self.inputs.activate('myname')
        
    def pass_click(self, pc, args):
        self.inputs.activate('mypass')

    def pccommandinput_exit_(self, pc, args):
        pass
    
    def pccommandinput_exit0(self, pc, args):
        pass
    
    def destruct(self, pc, args):
        self.buttons.clear()
        self.inputs.clear()
        self.entity.PropertyClassList.RemoveAll()
      
    #Small code saver for the function below
    def settxt(self, i, text):
        bb = celBillboard(self.inputs.elements[i]).Billboard
        bb.SetText(str(text))
        
    #The server sent us enough info to start the game
    def r_gameinfo(self, pc, args):
        self.buttons.elements[2].Behaviour.SendMessage('setactive', None, celGenericParameterBlock(0))
        addr, data = self.net.getNetData(args)
        self.gamedata = data
        self.settxt(0, data[0])
        self.settxt(1, data[1])
        self.settxt(2, data[2])
        self.settxt(3, '%s / %s' % (data[3], data[4]))
        self.settxt(4, data[5])
        self.settxt(5, data[6])
        self.settxt(6, data[7])
        
    def Back_click(self, pc, args):
        gamesel = CreateEntity('ioGameSelect', self.blpython, 'ioGameSelect')
        RemoveEntity(self.entity)
        
    def Garage_click(self, pc, args):
        #Now the garage knows where to return to if we click here
        ioDataBin.Store('lastmenu', (self.entity.Name, self.entity.Behaviour.Name), True)
        garage = CreateEntity('ioGarage', self.blpython, 'ioGarage')
        RemoveEntity(self.entity)
    
    #Join the game!
    def Launch_click(self, pc, args):
        #Now the server screen knows where to return to if we click here
        ioDataBin.Store('lastmenu', (self.entity.Name, self.entity.Behaviour.Name), True)
        self.inputs.deactivateAll()
        name = celBillboard(self.nameinp).text
        if not name:
            name = ''
        Config.SetStr('Outlaws.Player.Name', name)
        Config.Save()
        password = celBillboard(self.passinp).text
        if not password:
            password = ''
        pars = parblock({'password' : password})
        client = CreateEntity('ioCl', self.blpython, 'ioClient')
        client.Behaviour.SendMessage('setpassword', None, pars)
        RemoveEntity(self.entity)