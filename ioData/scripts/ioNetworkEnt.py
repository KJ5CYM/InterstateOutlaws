from pycel import *
import cPickle

import ioNetHelper
from ioNetworkEntBase import *

#Make the server version of an entity
def makeEntity(codename, name):
        #Find out entity template
        template = EntityTemplates[codename + '-tpl']
        if template:
            entity = CreateEntity(template, name,celEntityTemplateParams())
            #The entity needs to know its codename for network use
            pars = parblock({'codename' : codename})
            entity.Behaviour.SendMessage('setcodename', None, pars)
            return entity
        else:
            print 'missing template for entity codename', codename
            return None
        
#Behaviour for a networked object. server version
class ioNetworkEnt (ioNetworkEntBase):
    api_version = 2
    
    def __init__(self, celEntity):
        ioNetworkEntBase.__init__(self, celEntity)
        entmgr = Entities['ioEntMgr']
        if entmgr:
            pars = parblock({'entity' : self.entity.Name})
            self.owneraddr = cPickle.loads(entmgr.Behaviour.SendMessage('getaddr', None, pars))
            
    #We send our state to the server to update it.
    def pctimer_wakeup(self, pc, args):
        self.ticks += 1
        #Send the quaternion more often as it tends to desync easier
        if self.ticks == 2:
            self.net.sendToClients(self.entity.Name, 'q', self.getQuat(), self.owneraddr, False)
        if self.ticks == 4:
            self.net.sendToClients(self.entity.Name, 'p', self.getPos(), self.owneraddr, False)
            self.ticks = 0
            
    #We need to check that the correct client sent the update
    def r_p(self, pc, args):
        addr, data = self.net.getNetData(args)
        if addr == self.owneraddr:
            ioNetworkEntBase.r_p(self, pc, args)
            
    #We need to check that the correct client sent the update
    def r_q(self, pc, args):
        addr, data = self.net.getNetData(args)
        if addr == self.owneraddr:
            ioNetworkEntBase.r_q(self, pc, args)