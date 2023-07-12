from pycel import *
import cPickle
import os
import subprocess

import ioBaseInit
import ioDataBin
import ioLoader
import Menu
import ioScroller

#Screen with settings which launches a game server 'ioGameServer' process
class ioHostGame:
    api_version = 2
    
    def __init__(self,celEntity):
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']
        self.fconst = Menu.GetFontConstant()
        self.fcolor = Menu.GetFontColor()

        self.mapinfo = ioLoader.scanDir('maps')
        self.gameinfo = ioLoader.scanDir('gametypes')
        bg = celAddBillboard(self.entity).Billboard
        bg.SetMaterialName('hostjoin-bg')
        bg.SetPosition(0,0)
        bg.SetSize(307200,307200)
        
        frame = celAddBillboard(self.entity).Billboard
        frame.SetMaterialName('window-frame')
        frame.SetPosition(40000,40000)
        frame.SetSize(227200,227200)
        
        windowbg = celAddBillboard(self.entity).Billboard
        windowbg.SetMaterialName('host-window-bg')
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
        for i in xrange(5):
            ypos.append(pos)
            pos += spacing
        #How awesome am I! Store the positions in a dictionary.
        labels = []
        labels = {}
        labels['Notes'] = [150000, ypos[0]]
        labels['Game Name'] = [xpos, ypos[0]]
        labels['Location'] = [xpos, ypos[1]]
        labels['Game Type'] = [xpos, ypos[2]]
        labels['Max Plyrs'] = [xpos, ypos[3]]
        labels['Max Score'] = [90000, ypos[3]]
        labels['Password'] = [xpos, ypos[4]]
        
        for name, pos in labels.items():
            bb = celAddBillboard(self.entity).Billboard
            bb.SetTextFont('/outlaws/fonts/lcd2.ttf', self.fconst * 0.8)
            bb.SetText(name)
            bb.SetTextFgColor(self.fcolor)
            bb.SetPosition(pos[0], pos[1])
        
        self.buttons = Menu.ioMenu(self.entity)
        self.buttons.addElement('<<', 'Back_click', [42500, 42500], [6000, 6000], self.fconst * 0.7, 'back-bg')
        self.buttons.addElement('Launch', 'Launch_click', [244000, 186000], [19000, 8000], self.fconst, 'button-bg')
        
        self.inputs = Menu.ioMenu(self.entity)
        self.inputs.addElement('name', 'Input_click', [68000, 52000], [65000, 6000], self.fconst * 0.8, 'unselection', 'ioTextInput')
        
        #Add a location dropdown, and fill it in with maps in the 'ioData/maps' folder.
        location = self.inputs.addElement('location', 'Input_click', [68000, 60000], [65000, 6000], self.fconst * 0.8, 'unselection', 'ioDropDown')
        for dict in self.mapinfo:
            #Don't add the garage!
            if dict['Name'] != 'Garage':
                pars = parblock(dict)
                location.Behaviour.SendMessage('additem', None, pars)
        pars = parblock({'index' : 0})
        location.Behaviour.SendMessage('selectindex', None, pars)
        
        #Same for gametypes
        games = self.inputs.addElement('gametypes', 'Input_click', [68000, 68000], [65000, 6000], self.fconst * 0.8, 'unselection', 'ioDropDown')
        
        for dict in self.gameinfo:
            pars = parblock(dict)
            games.Behaviour.SendMessage('additem', None, pars)
        pars = parblock({'index' : 0})
        games.Behaviour.SendMessage('selectindex', None, pars)
        
        maxp = self.inputs.addElement('maxplayers', 'Input_click', [68000, 76000], [18000, 6000], self.fconst * 0.8, 'unselection', 'ioNumberInput')
        self.inputs.addElement('maxscore', 'Input_click', [114000, 76000], [18000, 6000], self.fconst * 0.8, 'unselection', 'ioNumberInput')
        self.inputs.addElement('password', 'Input_click', [68000, 84000], [65000, 6000], self.fconst * 0.8, 'unselection', 'ioTextInput')
        self.inputs.addElement('notes', 'Input_click', [150000, 60000], [100000, 8000], self.fconst * 0.8, 'button-bg', 'ioTextInput')
        self.inputs.activate('name')
        
        pars = parblock({'value' : 6})
        maxp.Behaviour.SendMessage('set_value', None, pars)
        
        pcinput = celCommandInput(self.entity)
        pcinput.Bind('esc', 'exit')
        
        #Check if we are going single-player or multiplayer
        self.mp = ioDataBin.Get('mpgame')
        if not self.mp:
            self.lobbyserver = (None, None)
            self.lobbyname = None
            ioDataBin.Store('lobbyserver', (self.lobbyname, self.lobbyserver), True)
        else:
            self.lobbyname, self.lobbyserver = ioDataBin.Get('lobbyserver', True)
        
    def pccommandinput_exit1(self, pc, args):
        q = CS_QUERY_REGISTRY (oreg, iEventQueue)
        if q:
            q.GetEventOutlet().Broadcast (csevQuit (oreg))

    def pccommandinput_exit_(self, pc, args):
        pass
    
    def pccommandinput_exit0(self, pc, args):
        pass
    
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
        self.buttons.clear()
        self.inputs.clear()
        
    def Input_click(self, pc, args):
        name = args[getid('cel.parameter.sender')]
        self.inputs.activate(name)
            
    def Back_click(self, pc, args):
        #Recreate the entity which called us. this depends on game mode
        if self.mp:
            returnname = 'ioGameSelect'
        else:
            returnname = 'ioMainMenu'
        returnent = CreateEntity(returnname, self.blpython, returnname)
        RemoveEntity(self.entity)
        
    def Garage_click(self, pc, args):
        garage = CreateEntity('ioGarage', self.blpython, 'ioGarage')
        pars = {}
        pars['name'] = self.entity.Name
        pars['behaviour'] = self.entity.Behaviour.Name
        garage.Behaviour.SendMessage('setreturn', None, parblock(pars))
        RemoveEntity(self.entity)
    
    #Run the server! Then send it the data in our widgets
    def Launch_click(self, pc, args):
        command = ioBaseInit.getCelstart()
        args = 'ioData/server/game/celstart.cfg'
        args = os.path.normpath(args)
        #pipe = os.popen(celstart + ' ' + args, 'w')
        #os.spawnl(os.P_NOWAIT, command, 'celstart', args)
        ps = subprocess.Popen([command, args], shell = False, stdin = subprocess.PIPE)

        pars = celGenericParameterBlock(0)
        self.inputs.deactivateAll()
        
        #Pull the data out of our billboard inputs
        name = celBillboard(self.inputs.elements[0]).Billboard.GetText()
        location = celBillboard(self.inputs.elements[1]).Billboard.GetText()
        gametype = celBillboard(self.inputs.elements[2]).Billboard.GetText()
        maxplayers = int(celBillboard(self.inputs.elements[3]).Billboard.GetText())
        maxscore = int(celBillboard(self.inputs.elements[4]).Billboard.GetText())
        password = celBillboard(self.inputs.elements[5]).Billboard.GetText()
        notes = celBillboard(self.inputs.elements[6]).Billboard.GetText()
        
        #Send our data through pipe to the server
        data = [name, location, gametype, maxplayers, maxscore, password, notes, self.lobbyname, self.lobbyserver]
        os.write(ps.stdin.fileno(), cPickle.dumps(data))
        os.close(ps.stdin.fileno())
        #if self.mp:
        #    self.Back_click(self.entity, pars)
        #else:
        #Jump straight into the game
        data = (name, ('127.0.0.1', 1828))
        ioDataBin.Store('gameserver', data, True)
        #Now the server screen knows where to return to if we click here
        ioDataBin.Store('lastmenu', (self.entity.Name, self.entity.Behaviour.Name), True)
        #check we don't have an old client still hanging around, first
        client = pl.FindEntity('ioCl')
        if client:
            RemoveEntity(client)
        client = CreateEntity('ioCl', self.blpython, 'ioClient')
        #The client will ignore the blank name
        if not password:
            password = ''
        pars = parblock({'password' : password})
        client.Behaviour.SendMessage('setpassword', None, pars)
        RemoveEntity(self.entity)