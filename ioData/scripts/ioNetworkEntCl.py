from pycel import *
import cPickle

import ioNetHelper
from ioNetworkEntBase import *

def makeEntity(codename, name):
        #Find out entity template
        template = EntityTemplates[codename + '-tpl']
        if template:
            originalname = template.Behaviour
            template.SetBehaviour('blpython', originalname + 'Cl')
            entity = CreateEntity(template, name, celEntityTemplateParams())
            template.SetBehaviour('blpython', originalname)
            #The entity needs to know its codename for network use
            pars = parblock({'codename' : codename})
            entity.Behaviour.SendMessage('setcodename', None, pars)
            return entity
        else:
            print 'missing template for entity codename', codename
            return None
        
#Behaviour for a networked object it sends its position to the server.
class ioNetworkEntCl (ioNetworkEntBase):
    api_version = 2
    
    def __init__(self, celEntity):
        ioNetworkEntBase.__init__(self, celEntity)

    #Register or unregister from the network.
    def setregistered(self, pc, args):
        self.registered = args[getid('cel.parameter.registered')]
        pars = {}
        if self.registered:
            self.net.sendData('ioEntMgr', 'newent', [self.entity.Name, self.codename])
        else:
            self.net.sendData('ioEntMgr', 'delent', [self.entity.Name])

    #Send input to the server. But make sure we don't flood the network
    def sendinput(self, inp):
        self.net.sendData(self.entity.Name, 'inp', [inp])
        
    #We send our state to the server to update it.
    def pctimer_wakeup(self, pc, args):
        if self.registered:
            self.ticks += 1
            #Send the quaternion more often as it tends to desync easier
            if self.ticks == 2:
                self.net.sendData(self.entity.Name, 'q', self.getQuat(), None, False)
            if self.ticks == 4:
                self.net.sendData(self.entity.Name, 'p', self.getPos(), None, False)
                self.ticks = 0