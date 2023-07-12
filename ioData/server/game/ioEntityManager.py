from pycel import *
import ioLoader
import random
import cPickle
import ioNetHelper
import ioNetworkEnt

#an entity which keeps track of the positions of managed entities,
#plus anything extra they need
class ioEntityManager:
    api_version = 2
    
    def __init__(self,celEntity):
        self.entity = celEntity
        print 'initialised entity manager'
        #Entities can store info here
        self.ents = {}
	self.gsrv = Entities['ioGSrv']
        
        self.net = ioNetHelper.ioNetHelper()

    #A client is registering an entity
    def r_newent(self, pc, args):
        addr, data = self.net.getNetData(args)
        print 'got newent server', addr, data
        name, codename = data
        if not self.ents.has_key(name):
            #The dictionary must already have an entry so the entity can know its owner addr
            self.ents[name] = [addr, codename]
            #Make the server side version of the vehicle. This will return None in sp mode, since the
            #templates aren't loaded.
            entity = ioNetworkEnt.makeEntity(codename, name)
    
            #Tell all other clients that a new entity has arrived.
            data = [name, codename]
            self.net.sendToClients('ioEntMgrCl', 'newent', data, addr)
            
            #Add the entity to the gametype
            gmtp = Entities['ioGmTp']
            #Let the gametype work out the positioning. This is only needed in mp.
            if entity:
                pars = parblock({'entity' : entity})
                gmtp.Behaviour.SendMessage('positionplayer', None , pars)
    
            pars = parblock({'name' : name})
            gmtp.Behaviour.SendMessage('addentity', None, pars)
        

    #Fill in  all other ents on the new machine
    def r_fillents(self, pc, args):
        addr = self.net.getNetData(args)[0]
        for ent, data in self.ents.iteritems():
            data = [ent, data[1]]
            self.net.sendData('ioEntMgrCl', 'newent', data, addr)
        
    def clientadd(self, pc, args):
        pass

    #A client was removed. We need to remove our own reference to it and tell all clients to remove it
    def clientpop(self, pc, args):
        client = cPickle.loads(args[getid('cel.parameter.client')])
        for entname, data in self.ents.items():
            if data[0] == client:
                #Tell all vehicles that this player is gone.
                pars = parblock({'name' : entname})
                for name in self.ents.keys():
                    e = Entities[name]
                    if e:
                        e.Behaviour.SendMessage('entremoved', None, pars)
                #Now we try to remove it ourselves
                ent = Entities[entname]
                if ent:
                    RemoveEntity(ent)
                self.net.sendToClients('ioEntMgrCl', 'delent', [entname])
                self.ents.pop(entname)
                    
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
                
    def getaddr(self, pc, args):
        ent = args[getid('cel.parameter.entity')]
        return cPickle.dumps(self.ents[ent][0])
    
    #Get the next entity from a current one in our entity dict, for a given entity. Used for targetting systems
    def getnextentity(self, pc, args):
        source = args[getid('cel.parameter.source')]
        current = args[getid('cel.parameter.current')]
        entities = self.ents.keys()
        if len(entities) > 1:
            try:
                idx = entities.index(current) + 1
            except:
                idx = 0
            if idx > len(entities) - 1:
                idx = 0
            #We don't want to target ourselves!
            if entities[idx] == source:
                idx += 1
                if idx > len(entities) - 1:
                    idx = 0
            return entities[idx]
        else:
            return ''