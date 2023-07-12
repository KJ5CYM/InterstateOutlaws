from pycel import *
import socket
import urllib2
import struct
from ioServerBase import *
import ioNetHelper
import ioDownloader


class ioLobbyServer(ioServerBase):
    api_version = 2
    def __init__(self, celEntity):
        ioServerBase.__init__(self, celEntity)
        if self.bindport(1827):
            self.masteraddress = Config.GetStr('Outlaws.MasterServer.Address')
            self.name = Config.GetStr('Outlaws.LobbyServer.Name')
            self.servertime = 0
            self.maxclients = 1024
            self.chatent = 'ioLobbyChat'
    
            socket.setdefaulttimeout(10)
            self.checkIn()
    
            self.dispatcher.exceptions += ['natcl', 'discover']
            print 'lobby server started!'
            
            #Used for multicast lan game finding
            intf = socket.gethostbyname(socket.gethostname())
            self.dispatcher.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(intf))
            #Not sure if this code works outside of localhost
            mreq = struct.pack('4sl', socket.inet_aton(ioNetHelper.multicastip), socket.INADDR_ANY)
            self.dispatcher.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            
            self.lastcheckin = Clock.GetCurrentTicks()
   
    def downloader_complete(self, pars):
        pass
    
    def downloader_error(self, pars):
        print 'error checking in to master server', pars
        
    def downloader_read(self, pars):
        pass
    
    #Refresh in the masterserver list
    def pctimer_wakeup(self, pc, args):
        ioServerBase.pctimer_wakeup(self, pc, args)
        curtime = Clock.GetCurrentTicks()
        if curtime - self.lastcheckin >= 3600000:
            self.lastcheckin = curtime
            self.checkIn()
            
    def pctimer_wakeupframe(self, pc, args):
        ioServerBase.pctimer_wakeupframe(self, pc, args)
        ioDownloader.dispatch(self, self.dl)
   
    def checkIn(self):
        serverstring = (self.masteraddress + 'write.php?lobby=' + self.name).replace(' ', '%20')
        self.dl = ioDownloader.ioDownloader(serverstring)
        self.dl.start()
   
    #Send a packet to a game server in order to punch-through NAT
    def r_natcl(self, pc, args):
        addr, data = self.net.getNetData(args)
        gsrv = data[0]
        self.net.sendData('ioGSrv', 'natsend', [addr], gsrv)
        
   #Server response
    def r_resp(self, pc, args):
        self.servertime = 0
        
    # A new chat client has joined, inform all existing clients.
    def clientadd(self, pc, args):
        name = args[parid('name')]
        self.net.sendToClients(self.chatent, 'addclient', [name])
        
    def r_discover(self, pc, args):
        addr, data = self.net.getNetData(args)
        self.net.sendData('ioServerSelect', 'discover', [self.name], addr)
