from pycel import *
import cPickle
import urllib2
import socket

import ioNetHelper
import ioDownloader
import Menu
import ioScroller
import ioDataBin

class ioServerSelect:
    api_version = 2
    
    #The server selection screen. Tries to download a list of games from the masterserver,
    #and multicast onto the lan
    def __init__(self,celEntity):
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']
        self.fconst = Menu.GetFontConstant()
        self.fcolor = Menu.GetFontColor()
        
        self.net = ioNetHelper.ioNetHelper()

        bg = celAddBillboard(self.entity).Billboard
        bg.SetMaterialName('server-bg')
        bg.SetPosition(0,0)
        bg.SetSize(307200,307200)
        
        frame = celAddBillboard(self.entity).Billboard
        frame.SetMaterialName('window-frame')
        frame.SetPosition(40000,40000)
        frame.SetSize(227200,227200)
        
        windowbg = celAddBillboard(self.entity).Billboard
        windowbg.SetMaterialName('servers-window-bg')
        windowbg.SetPosition(42500,50000)
        windowbg.SetSize(221200,212200)
        
        servers = celAddBillboard(self.entity).Billboard
        servers.SetTextFont('/outlaws/fonts/lcd2.ttf', self.fconst * 1.25)
        servers.SetText('Servers')
        servers.SetTextFgColor(self.fcolor)
        servers.SetPosition(240000, 42000)
        
        namebb = celAddBillboard(self.entity).Billboard
        namebb.SetTextFont('/outlaws/fonts/lcd2.ttf', self.fconst)
        namebb.SetText('Name')
        namebb.SetTextFgColor(self.fcolor)
        namebb.SetPosition(45000, 52000)
        
        self.menu = Menu.ioMenu(self.entity)
        self.menu.addElement('<<', 'Back_click', [42500, 42500], [6000, 6000], self.fconst * 0.7, 'back-bg')
        connect = self.menu.addElement('Connect', 'Connect_click', [45000, 252500], [22000, 8000], self.fconst, 'button-bg')
        connect.Behaviour.SendMessage('setinactive', None, celGenericParameterBlock(0))
        self.menu.addElement('Refresh', 'Refresh_click', [240000, 252500], [22000, 8000], self.fconst, 'button-bg')
        self.menu.addElement('LAN Games', 'LAN_click', [200000, 252500], [26000, 8000], self.fconst, 'button-bg')
            
        self.scroller = ioScroller.ioScroller(self.entity, [42500, 62500], [221200, 185000])

        self.masteraddress = Config.GetStr('Outlaws.MasterServer.Address')
        
        pcinput = celCommandInput(self.entity)
        pcinput.Bind('esc', 'exit')

        self.servers = []
        self.servernames = []
        
        self.timer = celTimer(self.entity)
        self.timer.WakeUpFrame(True)
        
        self.myip = None
        
        self.dl = None
                
        #We want to refresh on creation
        self.Refresh_click(None, celGenericParameterBlock(0))
        
    def pccommandinput_exit1(self, pc, args):
        q = CS_QUERY_REGISTRY (oreg, iEventQueue)
        if q:
            q.GetEventOutlet().Broadcast (csevQuit (oreg))

    def pccommandinput_exit_(self, pc, args):
        pass
    
    def pccommandinput_exit0(self, pc, args):
        pass
    
    def pctimer_wakeup(self, pc, args):
        self.entity.Behaviour.SendMessage('Refresh_click', None, celGenericParameterBlock(0))
        
    def pctimer_wakeupframe(self, pc, args):
        ioDownloader.dispatch(self, self.dl)
    
    def downloader_read(self, pars):
        pass
    
    def downloader_complete(self, pars):
        if self.dl.url.endswith('ipcheck.php'):
            self.myip = self.dl.data.strip()
            self.dl = ioDownloader.ioDownloader(self.masteraddress + '/servers.txt')
            self.dl.start()
        elif self.dl.url.endswith('servers.txt'):
            self.servernames = []
            self.scroller.clear()
            serverdat = self.dl.data
            for line in serverdat.strip().split('\n'):
                name, ip, time = line.split(',')
                self.addserver(name, ip.strip(), time)
                
    #Ask for the list of servers from the lobby again
    def Refresh_click(self, pc, args):
        self.servers = []
        self.servernames = []
        self.scroller.clear()
        self.scroller.additem('Downloading list of servers from master server', '')
        #We refresh every minute
        self.timer.WakeUp(60000, True)
        self.menu.elements[1].Behaviour.SendMessage('setinactive', None, celGenericParameterBlock(0))

        #We are going to need this. if our ip is the same as what the master server reports as lobby, we shall map to 127.0.0.1
        serverok = False
        self.dl = ioDownloader.ioDownloader(self.masteraddress + '/ipcheck.php')
        self.dl.start()
                
    #We picked up a lobby server over the lan
    def r_discover(self, pc, args):
        addr, data = self.net.getNetData(args)
        print 'found server!'
        servername = data[0]
        if len(self.scroller.items) is 1 and len(self.servers) is 0:
            self.scroller.clear()
        self.addserver(servername, addr[0], 0)
     
    #Add a server to our list, and track it
    def addserver(self, servername, ip, time):
        if self.myip == ip:
            realserver = ('127.0.0.1', 1827)
        else:
            realserver = (ip, 1827)
        try:
            name = socket.gethostbyaddr(realserver[0])[0]
        except:
            name = 'Unable to get hostname'
        self.scroller.additem('%s (%s)' % (servername, name), 'scroller_select')
        if realserver not in self.servers:
            self.servers.append(realserver)
            self.servernames.append(servername)
        
        #If this is the first after refresh, select it.
        if len(self.servers) == 1:
            self.scroller.selectindex(0)
            self.menu.elements[1].Behaviour.SendMessage('setactive', None, celGenericParameterBlock(0))

    #The user clicked on one of our items
    def scroller_select(self, pc, args):
        name = args[getid('cel.parameter.sender')]
        self.scroller.selectname(name)
        print self.servers, self.scroller.selectedindex
        
    def scroller_up(self, pc, args):
        self.scroller.scrollup()
        
    def scroller_down(self, pc, args):
        self.scroller.scrolldown()

    #Create the game select, which will pick up on our selected server
    def Connect_click(self, pc, args):
        server = self.servers[self.scroller.selectedindex]
        name = self.servernames[self.scroller.selectedindex]
        
        #Write out the selected settings
        ioDataBin.Store('lobbyserver', (name, server), True)
        print name, server
        gamesel = CreateEntity('ioGameSelect', self.blpython, 'ioGameSelect')
        self.entity.PropertyClassList.RemoveAll()
        RemoveEntity(self.entity)
        
    def destruct(self, pc, args):
        self.scroller.destruct()
        self.menu.clear()
        self.entity.PropertyClassList.RemoveAll()
            
    def Back_click(self, pc, args):
        CreateEntity('ioMainMenu', self.blpython, 'ioMainMenu')
        RemoveEntity(self.entity)
        
    #Multicast pickup of lobby servers
    def LAN_click(self, pc, args):
        self.net.sendData('ioLS', 'discover', [], (ioNetHelper.multicastip, 1827))
        self.scroller.clear()
        self.scroller.additem('Searching for LAN lobbies', '')
        self.servernames = []
        self.servers = []