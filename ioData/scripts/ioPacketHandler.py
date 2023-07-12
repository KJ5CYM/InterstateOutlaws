from pycel import *
from socket import *
import cPickle
import select
import random
import time

import ioNetPacket

#This class inspects data to check if it is important and acts appropriately to
#ensure it arrives
#Also prevents packet duping of important packets
class ioPacketHandler:
    def __init__(self, dispatcher):
        self.i = random.randrange(0, 100)
        self.importantpackets = {}
        self.recievedpackets = []
        self.dispatcher = dispatcher

    #Remember packets which are flagged, and keep sending them until they get there
    def inspectOutgoing(self, packet):
        #If the packet is flagged as important, remember it, give it an id
        if packet.important:
            if not packet.packetid:
                packet.packetid = self.i
            self.importantpackets[packet.packetid] = packet
            self.i += 1
            if self.i == 100:
                self.i = 0

    #Send replies to ack messages to important packets that have arrived
    def inspectIncoming(self, packet):
        #Send replies as ack messages to important packets that have arrived
        if packet.important:
            #Check that its not a dupe packet
            #We go by entity and message of data as well id, as sockets tend to get reused, so different parts of the program may have same ip
            #And use the same id for totally different data
            found = False
            check = [packet.ip, packet.entity, packet.message, packet.packetid]
            for checkpacket in self.recievedpackets:
                dupe = False
                if check == checkpacket:
                    #print 'dupe packet ', check
                    found = True
                    #This forces processing to stop
                    packet.entity = None
                    break
            if not found:
                self.recievedpackets.append(check)
                if len(self.recievedpackets) > 32:
                    self.recievedpackets.pop(0)
            #Send back the response
            response = ioNetPacket.ioNetPacket()
            response.ackpacket = True
            response.packetid = packet.packetid
            response.ip = packet.ip
            self.dispatcher.sendData(response)
            
        #Remove acked packets from our memory
        if packet.ackpacket:
            if self.importantpackets.has_key(packet.packetid):
                del self.importantpackets[packet.packetid]

    #Check for packets that have not been replied within 500ms. If so, send them again
    def checkStored(self):
        curticks = Clock.GetCurrentTicks()
        for packetid, packet in self.importantpackets.items():
            timediff = curticks - packet.lastsend
            ctimediff = curticks - packet.creationtime
            if timediff >= 2000:
                packet.lastsend = curticks
                #print 'resending', packet.entity, packet.message, packet.ip
                self.dispatcher.sendData(packet, True)
            #Give up on packets > 10s old
            if ctimediff >= 10000:
                del self.importantpackets[packetid]