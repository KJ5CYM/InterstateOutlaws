from pycel import *
import cPickle
from ioNetworkEnt import *
from ioVehicleBase import *
import ioLoader
import random

#Behaviour for a client-side prediction vehicle. It inherits of ioNetworkEnt,
#which sends position and input to the server.
class ioVehicle (ioNetworkEnt, ioVehicleBase):
    api_version = 2
    def __init__(self, celEntity):
        self.entity = celEntity
        ioNetworkEnt.__init__(self, self.entity)
        ioVehicleBase.__init__(self, self.entity)
        
        #We batch send damage messages to send bandwidth
        #self.damages is our buffer. its keys are tuples of zones and indexes
        #This ensures each type of damage will only be sent once.
        #eg (fr, 2) = 40.2
        #All items are sent and cleared every timer tick
        self.damages = {}
        
    def makeShadow(self):
        pass
    
    def makeSmoke(self):
        pass
        
    #A client broadcasts its input over the network
    def r_inp(self, pc, args):
        addr, data = self.net.getNetData(args)
        inp = data[0]
        if addr == self.owneraddr:
            inpstring = self.inpmap[inp]
            inpmethod = getattr(self, 'pccommandinput_' + inpstring)
            inpmethod(self.entity, celGenericParameterBlock(0))
            self.net.sendToClients(self.entity.Name, 'inp', [inp], addr)
        
    def pctimer_wakeup(self, pc, args):
        ioNetworkEnt.pctimer_wakeup(self, pc, args)
        ioVehicleBase.pctimer_wakeup(self, pc, args)
    
    def setcodename(self, pc, args):
        ioNetworkEnt.setcodename(self, pc, args)
        ioVehicleBase.setcodename(self, pc, args)
        self.net.sendData(self.entity.Name, 'nweps', [], self.owneraddr)
            
    #Weapon info sent from the client
    def r_weps(self, pc, args):
        addr, data = self.net.getNetData(args)
        if addr == self.owneraddr:
            for i, weapon in enumerate(data):
                pars = parblock({'mount' : self.mounts[i], 'weapon' : weapon})
                self.addweapon(self.entity, pars)
            self.net.sendToClients(self.entity.Name, 'weps', data, addr)
            #We shall now pick the first link group
            self.entity.Behaviour.SendMessage('pccommandinput_link1', None, args)
            self.net.sendToClients(self.entity.Name, 'setlnk', self.currentgroup)        
        
    #Clients call these functions when they are created,
    #because they need to know what has changed from the default.
    
    #A client needs to know about our weapon setup
    def r_nweps(self, pc, args):
        addr = self.net.getNetData(args)[0]
        data = []
        for mount in self.mounts:
            weapon = self.weapons[mount]
            codename = ''
            if weapon:
                codename = weapon.Behaviour.SendMessage('getcodename', None, args)
            data.append(codename)
        self.net.sendData(self.entity.Name, 'weps', data, addr)
        
    #A client needs to know about our existing damage state
    def r_ndmgst(self, pc, args):
        addr = self.net.getNetData(args)[0]
        data = [self.health]
        for health in self.frame + self.armour:
            data += round(health, 2)
        data += [x.round(2) for x in [self.powertrain, self.brakes, self.avgframe]]
        self.net.sendData(self.entity.Name, 'dmgst', data, addr)
        
        #We send damage of weapons and wheels in a seperate packet
        armours = []
        for ent in self.weapons.values() + self.wheelents:
            armour = 0
            if ent:
                armour = ent.Behaviour.SendMessage('getarmour', None, celGenericParameterBlock(0))
            armours.append(armour)
        self.net.sendData(self.entity.Name, 'subdmg', armours, addr)
        
    #Client needs to know our link setup
    def r_nlnk(self, pc, args):
        addr = self.net.getNetData(args)[0]
        self.net.sendData(self.entity.Name, 'setlnk', self.currentgroup, addr)    
        
    #Client needs to know our target setup
    def r_ntgt(self, pc, args):
        addr = self.net.getNetData(args)[0]
        self.net.sendData(self.entity.Name, 'settgt', [self.targetname], addr)
        
    #The server picks out a new target and updates the clients
    def r_nxtgt(self, pc, args):
        addr = self.net.getNetData(args)[0]
        if addr == self.owneraddr:
            pars = parblock({'source' : self.entity.Name, 'current' : self.targetname})
            entmgr = Entities['ioEntMgr']
            targetname = entmgr.Behaviour.SendMessage('getnextentity', None, pars)
            if targetname != '':
                self.targetname = targetname
                self.targetUpdate()
                self.net.sendToClients(self.entity.Name, 'settgt', [self.targetname])
    
    #Set a new link group
    def r_nxlnk(self, pc, args):
        addr = self.net.getNetData(args)[0]
        if addr == self.owneraddr:
            self.pccommandinput_link1(self.entity, args)
            self.net.sendToClients(self.entity.Name, 'setlnk', self.currentgroup)
        
    #Told by player client that we must remove a link
    def r_rmlink(self, pc, args):
        addr, data = self.net.getNetData(args)
        hardpoint = data[0]
        if addr == self.owneraddr:
            self.removeLink(hardpoint)
            self.net.sendToClients(self.entity.Name, 'setlnk', self.currentgroup)
            
    #Told by player client that we must remove a link
    def r_addlink(self, pc, args):
        addr, hardpoint = cPickle.loads(args[self.idData])
        if addr == self.owneraddr:
            self.addLink(hardpoint)
            self.net.sendToClients(self.entity.Name, 'setlnk', self.currentgroup)
    
    #Don't need none of those fancy effects here
    def doDeform(self, pos, depth, normal):
        pass
    
    def damageDeform(self, pos, damage):
        pass
    
    def makeWindows(self):
        pass
    
    def makeExhaust(self):
        pass
    
    def changeBodyMesh(self, dmgfname, reparent):
        pass
    
    def dieEffects(self):
        pass
    
    def makeDustTrails(self):
        pass
    
    def pctimer_wakeupframe(self, pc, args):
        ioNetworkEnt.pctimer_wakeupframe(self, pc, args)
    
    def pctimer_wakeup(self, pc, args):
        ioNetworkEnt.pctimer_wakeup(self, pc, args)
        ioVehicleBase.pctimer_wakeup(self, pc, args)
        #Send our batch of damage messages
        for type, damage in self.damages.iteritems():
            zone, idx = type
            data = [idx, damage]
            self.net.sendToClients(self.entity.Name, '%s_dmg' % zone, data)
        self.damages = {}
            
    def pcwheeled_collision(self, pc, args):
        pass
    
    #Send our new damage data to clients
    #To save bandwidth, we batch it all up, and send it at once every 500ms
    def postProcessDamage(self, zone, idx, health, source):
        ioVehicleBase.postProcessDamage(self, zone, idx, health, source)
        self.damages[(zone, idx)] = round(health, 2)
    
    def checkWindows(self, idx):
        pass
        
    def die(self, source):
        ioVehicleBase.die(self, source)
        #Tell the clients to die
        self.net.sendToClients(self.entity.Name, 'die', [source])
        gametype = Entities['ioGmTp']
        pars = parblock({'killedby' : source, 'killed' : self.entity.Name})
        gametype.Behaviour.SendMessage('playerkilled', None, pars)
    
    #Also tell client to respawn
    def respawn(self, pc, args):
        ioVehicleBase.respawn(self, pc, args)
        self.net.sendToClients(self.entity.Name, 'rspn', [])
