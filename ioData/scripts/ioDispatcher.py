from pycel import *
import asyncore
import socket

import ioPacketHandler
import ioNetPacket

#A dispatcher which reads from the socket and sends out messages to entities.
#Also writes to the socket
class ioDispatcher(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.buffers = []
        self.clients = []
        self.exceptions = []
        
        #The packethandler is responsible for making sure important packets reach their destination
        self.packethandler = ioPacketHandler.ioPacketHandler(self)

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        #Try to read at most 100 packets per frame
        for i in xrange(100):
            try:
                packet = ioNetPacket.ioNetPacket()
                netdata = self.recvfrom(1024)
                packet.fill(netdata)
                if packet.valid:
                    self.packethandler.inspectIncoming(packet)
                    if packet.entity:
                        if packet.ip in self.clients or packet.message in self.exceptions:
                            reciever = pl.FindEntity(packet.entity)
                            if reciever is not None:
                                reciever.Behaviour.SendMessage('r_%s' % packet.message, None, packet.toPars())
                            else:
                                #print 'no entity', packet.entity
                                pass
                        else:
                            pass
                            print 'discarded', packet.entity, packet.message, self.clients, packet.ip, packet.ip in self.clients, packet.message in self.exceptions
                else:
                    break
            except socket.error, why:
                #Error 10054 seems to happen on windows for no reason
                if (why[0] != asyncore.EWOULDBLOCK) and (why[0] != asyncore.ECONNRESET):
                    raise socket.error, why
                else:
                    break

    def writable(self):
        return (len(self.buffers) > 0)
    
    def readable(self):
        return True

    def handle_write(self):
        for packet in self.buffers:
            try:
                data = packet.construct()
                packetok = True
            except:
                packetok = False
                print 'couldnt create packet'
            if packetok:
                addr = packet.ip
                if isinstance(addr, list):
                    #We must convert back into a tuple, as json will have returned a list instead
                    addr = (addr[0], addr[1])
                try:
                    self.sendto(data, addr)
                except:
                    print 'bad data', data, addr
            self.buffers = []
        
    def sendData(self, packet, inspected = False):
        if not inspected and packet.entity:
            self.packethandler.inspectOutgoing(packet)
        self.buffers.append(packet)
