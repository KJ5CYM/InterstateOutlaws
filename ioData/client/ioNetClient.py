from pycel import *
import asyncore
import time
import cPickle
import socket

import ioDispatcher
import ioNetPacket
import ioNetHelper
import ioDataBin

#Is the transport entity to the server for clients.
class ioNetClient:
    api_version = 2
    def __init__(self, celEntity):
        self.dispatcher = ioDispatcher.ioDispatcher()
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']
        self.timer = celTimer(self.entity)
        self.timer.WakeUpFrame(0)
        self.timer.WakeUp(500, True)
        self.server = None
        ioDataBin.Store('socketent', self.entity.Name)
        self.dispatcher.exceptions = ['gameinfo', 'discover', 'dldata', 'dldone']
        
        #We test lag this way, by waiting for a timer event
        self.fakelag = False
        self.lagsend = []
        
        #Used for picking up lan games
        self.dispatcher.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20)
        self.dispatcher.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)
        
    #An entity requested to send something
    def senddata(self, pc, args):
        entity = args[parid('entity')]
        message = args[parid('message')]
        data = cPickle.loads(args[parid('data')])
        destination = cPickle.loads(args[parid('destination')])
        important = args[parid('important')]
        if destination is None:
            destination = self.server
        packet = ioNetPacket.ioNetPacket()
        packet.create(entity, message, data, destination, important)
        if self.fakelag:
            self.lagsend.append((packet, Clock.GetCurrentTicks()))
        else:
            self.dispatcher.sendData(packet)

    def pctimer_wakeupframe(self, pc, args):
        asyncore.loop(0, True, asyncore.socket_map, 1)
        if self.fakelag:
            for data in self.lagsend[:]:
                packet, mtime = data
                if Clock.GetCurrentTicks() - mtime >= 200:
                    self.dispatcher.sendData(packet)
                    self.lagsend.remove(data)

    def pctimer_wakeup(self, pc, args):
        self.dispatcher.packethandler.checkStored()

    #A child entity needs to add more network client messages
    def addexceptions(self, pc, args):
        exceptions = cPickle.loads(args[parid('exceptions')])
        for el in exceptions:
            if el not in self.dispatcher.exceptions:
                self.dispatcher.exceptions.append(el)
    
    def destruct(self, pc, args):
        self.dispatcher.close()
        
    def setserver(self, pc, args):
        self.server = cPickle.loads(args[parid('server')])
        if isinstance(self.server, list):
            server = (self.server[0], self.server[1])
        self.dispatcher.clients = [self.server]
        
    def addserver(self, pc, args):
        server = cPickle.loads(args[parid('server')])
        if isinstance(server, list):
            server = (server[0], server[1])
        self.dispatcher.clients.append(server)
