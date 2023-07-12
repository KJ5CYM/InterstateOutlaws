from pycel import *
import cPickle
from ioNetworkEntCl import *
from ioVehicleBase import *
import ioLoader
import random

#Behaviour for a client-side prediction vehicle. It inherits of ioNetworkEnt,
#which sends position and input to the server.
class ioVehicleCl (ioNetworkEntCl, ioVehicleBase):
    api_version = 2
    
    def __init__(self, celEntity):
        self.entity = celEntity
        ioNetworkEntCl.__init__(self, self.entity)
        ioVehicleBase.__init__(self, self.entity)
        
        #We store weapon damage sent from the server if recieved before our actual weapons
        self.damagedata = None
        self.hud = Entities['ioHUD']
        
        #Controls our movement if we are a bot
        self.botcontroller = None
        
        #Usually the car starts off with wheels stuck in the ground. When this hits 10 (1 sec) we reset.
        self.resetticks = 0
    
    def destruct(self, pc, args):
        ioNetworkEntCl.destruct(self, pc, args)
        if self.botcontroller:
            RemoveEntity(self.botcontroller)
        ioVehicleBase.destruct(self, pc, args)

    def setplayer(self, pc, args):
        self.player = args[parid('player')]
        if self.player:
            self.camera =  celDefaultCamera(Entities['ioGameWorld'])
            self.pcinput = celCommandInput(self.entity)
            self.pcinput.Bind (Config.GetStr('Outlaws.Vehicle.Accelerate', 'up'), 'accelerate')
            self.pcinput.Bind (Config.GetStr('Outlaws.Vehicle.Brake', 'down'), 'brake')
            self.pcinput.Bind (Config.GetStr('Outlaws.Vehicle.SteerLeft', 'left'), 'steerleft')
            self.pcinput.Bind (Config.GetStr('Outlaws.Vehicle.SteerRight', 'right'), 'steerright')
            self.pcinput.Bind (Config.GetStr('Outlaws.Vehicle.Handbrake','space'), 'handbrake')
            self.pcinput.Bind (Config.GetStr('Outlaws.Vehicle.Reset','r'), 'recover')
            self.pcinput.Bind (Config.GetStr('Outlaws.Vehicle.Cammode','c'), 'cammode')
            self.pcinput.Bind (Config.GetStr('Outlaws.Vehicle.Target','t'), 'target')
            self.pcinput.Bind(Config.GetStr('Outlaws.Vehicle.GearLeft',','), 'gearleft')
            self.pcinput.Bind(Config.GetStr('Outlaws.Vehicle.GearRight','.'), 'gearright')
            self.pcinput.Bind(Config.GetStr('Outlaws.Vehicle.Shoot','lctrl'), 'shoot')
            self.pcinput.Bind(Config.GetStr('Outlaws.Vehicle.Link','l'), 'link')
            self.pcinput.Bind(Config.GetStr('Outlaws.Vehicle.CamUp', 'w'), 'camup')
            self.pcinput.Bind(Config.GetStr('Outlaws.Vehicle.CamDown', 's'), 'camdown')
            self.pcinput.Bind(Config.GetStr('Outlaws.Vehicle.CamLeft', 'a'), 'camleft')
            self.pcinput.Bind(Config.GetStr('Outlaws.Vehicle.CamRight', 'd'), 'camright')
            for i in xrange(1, 9):
                key = str(i)
                self.pcinput.Bind(key, 'firehardpoint' + key)
        self.statusupdate()
        
        #If it is a representation of another player, fill in the details
        if not self.player:
            n = self.entity.Name
            self.net.sendData(n, 'nweps', [])
            self.net.sendData(n, 'nlnk', [])
            self.net.sendData(n, 'ntgt', [])
            self.net.sendData(n, 'ndmg', [])


    def pccommandinput_camleft1(self, pc, args):
        self.camera.SetYawVelocity(0.8)

    def pccommandinput_camleft0(self, pc, args):
        self.camera.SetYawVelocity(0)

    def pccommandinput_camright1(self, pc, args):
        self.camera.SetYawVelocity(-0.8)

    def pccommandinput_camright0(self, pc, args):
        self.camera.SetYawVelocity(0)

    def pccommandinput_camup1(self, pc, args):
        self.camera.SetPitchVelocity(-0.8)

    def pccommandinput_camup0(self, pc, args):
        self.camera.SetPitchVelocity(0)

    def pccommandinput_camdown1(self, pc, args):
        self.camera.SetPitchVelocity(0.8)

    def pccommandinput_camdown0(self, pc, args):
        self.camera.SetPitchVelocity(0)

    def pccommandinput_camdown_(self, pc, args):
        pass

    #The server handles damage processing. we only show it
    def pcdamage_hurt(self, pc, args):
        pos = args[parid('position')]
        amount = args[parid('amount')]
        source = args[parid('source')]
        if source != self.entity.Name:
            self.damageDeform(pos, amount)
    
    #The server told us to die
    def r_die(self, pc, args):
        addr, data = self.net.getNetData(args)
        source = data[0]
        self.die(source)
        
    #Damage messages sent from the server ------------------------------------------
    
    #armour damage
    def r_am_dmg(self, pc, args):
        addr, data = self.net.getNetData(args)
        idx, health = data
        self.armour[idx] = health
        self.postProcessDamage('am', idx, health, '')
        if self.hud and self.player:
            pars = parblock({'index' : idx, 'armour' : health})
            self.hud.Behaviour.SendMessage('setarmour', None, pars)

    #Frame damage
    def r_fr_dmg(self, pc, args):
        addr, data = self.net.getNetData(args)
        idx, health = data
        self.frame[idx] = health
        self.avgframe = sum(self.frame) / 4.0
        self.postProcessDamage('fr', idx, health, '')
        if self.hud and self.player:
            pars = parblock({'index' : idx, 'frame' : health, 'average' : self.avgframe})
            self.hud.Behaviour.SendMessage('setframe', None, pars)

    #Health damage
    def r_hl_dmg(self, pc, args):
        addr, data = self.net.getNetData(args)
        idx, health = data
        if self.health > 0:
            self.health = health
            self.postProcessDamage('hl', idx, health, '')
            if self.hud and self.player:
                pars = parblock({'health' : self.health})
                self.hud.Behaviour.SendMessage('sethealth', None, pars)

    #Powertrain damage
    def r_pt_dmg(self, pc, args):
        addr, data = self.net.getNetData(args)
        idx, health = data
        self.powertrain = health
        self.postProcessDamage('pt', idx, health, '')
        if self.hud and self.player:
            pars = parblock({'powertrain' : self.powertrain})
            self.hud.Behaviour.SendMessage('setpowertrain', None, pars)

    #Brakes damage
    def r_br_dmg(self, pc, args):
        addr, data = self.net.getNetData(args)
        idx, health = data
        self.brakes = health
        self.postProcessDamage('br', idx, health, '')
        if self.hud and self.player:
            pars = parblock({'brakes' : self.brakes})
            self.hud.Behaviour.SendMessage('setbrakes', None, pars)
    
    #Wheels damage
    def r_wh_dmg(self, pc, args):
        addr, data = self.net.getNetData(args)
        idx, health = data
        self.postProcessDamage('wh', idx, health, '')
        pars = parblock({'index' : idx, 'armour' : health})
        self.wheelents[idx].Behaviour.SendMessage('setarmour', None, pars)
        if self.hud and self.player:
            self.hud.Behaviour.SendMessage('setwheel', None, pars)
 
    #Weapons damage
    def r_we_dmg(self, pc, args):
        addr, data = self.net.getNetData(args)
        idx, health = data
        self.postProcessDamage('we', idx, health, '')
        pars = parblock({'index' : idx, 'armour' : health})
        self.hardpoints[idx].Behaviour.SendMessage('setarmour', None, pars)

    #The server needs to know about our weapon setup
    def r_nweps(self, pc, args):
        data = []
        #Run through all our mounts, pulling out the codename
        for mount in self.mounts:
            weapon = self.weapons[mount]
            codename = ''
            if weapon:
                codename = weapon.Behaviour.SendMessage('getcodename', None, args)
            data.append(codename)
        self.net.sendData(self.entity.Name, 'weps', data)
        
    #Weapon info sent from the server for this vehicle
    def r_weps(self, pc, args):
        addr, data = self.net.getNetData(args)
        for i, weapon in enumerate(data):
            mount = self.mounts[i]
            pars = parblock({'mount' : mount, 'weapon' : weapon})
            self.addweapon(self.entity, pars)
            
            #Now we can set the damage data we have recieved from the server
            if self.damagedata:
                pars = parblock({'armour' : self.damagedata[i]})
                weapon = self.weapons[mount]
                if weapon:
                    weapon.Behaviour.SendMessage('setarmour', None, pars)
            
    #info about existing damage sent from the server
    def r_dmgst(self, pc, args):
        addr, data = self.net.getNetData(args)
        self.health = data[0]
        self.frame = data[1:5]
        self.armour = data[5:9]
        self.powertrain = data[9]
        self.brakes = data[10]
        self.avgframe = data[11]
        
    #info about damage of weapons and wheels sent from the server
    def r_subdmg(self, pc, args):
        addr, data = self.net.getNetData(args)
        #We store this in case our weapons haven't arrived yet
        self.damagedata = data
        for i, ent in enumerate(self.weapons.values() + self.wheelents):
            if ent:
                pars = parblock({'armour' : data[i]})
                ent.Behaviour.SendMessage('setarmour', None, pars)                
        
    #Our collision damage is handled at the server side. Only handle cosmetics
    def pcdynamicbody_collision(self, pc, args):
        curtime = Clock.GetCurrentTicks()
        if (curtime - self.creationtime) >= 5000:
            pos = args['position']
            depth = args['depth']
            normal = args['normal']
            self.doDeform(pos, depth, normal)

    #Input sent remotely
    def r_inp(self, pc, args):
        addr, data = self.net.getNetData(args)
        inp = data[0]
        inpstring = self.inpmap[inp]
        inpmethod = getattr(self, 'pccommandinput_%s' % inpstring)
        inpmethod(self.entity, celGenericParameterBlock(0))
            
    #These two are only able to be done once the codename is set
    def setcodename(self, pc, args):
        ioNetworkEntCl.setcodename(self, pc, args)
        ioVehicleBase.setcodename(self, pc, args)
        
    def pctimer_wakeup(self, pc, args):
        ioNetworkEntCl.pctimer_wakeup(self, pc, args)
        ioVehicleBase.pctimer_wakeup(self, pc, args)
        #Reset the vehicle 2 sec after creation. Sometimes the wheels spawn stuck in the ground
        #if self.resetticks >= 0 and self.registered:
            #self.resetticks += 1
            #if self.resetticks >= 20:
                #self.resetticks = -1
                #self.entity.Behaviour.SendMessage('pccommandinput_recover1', None, celGenericParameterBlock(0))
        
    def pctimer_wakeupframe(self, pc, args):
        ioNetworkEntCl.pctimer_wakeupframe(self, pc, args)
        ioVehicleBase.pctimer_wakeupframe(self, pc, args)
        
    def pccommandinput_target1(self, pc, args):
        self.net.sendData(self.entity.Name, 'nxtgt', [])
    
    #Update our link setup, tell our server entity, update hud
    def pccommandinput_link1(self, pc, args):
        for i in self.currentgroup:
            self.releasehardpoint(i)
        ioVehicleBase.pccommandinput_link1(self, pc, args)
        hud = Entities['ioHUD']
        if self.player and hud:
            pars = parblock({'group' : cPickle.dumps(self.currentgroup, 0)})
            hud.Behaviour.SendMessage('setlink', None, pars)
        data = ['i', self.entity.Name, 'nxlnk']
        self.net.sendData(self.entity.Name, 'nxlnk', [])
        
    #The server sets our target
    def r_settgt(self, pc, args):
        addr, data = self.net.getNetData(args)
        self.targetname = data[0]
        self.targetUpdate()
        hud = Entities['ioHUD']
        if self.player and hud:
            pars = parblock({'name' : self.targetname})
            hud.Behaviour.SendMessage('settarget', None, pars)
        if self.botcontroller:
            pars = parblock({'name' : self.targetname})
            self.botcontroller.Behaviour.SendMessage('settarget', None, pars) 
     
    #The server sets our link group
    def r_setlnk(self, pc, args):
        #Stop shooting first so we don't mess things up
        for i in self.currentgroup:
            self.releasehardpoint(i)
        addr, self.currentgroup = self.net.getNetData(args)
        hud = Entities['ioHUD']
        if self.player and hud:
            pars = parblock({'group' : cPickle.dumps(self.currentgroup, 0)})
            hud.Behaviour.SendMessage('setlink', None, pars)
            
    def clearTarget(self):
        ioVehicleBase.clearTarget(self)
        hud = Entities['ioHUD']
        if self.player and hud:
            pars = parblock({'name' : self.targetname})
            hud.Behaviour.SendMessage('settarget', None, parblock(pars))
            
    def die(self, source):
        ioVehicleBase.die(self, source)
        if self.player and self.hud:
            self.hud.Behaviour.SendMessage('alldie', None, celGenericParameterBlock(0))
            
    #The hud told us to remove a weapon from our link group
    def removelink(self, pc, args):
        hardpoint = args[parid('hardpoint')]
        self.removeLink(hardpoint)
        self.net.sendData(self.entity.Name, 'rmlnk', [hardpoint])
        
    #The hud told us to add a weapon from our link group
    def addlink(self, pc, args):
        hardpoint = args[parid('hardpoint')]
        self.addLink(hardpoint)
        data = ['i', self.entity.Name, 'addlnk', hardpoint]
        self.net.sendData(self.entity.Name, 'addlnk', [hardpoint])
            
    #We don't handle wheel damage here, we do it remotely
    def wheeldamage(self, pc, args):
        pass
    
    #We don't handle weapon damage here, we do it remotely
    def weapondamage(self, pc, args):
        pass
    
    def r_rspn(self, pc, args):
        self.respawn(pc, args)
        
    def unstuck(self, resetorientation):
        ioVehicleBase.unstuck(self, resetorientation)
        
    def respawn(self, pc, args):
        ioVehicleBase.respawn(self, pc, args)
        if self.hud and self.player:
            self.hud.Behaviour.SendMessage('allrestore', None, celGenericParameterBlock(0))
            
    def setbot(self, pc, args):
        ioVehicleBase.setbot(self, pc, args)
        if self.bot:
            self.botcontroller = CreateEntity('ioBotController', self.blpython, 'ioBotController')
            pars = parblock({'entity' : self.entity})
            self.botcontroller.Behaviour.SendMessage('setcontrol', None, pars)
            pars = parblock({'name' : self.targetname})
            self.botcontroller.Behaviour.SendMessage('settarget', None, pars) 
        elif self.botcontroller:
            RemoveEntity(self.botcontroller)
            
    
            