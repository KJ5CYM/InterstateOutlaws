from pycel import *

import ioDataBin
import cPickle
import ioLoader
import ioNetHelper

#client loads the map, and runs its own physics world.
class ioClient:
    api_version = 2
    def __init__(self, celEntity):
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']
        self.gamestarted = False
        self.idData = getid('cel.parameter.data')
        
        self.netclient = Entities['ioNetClient']
        self.net = ioNetHelper.ioNetHelper()
        
        self.playername = Config.GetStr('Outlaws.Player.Name')
        #The password will actually be set properly through setpassword message
        self.password = ''
        
        self.servertime = 0
        #Have we been allowed, or are we still waiting?
        self.authed = False
        self.denied = False
        self.needauth = False
        self.needinfo = False
        print 'client started'
        blpython = BehaviourLayers['blpython']

        #Create a general network game clientmanager
        self.netmgr = CreateEntity('ioNetMgrCl', self.blpython, 'ioNetGameClient')
        
        self.serverInit()
        
        #Wakeup the packethandler
        timer = celTimer(self.entity)
        timer.WakeUp(5000, True)

    def pctimer_wakeup(self, pc, args):
        # If we have joined the game, send a ping to the server
        if self.gameserver and self.authed:
            self.servertime += 1
            if self.servertime >= 3:
                hud = Entities['ioHUD']
                if hud:
                    hud.Behaviour.SendMessage('lag', None, celGenericParameterBlock(0))
            msg = 'reg'
            data = []
        #If we have not recieved a reply from the server, re-send an authentication request
        if self.needauth and self.gameserver:
            msg = 'auth'
            data = [self.password, self.playername, self.entity.Name, True]
        #If we still need game information, re-send a request
        if self.needinfo and self.gameserver:
            msg = 'getinfo'
            data = [self.entity.Name]

        if not self.denied:
            self.net.sendData('ioGSrv', msg, data, self.gameserver)
            
    def r_resp(self, pc, args):
        if self.servertime >= 2:
            hud = Entities['ioHUD']
            if hud:
                hud.Behaviour.SendMessage('unlag', None, celGenericParameterBlock(0))
        self.servertime = 0

    #Get the servers sending info to us
    def serverInit(self):
        self.lobbyname, self.lobbyserver = ioDataBin.Get('lobbyserver', True)
        self.gamename, self.gameserver = ioDataBin.Get('gameserver', True)                
        
        #Make the connecting screen
        self.serverscr = CreateEntity('ioServerScreen', self.blpython, 'ioServerScreen')
        pars = parblock({'text' : 'Connecting to Server...'})
        self.serverscr.Behaviour.SendMessage('setlabel', None, pars)

        #Tell the netclient to allow our gameserver. it also allows users of netclient to not
        #know the gameservers ip and get away with it
        self.gameserver = (self.gameserver[0], self.gameserver[1])
        pars = parblock({'server' : cPickle.dumps(self.gameserver, 0)})
        self.netclient.Behaviour.SendMessage('setserver', None, pars)
        
        #Now we keep sending requests to get game info.
        self.needinfo = True
        self.pctimer_wakeup(None, None)

    #Server send us info about the game. Now we authenticate
    def r_gameinfo(self, pc, args):
        addr, data = self.net.getNetData(args)
        self.mapname = data[1]
        self.gametype = data[2]

        pars = parblock({'data' : cPickle.dumps(data, 0)})
        self.serverscr.Behaviour.SendMessage('setgameinfo', None, pars)
        #Ask for joining
        self.needauth = True
        self.needinfo = False
        self.pctimer_wakeup(self.entity, args)

    def r_aok(self, pc, args):
        if not self.authed:
            self.authed = True
            self.needauth = False
            
            #We need to tell our thread to handle sending pings for a while
            #Otherwise the server may drop us while we are blocked loading
            data = ['ioGSrv', 'reg', self.playername, self.entity.Name]
            #self.netreader.timedSend(self.gameserver, data, False, 5)
    
            pars = parblock({'text' : 'Connected! Loading map.'})
            self.serverscr.Behaviour.SendMessage('setlabel', None, pars)
    
            #Tell the netmgr our map
            pars = parblock({'name' : self.mapname})
            self.netmgr.Behaviour.SendMessage('setmapname', None, pars)
            
            #Create the client game
            gameinfo = ioLoader.findSubfolderCfgString('gametypes', self.gametype)
            self.gametp = CreateEntity('ioGmTpCl', self.blpython, gameinfo['ClientBehaviour'])
    
            self.entmgr = CreateEntity('ioEntMgrCl', self.blpython, 'ioEntityManagerClient')

    #Non-blocking again, we can continue to handle pinging
    def maploaded(self, pc, args):
        pass
        #self.netreader.stopTimedSend()

    def r_den(self, pc, args):
        server, data = self.net.getNetData(args)
        reason = data[0]
        self.authed = False
        self.denied = True
        self.needauth = False
        pars = parblock({'text' : reason})
        self.serverscr.Behaviour.SendMessage('setlabel', None, pars)
        
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
        self.net.sendData('ioGSrv', 'leave', [], self.gameserver)
        
    def getlobbyserver(self, pc, args):
        return cPickle.dumps([self.lobbyname, self.lobbyserver], 0)
    
    def getgameserver(self, pc, args):
        return cPickle.dumps([self.gamename, self.gameserver], 0)

    #Change login name and password
    def setpassword(self, pc, args):
        self.password = args[parid('password')]