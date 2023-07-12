from pycel import *
from ioServerBase import *
import cPickle
import sys
import os

import ioLoader
import ioDispatcher
import ioNetHelper

class ioGameServer(ioServerBase):
    api_version = 2
    
    def __init__(self, celEntity):
        ioServerBase.__init__(self, celEntity)
        if self.bindport(1828):
            #We need less sleeptime to keep ode synced better
            self.sleeptime = 0.015
            self.servertime = 0
            
            #Used for compatibility testing
            self.compatversion = Config.GetStr('Outlaws.Version.Compat')
            #Used just for informing the client
            self.versionname = Config.GetStr('Outlaws.Version.Name')
            
            self.chatent = 'ioNetMgrCl'
    
            print 'game server started'
            self.blpython = BehaviourLayers['blpython']
    
            #Are we still trying to get into the lobby?
            self.needauth = True
            
            #We don't know the lobby server yet
            self.server = (None, None)
            self.lobbyname = ''
            
            self.name = ''
            self.mapname = ''
            self.gametype = ''
            self.maxclients = 0
            self.maxscore = 0
            self.password = ''
            self.notes = ''
    
            self.ingame = False
            
            self.authed = False
            
            #Allow the host game screen to get in here.
            self.dispatcher.exceptions += ['init', 'natcl', 'natsend']
                
            #Read game server settings from the host game screen, and send our ready response
            data = sys.stdin.read()
            data = cPickle.loads(data)
            self.initServer(data)
        
    def fullTimer(self):
        ioServerBase.fullTimer(self)
        if self.needauth and self.server != (None, None):
            #TODO, password
            data = ['', self.name, self.entity.Name, False]
            self.net.sendData('ioLS', 'auth', data, self.server)
 
        if self.server != (None, None) and self.authed:
            self.net.sendData('ioLS', 'reg', [], self.server)
            self.servertime += 1
            if self.servertime >= 6:
                print 'Dead lobby server!'
        
   #Server response
    def r_resp(self, pc, args):
        self.servertime = 0

    #Send a packet to a client in order to get through NAT
    def r_natsend(self, pc, args):
        lserv, data = self.net.getNetData(args)
        client = data[0]
        for i in xrange(2):
            self.net.sendData('', '', [], client)
    
    #Recieved info from the game hosting screen
    def initServer(self, data):
        for i in xrange(len(data)):
            if data[i] == None:
                data[i] = ''
        self.name = data[0]
        self.mapname = data[1]
        self.gametype = data[2]
        self.maxclients = data[3]
        self.maxscore = data[4]
        self.password = data[5]
        self.notes = data[6]
        self.lobbyname = data[7]
        self.server = data[8]

        self.dispatcher.clients.append(self.server)
        #If we are a single player server, we only get None as our server
        if self.server != (None, None):
            self.needauth = True
        
        #Make the gametype server
        gameinfo = ioLoader.findSubfolderCfgString('gametypes', self.gametype)
        self.gamebehave = CreateEntity('ioGmTp', self.blpython, gameinfo['ServerBehaviour'])
        pars = parblock({'score' : self.maxscore})
        self.gamebehave.Behaviour.SendMessage('setmaxscore', None, pars)

        #Make the netgame manager
        self.netmgr = CreateEntity('ioNetMgr', self.blpython, 'ioNetGameServer')
        
        pars = parblock({'name' : self.mapname})
        self.netmgr.Behaviour.SendMessage('setmapname', None, pars)

        #Make the entity manager
        self.entmgr = CreateEntity('ioEntMgr', self.blpython, 'ioEntityManager')

    def r_aok(self, pc, args):
        print 'game server connected to lobby'
        self.authed = True
        self.needauth = False
        
    def r_den(self, pc, args):
        print 'gameserver denied!'
        self.authed = False
            
    def r_getinfo(self, pc, args):
        addr, data = self.net.getNetData(args)
        ent = data[0]
        sendinfo = [self.name, self.mapname, self.gametype, len(self.clients), self.maxclients, self.maxscore, self.password != '', self.notes, self.compatversion, self.versionname]
        self.net.sendData(ent, 'gameinfo', sendinfo, addr)

    #This needs to be protected
    def r_setgametype(self, pc, args):
        addr, data = self.net.getNetData(args)
        if addr[0] == '127.0.0.1':
            self.gametype = data[0]

    #This needs to be protected
    def r_setmapname(self, pc, args):
        addr, data = self.net.getNetData(args)
        if addr[0] == '127.0.0.1':
            self.mapname = data[0]
            pars = parblock({'name' : self.mapname})
            self.netmgr.Behaviour.SendMessage('setmapname', None, pars)

    #Tell entities a client added
    def clientadd(self, pc, args):
        for ent in [self.gamebehave, self.netmgr, self.entmgr]:
            ent.Behaviour.SendMessage('clientadd', None, args)

    #Tell entities that a client died
    def clientpop(self, pc, args):
        for ent in [self.gamebehave, self.netmgr, self.entmgr]:
            ent.Behaviour.SendMessage('clientpop', None, args)
            
    #A local client is polling for the server
    def r_poll(self, pc, args):
        addr, data = self.net.getNetData(args)
        ent = data[0]
        if addr[0] == '127.0.0.1':
            self.net.sendData(ent, 'pollreply', [], addr)