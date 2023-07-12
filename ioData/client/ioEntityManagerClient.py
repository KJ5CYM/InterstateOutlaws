from pycel import *
import random
import cPickle

import ioNetworkEntCl
import ioLoader
import ioNetHelper

#an entity which keeps track of the positions of managed entities,
#plus anything extra they need. this is the client version.
class ioEntityManagerClient :
    api_version = 2
    
    def __init__(self, celEntity):
        self.entity = celEntity
        self.entities = []
        self.numbots = 3
        
        self.net = ioNetHelper.ioNetHelper()

    def authok(self, pc, args):
        pass
    
    def r_newent(self, pc, args):
        server, data = self.net.getNetData(args)
        ent, codename = data
        testent = pl.FindEntity(ent)
        if not testent:
            print 'making new entity', ent
            entity = ioNetworkEntCl.makeEntity(codename, ent)
            pars = parblock({'player' : False})
            entity.Behaviour.SendMessage('setplayer', None, pars)
            self.entities.append(ent)

    def r_delent(self, pc, args):
        server, data = self.net.getNetData(args)
        name = data[0]
        try:
            self.entities.remove(name)
        except:
            pass
        entity = Entities[name]
        if entity:
            RemoveEntity(entity)
        #Tell all vehicles that this player is gone.
        pars = parblock({'name' : name})
        for entname in self.entities:
            ent = Entities[entname]
            if ent:
                ent.Behaviour.SendMessage('entremoved', None, pars)

    #This is bad! Shouldn't hardcode the van and browning in as defaults. But map unloading issue is messing things up.
    def makeplayer(self, pc, args):
        playername = Config.GetStr('Outlaws.Player.Name')
        codename = Config.GetStr('Outlaws.Player.Vehicle')
        gameworld = Entities['ioGameWorld']

        vehicle = ioNetworkEntCl.makeEntity(codename, playername)

        #Put its mesh in the sector
        vehiclemesh = celMesh(vehicle)
        vehiclemesh.MoveMesh(Engine.GetSectors().Get(0), vehiclemesh.Mesh.GetMovable().GetPosition())

        ##Set up the camera
        camera = celDefaultCamera(gameworld)
        camera.SetFollowEntity(vehicle)
        camera.ModeName = 'thirdperson'
        camera.Pitch = -0.15

        gmtp = Entities['ioGmTpCl']
        pars = parblock({'entity' : vehicle})
        gmtp.Behaviour.SendMessage('positionplayer', None, pars)

        #Tell it to be player controlled
        pars = parblock({'player' : True})
        vehicle.Behaviour.SendMessage('setplayer', None, pars)
            
        pars = celGenericParameterBlock(0)
        for mount in ['Front1', 'Front2', 'Roof1', 'Roof2', 'Side1', 'Side2', 'Rear1', 'Rear2']:
            weapon = Config.GetStr('Outlaws.Player.' + mount, 'BRWNG')
            pars = parblock({'mount' : mount, 'weapon' : weapon})
            vehicle.Behaviour.SendMessage('addweapon', None, pars)
            
        #Finally Register it to the network
        pars = parblock({'registered' : True})
        vehicle.Behaviour.SendMessage('setregistered', None, pars)

        self.entities.append(vehicle.Name)

    def fillbots(self, pc, args):
        vehicles = ioLoader.scanDir('vehicles')
        for i in xrange(self.numbots):
            #Pick a random vehicle, and extract its template
            vehicleinfo = random.choice(vehicles)
            vehicle = ioNetworkEntCl.makeEntity(vehicleinfo['Codename'], 'ioBot' + str(i))
            mesh = celMesh(vehicle)
            mesh.MoveMesh(Engine.GetSectors().Get(0), mesh.Mesh.GetMovable().GetPosition())

            if vehicle:
                gmtp = Entities['ioGmTpCl']
                pars = parblock({'entity' : vehicle})
                gmtp.Behaviour.SendMessage('positionplayer', None, pars)

            #Equip random model for weapons
            models = ioLoader.scanModels(vehicleinfo['Path'])
            model = random.choice(models)
            weapons = model['Weapons']
            for mount, weapon in weapons.items():
                pars = parblock({'mount' : mount, 'weapon' : weapon})
                vehicle.Behaviour.SendMessage('addweapon', None, pars)
                
            pars = parblock({'player' : False})
            vehicle.Behaviour.SendMessage('setplayer', None, pars)
 
            print 'registering bot'
            #Finally Register it to the network
            pars = parblock({'registered' : True})
            vehicle.Behaviour.SendMessage('setregistered', None, pars)
            
            pars = parblock({'bot' : True})
            vehicle.Behaviour.SendMessage('setbot', None, pars)

            self.entities.append(vehicle.Name)
            
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
                
        for entname in self.entities:
            ent = Entities[entname]
            if ent:
                RemoveEntity(ent)

    def makespectator(self, pc, args):
        pass