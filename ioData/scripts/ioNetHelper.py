from pycel import *
import cPickle
import simplejson
import ioDataBin

multicastip = '225.100.100.100'

#A helper class which makes it easy to send data over the network through
#an entity holding an ioDispatcher.
class ioNetHelper:
    def __init__(self):
        #The transport entity is the entity which holds our dispatcher.
        #We require that it is stored in the data bin
        self.transportent = pl.FindEntity(ioDataBin.Get('socketent'))
        self.clientaddrs = None
         
    #Sends a message to our transport to send data
    def sendData(self, entity, message, data, dest = None, important = True):
        msgblock = {}
        msgblock['entity'] = entity
        msgblock['message'] = message
        msgblock['data'] = cPickle.dumps(data, 0)
        msgblock['destination'] = cPickle.dumps(dest, 0)
        msgblock['important'] = important
        pars = parblock(msgblock)
        if not self.transportent:
            self.transportent = Entities[ioDataBin.Get('socketent')]
        self.transportent.Behaviour.SendMessage('senddata', None, pars)

    #Fetch and store the list of client addresses from the transport entity
    def updateClientAddrs(self):
        pars = celGenericParameterBlock(0)
        clients = self.transportent.Behaviour.SendMessage('getclientaddrs', None, pars)
        self.clientaddrs = cPickle.loads(clients)
        
    #for use by server entities, send a message to all clients, except for one optional one
    def sendToClients(self, entity, message, data, source = None, important = True):
        #if not self.clientaddrs:
        self.updateClientAddrs()
        for client in self.clientaddrs:
            if source != client:
                self.sendData(entity, message, data, client, important)
                
    #Return the data out of a parblock
    def getNetData(self, pars):
        ip = cPickle.loads(pars[parid('addr')])
        data = cPickle.loads(pars[parid('data')])
        return (ip, data)