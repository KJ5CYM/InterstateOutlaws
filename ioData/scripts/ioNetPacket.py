from pycel import *

import cPickle

#We use simplejson to serialise our network data for security and efficiency.
import simplejson

#A packet which we send over the network
#Packets are created for:
#  - sending over the network. create and fill are used for this
#  - recieving from the network. Fill is used for this
#  - sending / recieving an ack packet
#  - sending / recieving to an entity

class ioNetPacket:
    def __init__(self):
        self.entity = None
        self.message = None
        self.data = None
        #ip can represent where we are going or where we came from
        self.ip = None
        self.important = True
        self.packetid = None
        self.ackpacket = False
        self.valid = True
        
    #create our packet to send
    def create(self, entity, message, data, ip, important = True):
        self.entity = entity
        self.message = message
        self.data = data
        #ip can represent where we are going or where we came fromW
        self.ip = ip
        self.important = important
        self.lastsend = Clock.GetCurrentTicks()
        self.creationtime = Clock.GetCurrentTicks()
        self.packetid = None
    
    #Return the binary interpretation of our data to be sent over the socket
    #similar to pickle's dumps ! is prepended to important packets, and @ to
    #responses to important packets
    def construct(self):
        if self.ackpacket:
            data = '@%s' % simplejson.dumps([self.packetid])
        else:
            if self.important:
                msg = [self.packetid, self.entity, self.message, self.data]
                data = '!%s' % simplejson.dumps(msg)
            else:
                msg = [self.entity, self.message, self.data]
                data = '-%s' % simplejson.dumps(msg)
        return data
        
    #Fill in our data from a binary string recieved over the socket
    #Return whether fill worked out ok. Either not enough data,
    #or we are an ack packet
    #similar to pickle's loads
    def fill(self, socketdata):
        data = socketdata[0]
        packettype = data[0]
        try:
            data = simplejson.loads(data[1:])
        except:
            #Rubbish / wrongly encoded data
            pass
        #Convert all strings in data from unicode to utf-8
        data = map(csencode, data)
        
        self.ip = socketdata[1]
        
        self.lastsend = Clock.GetCurrentTicks()
        self.creationtime = Clock.GetCurrentTicks()
        
        #An ack packet, flag as such and extract id
        if packettype == '@':
            self.ackpacket = True
            self.packetid = data[0]
            self.valid = True
            self.important = False
            return
        #An important packet, flag ourselves as such and extract our id.
        elif packettype == '!':
            self.important = True
            self.packetid = data.pop(0)
            self.valid = True
        elif packettype == '-':
            self.important = False
            self.ackpacket = False
            self.valid = True
        else:
            self.valid = False
            return
        
        if len(data) >= 3:
            self.entity, self.message, self.data = data[0:3]
            self.valid = True
        else:
            self.valid = False
        
    #Create a parblock to send to an entity
    def toPars(self):
        msg = {}
        msg['addr'] = cPickle.dumps(self.ip, 0)
        msg['data'] = cPickle.dumps(self.data, 0)
        return parblock(msg)
    
#Converts a string from unicode into utf-8 compatible with the cs c functions
def csencode(item):
    if isinstance(item, unicode):
        return item.encode('utf-8')
    #Apply ourself recursively into a list
    elif isinstance(item, list):
        return map(csencode, item)
    else:
        return item
    return encls