from pycel import *
import socket
import asyncore
import cPickle
import time

import ioDispatcher
import ioInit
import ioNetPacket
import ioNetHelper
import ioDataBin

class ioReportingClient:
    def __init__(self, addr, name, ent):
        self.addr = addr
        self.reporttime = 0
        self.name = name
        self.entity = ent
        
class ioServerBase:
    api_version = 2
    
    def __init__(self, celEntity):
        self.entity = celEntity
        ioInit.registerclasses()
        #A class list of clients
        self.clients = []
        #List of higher level servers connected to this one
        self.childservers = []
        #This server may be reporting to a higher one, eg game servers to the lobby
        self.server = (None, None)
        #The entity that we send chat messages to. This needs to be overridden in specific implementations.
        self.chatent = ''
        self.blpython = BehaviourLayers['blpython']

        self.timer = celTimer(self.entity)
        self.timer.WakeUpFrame(0)

        self.maxclients = Config.GetInt('Outlaws.Server.MaxClients', 0)
        self.maxservers = Config.GetInt('Outlaws.Server.MaxChildServers', 0)
        self.dispatcher = ioDispatcher.ioDispatcher()
        #The messages that anyone is allowed to send
        self.dispatcher.exceptions = ['getinfo', 'auth']
        
        #Every 10 secs we check for dead clients, and send a ping to all.
        self.timer.WakeUp(10000, True)

        self.password = ''
        #The time to delay in between frames to save cpu usage.
        self.sleeptime = 0.05
        
        #Wakeup the packethandler
        self.lastmajorwakeup = Clock.GetCurrentTicks()
        timer = celTimer(self.entity)
        timer.WakeUp(500, True)

        ioDataBin.Store('socketent', self.entity.Name) 
        
        #We test lag this way, by waiting for a timer event
        self.fakelag = False
        self.lagsend = []
        self.net = ioNetHelper.ioNetHelper()

    #Handle the network que. also sleep to reduce cpu usage
    def pctimer_wakeupframe(self, pc, args):
        asyncore.loop(0, True, asyncore.socket_map, 1)
        if self.fakelag:
            for data in self.lagsend[:]:
                packet, mtime = data
                if Clock.GetCurrentTicks() - mtime >= 200:
                    self.dispatcher.sendData(packet)
                    self.lagsend.remove(data)
        if self.sleeptime > 0.0:
            time.sleep(self.sleeptime)
        
    #A client or server is reporting in
    def r_reg(self, pc, args):
        addr, data = self.net.getNetData(args)
        for client in self.clients + self.childservers:
            if addr == client.addr:
                client.reporttime = 0

    #A client or server wants to join
    def r_auth(self, pc, args):
        addr, data = self.net.getNetData(args)
        password = data[0]
        name = data[1]
        entity = data[2]
        clienttype = data[3]
        clientok = True
        reason = ''        
        
        #Work out the details we will be working on
        lst = {}
        lst[True] = self.clients, self.maxclients, 'client'
        lst[False] = self.childservers, self.maxservers, 'server'
        connectedlist, maxconnected, typename = lst[clienttype]
        
        
        #First check that we don't already have the client (dupe request)
        #if so, we send them an ok anyway.
        clientin = False
        for client in connectedlist:
            if addr == client.addr:
                clientin = True
                client.reporttime = 0
                self.net.sendData(entity, 'aok', [], addr)
            
        if not clientin:
            #Checks to allow entry
            #Make sure it has a unique name
            for client in connectedlist:
                if client.name == name:
                    clientok = False
                    reason = 'Client with same name already exists'
            if len(connectedlist) >= maxconnected:
                clientok = False
                reason = 'Too many' + typename + 's'
            if password != self.password:
                clientok = False
                reason = 'Wrong password'
            #They pass the tests, send them an acknowledgement and add them
            if clientok:
                self.net.sendData(entity, 'aok', [], addr)
                print 'New ' + typename + ' -', addr, name
                client = ioReportingClient(addr, name, entity)
                connectedlist.append(client)
                self.net.updateClientAddrs()
                self.dispatcher.clients.append(addr)
                pars = parblock({typename : cPickle.dumps(addr), 'name' : name})
                self.entity.Behaviour.SendMessage(typename + 'add', None, pars)
            #Didn't pass. send them a denial
            else:
                print typename + 'denied -', addr, name
                self.net.sendData(entity, 'den', [reason], addr)

    #Check our packets
    def pctimer_wakeup(self, pc, args):
        self.dispatcher.packethandler.checkStored()
        curtime = Clock.GetCurrentTicks()
        if (curtime - self.lastmajorwakeup) >= 5000:
            self.fullTimer()
            self.lastmajorwakeup = curtime 
    
    #Every 5 secs send a echo to all clients and servers, and time for dead ones.
    def fullTimer(self):
        pars = {}
        for connected in self.clients + self.childservers:
            self.net.sendData(connected.entity, 'resp', [], connected.addr)
            connected.reporttime += 1
            if connected.reporttime >= 12:
                print 'dead connection -', connected.name, connected.addr
                self.dropaddr(connected.addr)
                
    def r_leave(self, pc, args):
        addr, data = self.net.getNetData(args)
        self.dropaddr(addr)    
    
    def dropaddr(self, addr):
        for client in self.clients[:]:
            if client.addr == addr:
                self.clients.remove(client)
                self.net.updateClientAddrs()
                self.dispatcher.clients.remove(addr)
                pars = parblock({'client' : cPickle.dumps(client.addr), 'name' : client.name})
                self.entity.Behaviour.SendMessage('clientpop', None, pars)
                return
        for server in self.childservers[:]:
            if server.addr == addr:
                self.childservers.remove(server)
                self.dispatcher.clients.remove(addr)
                pars = parblock({'server' : cPickle.dumps(server.addr), 'name' : server.name})
                self.entity.Behaviour.SendMessage('serverpop', None, pars)
    
    #An entity requested to send something to somewhere.
    def senddata(self, pc, args):
        entity = args[parid('entity')]
        message = args[parid('message')]
        data = cPickle.loads(args[parid('data')])
        destination = cPickle.loads(args[parid('destination')])
        important = args[parid('important')]
        if not destination:
            print 'warning - no destination for packet', entity, message, data
        packet = ioNetPacket.ioNetPacket()
        packet.create(entity, message, data, destination, important)
        if self.fakelag:
            self.lagsend.append((packet, Clock.GetCurrentTicks()))
        else:
            self.dispatcher.sendData(packet)

    #A child entity needs to add more network client messages
    def addexceptions(self, pc, args):
        exceptions = cPickle.loads(args[parid('exceptions')])
        for el in exceptions:
            if el not in self.exceptions:
                self.dispatcher.exceptions.append(el)

    def serveradd(self, pc, args):
        pass

    def serverpop(self, pc, args):
        pass

    def clientadd(self, pc, args):
        pass

    def clientpop(self, pc, args):
        pass
    
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
        
    #Return all clients names
    def r_getclientnames(self, pc, args):
        pars = {}
        requester, data = self.net.getNetData(args)
        entity = data[0]
        for client in self.clients:
            self.net.sendData(entity, 'addclient', [client.name], requester)
        
    #Return servers connected under this one.
    def r_getservers(self, pc, args):
        pars = {}
        requester, data = self.net.getNetData(args)
        entity = data[0]
        #Send the name, address and index of all lobby
        #But we have to be careful, if we are sending a local client to an external computer
        #Then we need to warn it to use our internet ip instead of local one
        #Similarly a client which is also hosting needs to know to use its internal ip
        sendservers = []
        if len(self.childservers) is 0:
            self.net.sendData(entity, 'noservers', [], requester)
        for i, server in enumerate(self.childservers):
            if server.addr[0] == '127.0.0.1':
                addr = ('serverip', server.addr[1])
            elif server.addr[0] == requester[0]:
                addr = ('127.0.0.1', server.addr[1])
            else:
                addr = server.addr
            name = server.name
            data = [name, addr]
            self.net.sendData(entity, 'addserver', data, requester)
            
    #someone sent a message. work out the name of the client that sent it from the addr      
    def r_msg(self, pc, args):
        addr, data = self.net.getNetData(args)
        msg = data[0]
        name = 'anonymous'
        for client in self.clients:
            if client.addr == addr:
                name = client.name
        self.net.sendToClients(self.chatent, 'msg', [name, msg])
        
    #Return the list of our clients
    def getclientaddrs(self, pc, args):
        return cPickle.dumps([client.addr for client in self.clients], 0)
    
    #Quit if sent by the local client
    def r_quit(self, pc, args):       
        addr, data = self.net.getNetData(args)
        if addr[0] == '127.0.0.1':
            self.killserver()
            
    #Exit server process
    def killserver(self):
        print 'Server quit!'
        q = CS_QUERY_REGISTRY (oreg, iEventQueue)
        if q:
            q.GetEventOutlet().Broadcast (csevQuit (oreg))
            
    #Attempt to bind the dispatcher to a port
    def bindport(self, port):
        try:
            self.dispatcher.bind(('', port))
            return True
        except:
            print "Couldn't bind to port %d. Maybe another server is already running?" % port
            self.killserver() 
            return False
