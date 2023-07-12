from pycel import *
import cPickle
import Menu

import ioScroller
import ioDataBin
import ioNetHelper

class ioGameSelect:
    api_version = 2
    #The server selection screen
    def __init__(self,celEntity):
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']
        self.fconst = Menu.GetFontConstant()
        self.fcolor = Menu.GetFontColor()
        self.playername = Config.GetStr('Outlaws.Player.Name')
        self.chatent = 'ioGameChat'
        
        #Used for compatibility testing
        self.compatversion = Config.GetStr('Outlaws.Version.Compat')
        #Used just for informing the client
        self.versionname = Config.GetStr('Outlaws.Version.Name')

        bg = celAddBillboard(self.entity).Billboard
        bg.SetMaterialName('game-bg')
        bg.SetPosition(0,0)
        bg.SetSize(307200,307200)
        
        frame = celAddBillboard(self.entity).Billboard
        frame.SetMaterialName('window-frame')
        frame.SetPosition(40000,40000)
        frame.SetSize(227200,227200)
        
        windowbg = celAddBillboard(self.entity).Billboard
        windowbg.SetMaterialName('games-window-bg')
        windowbg.SetPosition(42500,50000)
        windowbg.SetSize(221200,212200)
        
        games = celAddBillboard(self.entity).Billboard
        games.SetTextFont('/outlaws/fonts/lcd2.ttf', self.fconst * 1.25)
        games.SetText('Games')
        games.SetTextFgColor(self.fcolor)
        games.SetPosition(245000, 42000)

        insession = celAddBillboard(self.entity).Billboard
        insession.SetTextFont('/outlaws/fonts/lcd2.ttf', self.fconst)
        insession.SetText('Games in Session')
        insession.SetTextFgColor(self.fcolor)
        insession.SetPosition(45000, 52000)
        
        details = celAddBillboard(self.entity).Billboard
        details.SetTextFont('/outlaws/fonts/lcd2.ttf', self.fconst)
        details.SetText('Details')
        details.SetTextFgColor(self.fcolor)
        details.SetPosition(184000, 52000)

        self.menu = Menu.ioMenu(self.entity)
        self.menu.addElement('<<', 'Back_click', [42500, 42500], [6000, 6000], self.fconst * 0.7, 'back-bg')
        self.hostbutton = self.menu.addElement('Host', 'Host_click', [44000, 187000], [16000, 8000], self.fconst, 'button-bg')
        self.hostbutton.Behaviour.SendMessage('setinactive', None, celGenericParameterBlock(0))
        self.joinbutton = self.menu.addElement('Join', 'Join_click', [61000, 187000], [16000, 8000], self.fconst, 'button-bg')
        self.joinbutton.Behaviour.SendMessage('setinactive', None, celGenericParameterBlock(0))
        self.menu.addElement('Garage', 'Garage_click', [137000, 187000], [20000, 8000], self.fconst, 'button-bg')
        self.menu.addElement('Refresh', 'Refresh_click', [158000, 187000], [22000, 8000], self.fconst, 'button-bg')

        self.scroller = ioScroller.ioScroller(self.entity, [42500, 61000], [132000, 125000])
        
        #This one gets filled in when the game info comes
        self.labels = Menu.ioMenu(self.entity)
        
        pcinput = celCommandInput(self.entity)
        pcinput.Bind('esc', 'exit')
        
        lobbyname, self.lobbyserver = ioDataBin.Get('lobbyserver', True)
        self.servers = []
        self.servernames = []
        
        self.net = ioNetHelper.ioNetHelper()
        
        netcl = Entities[ioDataBin.Get('socketent')]
        pars = parblock({'server' : cPickle.dumps(self.lobbyserver, 0)})
        netcl.Behaviour.SendMessage('setserver', None, pars)
        
        #Used to autorefresh
        self.timer = celTimer(self.entity)
        self.timer.WakeUp(5000, True)
        #Wakeups since we last refreshed
        self.lastrefresh = 0

        #Join the lobby
        data = ['', self.playername, self.entity.Name, True]
        self.net.sendData('ioLS', 'auth', data, self.lobbyserver)
        self.scroller.additem('Joining lobby...', '')
        self.authed = False
        
        self.chatcl = CreateEntity('ioLobbyChat', self.blpython, 'ioLobbyChat')
        
    def pccommandinput_exit1(self, pc, args):
        q = CS_QUERY_REGISTRY (oreg, iEventQueue)
        if q:
            q.GetEventOutlet().Broadcast (csevQuit (oreg))

    def pccommandinput_exit_(self, pc, args):
        pass
    
    def pccommandinput_exit0(self, pc, args):
        pass
    
    #We are now in the lobby
    def r_aok(self, pc, args):
        pars = celGenericParameterBlock(0)
        self.Refresh_click(self.entity, pars)
        self.chatcl.Behaviour.SendMessage('joined', None, pars)
        self.authed = True
        
    def r_den(self, pc, args):
        self.scroller.clear()
        self.scroller.additem("Couldn't enter lobby", '')
        
    #No games on this lobby. what a shame.
    def r_noservers(self, pc, items):
        self.scroller.clear()
        self.scroller.additem('No Games on this lobby', '')
        self.hostbutton.Behaviour.SendMessage('setactive', None, celGenericParameterBlock(0))
        
    def r_addserver(self, pc, args):
        #Is this our first server?
        if len(self.scroller.items) is 1:
            self.scroller.clear()
            pars = celGenericParameterBlock(0)
            self.hostbutton.Behaviour.SendMessage('setactive', None, pars)
        serveraddr, data = self.net.getNetData(args)
        #Convert back into a tuple, as json converted it into a list
        serveraddr = (serveraddr[0], serveraddr[1])
        servername = data[0]
        server = data[1]
        #The client is on the same network as server, so we use it's ip, with the given port
        if server[0] == 'serverip':
            realserver = (serveraddr[0], server[1])
        else:
            realserver = server

        try:
            name = socket.gethostbyaddr(realserver[0])[0]
        except:
            name = 'Unable to get hostname'

        self.scroller.additem(servername + ' (' + name + ')', 'scroller_select')
        self.servernames.append(name)
        self.servers.append(realserver)
        
        #If this is the first after refresh, select it.
        if len(self.servers) is 1:
            self.scroller.selectindex(0)
            self.updateDetails()
   
    def scroller_select(self, pc, args):
        name = args[getid('cel.parameter.sender')]
        self.scroller.selectname(name)
        self.updateDetails()
    
    #Update the details coloumn with info of selected game 
    def updateDetails(self):
        gamesrv = self.servers[self.scroller.selectedindex]
        #Punch through NAT if gameserver is elsewhere
        self.net.sendData('ioLS', 'natcl', [gamesrv], self.lobbyserver)
        for i in xrange(2):
            self.net.sendData('', '', [], gamesrv)
        self.net.sendData('ioGSrv', 'getinfo', [self.entity.Name], gamesrv)
      
    #The server sent us enough info to start the game
    def r_gameinfo(self, pc, args):
        addr, data = self.net.getNetData(args)
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
        if compatversion == self.compatversion:
            compatibility = '(Compatibile)'
            self.joinbutton.Behaviour.SendMessage('setactive', None, celGenericParameterBlock(0))
        else:
            compatibility = '(Incompatibile)'
            self.joinbutton.Behaviour.SendMessage('setinactive', None, celGenericParameterBlock(0))
        self.labels.addElement('Version: %s %s' % (versionname, compatibility), '', [0, 0], [0, 0], self.fconst, '')
        self.labels.align([184000, 62000], [0, 8000])
        
        
    def pctimer_wakeup(self, pc, args):
        #auto-refresh every minute
        self.lastrefresh += 1
        if self.lastrefresh >= 12:
            self.entity.Behaviour.SendMessage('Refresh_click', None, celGenericParameterBlock(0))
            self.lastrefresh = 0
        #Send a ping to the lobby server
        if self.authed:
            self.net.sendData('ioLS', 'reg', [], self.lobbyserver)
        
    def Refresh_click(self, pc, args):
        self.servers = []
        self.servernames = []
        pars = celGenericParameterBlock(0)
        self.hostbutton.Behaviour.SendMessage('setinactive', None, pars)
        self.joinbutton.Behaviour.SendMessage('setinactive', None, pars)
        self.scroller.clear()
        self.scroller.additem('Getting list of game servers...', '')
        if self.lobbyserver:
            self.net.sendData('ioLS', 'getservers', [self.entity.Name], self.lobbyserver)
    
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
        self.scroller.destruct()
        self.menu.clear()
        self.labels.clear()
        RemoveEntity(self.chatcl)
        self.net.sendData('ioLS', 'leave', [], self.lobbyserver)
            
    def Back_click(self, pc, args):
        CreateEntity('ioServerSelect', self.blpython, 'ioServerSelect')
        RemoveEntity(self.entity)
        
    def Garage_click(self, pc, args):
        #Now the garage knows where to return to if we click here
        ioDataBin.Store('lastmenu', (self.entity.Name, self.entity.Behaviour.Name), True)
        garage = CreateEntity('ioGarage', self.blpython, 'ioGarage')
        RemoveEntity(self.entity)
        
    def Host_click(self, pc, args):
        #Now the hostgame knows where to return to if we click here
        ioDataBin.Store('lastmenu', (self.entity.Name, self.entity.Behaviour.Name), True)
        hg = CreateEntity('ioHostGame', self.blpython, 'ioHostGame')
        RemoveEntity(self.entity)
        
    def Join_click(self, pc, args):
        server = self.servers[self.scroller.selectedindex]
        name = self.servernames[self.scroller.selectedindex]
        ioDataBin.Store('gameserver', (name, server), True)
        jg = CreateEntity('ioJoinGame', self.blpython, 'ioJoinGame')
        RemoveEntity(self.entity)