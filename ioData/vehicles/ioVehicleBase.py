from pycel import *
import cPickle
import ioLoader
import random
#The base code for a vehicle, independent of the networking code
class ioVehicleBase:
    api_version = 2
    
    def __init__(self, celEntity):
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']
        self.player = False
        self.bot = False
        self.mesh = celMesh(self.entity)
        self.wheeled = celWheeled(self.entity)
        self.deform = celMeshDeform(self.entity)
        self.usetrails = Config.GetBool('Outlaws.Settings.Video.DustTrails', True)
        if not self.usetrails:
            self.wheeled.SetCollisionCallbackEnabled(False)
       
        self.weapons = {}
        #Keep the weapons in an array as hardpoints for keyboard control
        self.hardpoints = []
        self.mounts = ['Front1', 'Front2', 'Roof1', 'Roof2', 'Side1', 'Side2', 'Rear1', 'Rear2']
        self.sidenames = ['Front', 'Rear', 'Left', 'Right',]
        self.windows = [None, None, None, None]
        self.exhausts = []
        self.wheeltrails = []
        for mount in self.mounts:
            self.weapons[mount] = None
        #Armour list - corresponds to icons on the hud - front rear left right
        self.armour = [100, 100, 100, 100]
        #Frame list - also hud icons - front rear left right
        self.frame = [100, 100, 100, 100]
        self.powertrain = 50
        self.brakes = 50
        self.avgframe = 100
        
        #Store a pointer to a replacement mesh (damaged or exploded) since pcmesh wont delete it for us
        self.rmesh = None
        #The main health of the vehicle, when this is 0, it dies
        self.health = 100
        self.scene = Engine.GetSectors().Get(0)

        #Map keys recieved over the network to commandinput bindngs
        self.inpmap = {}
        self.inpmap['ac1'] = 'accelerate1'
        self.inpmap['ac0'] = 'accelerate0'
        self.inpmap['br1'] = 'brake1'
        self.inpmap['br0'] = 'brake0'
        self.inpmap['sl1'] = 'steerleft1'
        self.inpmap['sl0'] = 'steerleft0'
        self.inpmap['sr1'] = 'steerright1'
        self.inpmap['sr0'] = 'steerright0'
        self.inpmap['hb1'] = 'handbrake1'
        self.inpmap['hb0'] = 'handbrake0'
        self.inpmap['rc1'] = 'recover1'
        self.inpmap['gl1'] = 'gearleft1'
        self.inpmap['gr1'] = 'gearright1'
        for i in xrange(1, 9):
            i = str(i)
            self.inpmap['fh' + i + '1'] = 'firehardpoint' + i + '1'
            self.inpmap['fh' + i + '0'] = 'firehardpoint' + i + '0'

        self.entmgr = Entities['ioEntMgrCl']
        self.targetname = ''

        self.lastcollision = Clock.GetCurrentTicks()
        self.lastrecovery = Clock.GetCurrentTicks()
        self.creationtime = Clock.GetCurrentTicks()
        
        #the fire effect created when the car is destroyed
        self.fire = None
        self.shatterfact = Engine.FindMeshFactory('windowShatter')
        
        #When subclassed by ioVehicle, has to be kept in sync with the timer time in ioNetworkEnt
        timer = celTimer(self.entity)
        timer.WakeUp(100, True)
        #timer.WakeUpFrame(0)
        
        #This dict matches up sets of similar weapons. eg {'FLMR' : [0,2,4], 'BRWNG' : [1,5]}
        self.weapongroups = {}
        #Holds which weapon group we are using right now
        self.currentgroup = []
        
        #Work out our width and our height for shadow
        mobj = self.mesh.Mesh.GetMeshObject().GetObjectModel ()
        bb = mobj.GetObjectBoundingBox()
        self.width = bb.GetSize().x * 1.1
        self.height = bb.GetSize().z * 1.4
        
        #Use the decal mgr to make a shadow
        #self.shadow = None
        #self.lastshadow = Clock.GetCurrentTicks()
        #self.makeShadow()
        #self.trail = 0
        
        self.enginesmoke = None
        
        #Whether windows are intact
        self.windowsintact = [True, True, True, True]
        
    def makeShadow(self):
        self.decal_mgr = CS_QUERY_REGISTRY_TAG_INTERFACE (oreg, "crystalspace.decal.manager", iDecalManager)
        if not self.decal_mgr:
            self.decal_mgr = CS_LOAD_PLUGIN(PluginManager, "crystalspace.decal.manager", iDecalManager)
        mat = Engine.FindMaterial('shadow')
        if not mat:
            Loader.LoadTexture ('shadow', '/outlaws/textures/shadow.png')
            mat = Engine.FindMaterial('shadow')
        self.dt = self.decal_mgr.CreateDecalTemplate(mat)
        #self.dt.SetDecalOffset(0.02)
        self.dt.SetPolygonNormalThreshold(0.25)
        self.dt.SetTimeToLive(0.5)
        self.dt.SetTopClipping(False)
        
    #Turn wheels into entities, so that they can process damage
    def entiseWheels(self):
        self.wheelents = []
        parentpars = parblock({'name' : self.entity.Name, 'player' : self.player})
        for i in xrange(self.wheeled.WheelCount):
            body = self.wheeled.GetWheelBody(i)
            mesh = body.GetAttachedMesh()
            name = self.entity.Name + 'Wheel' + str(i)
            ent = CreateEntity(name, self.blpython, 'ioWheel')
            pcmesh = celMesh(ent)
            pcmesh.Mesh = mesh
            #Tell the wheel its parent
            pars = parblock({'index' : i})
            ent.Behaviour.SendMessage('setindex', None, pars)
            ent.Behaviour.SendMessage('setparent', None, parentpars)
            self.wheelents.append(ent)
    
    #Create the dust trail particles that trail the car
    def makeDustTrails(self):
        if self.usetrails:
            partfact = Engine.FindMeshFactory('dustTrail')
            for i in xrange(self.wheeled.WheelCount):
                colpart = Engine.CreateMeshWrapper(partfact, self.entity.Name + 'trail' + str(i), self.scene, csVector3(0))
                partsys = SCF_QUERY_INTERFACE(colpart.GetMeshObject(), iParticleSystem)
                self.wheeltrails.append([colpart, partsys, False, 0.0])


    #Move and reset size of the wheel trails
    def pcwheeled_collision(self, pc, args):
        if self.usetrails:
            index = int(args[getid('cel.parameter.index')])
            position = args[getid('cel.parameter.position')]
            traildata = self.wheeltrails[index]
            if traildata:
                trail = traildata[0]
                trail.GetMovable().SetPosition(position)
                trail.GetMovable().UpdateMove()
                #Indicate a recent collision
                traildata[2] = True

    #Tell weapons and wheels of a new status
    def statusupdate(self):
        pars = parblock({'name' : self.entity.Name, 'player' : self.player})
        for ent in self.weapons.values() + self.wheelents:
            if ent:
                ent.Behaviour.SendMessage('setparent', None, pars)
                                        
    #Start timing a collision or add to the depth
    #We damage our frame and suspension from a collision
    def pcdynamicbody_collision(self, pc, args):
        curtime = Clock.GetCurrentTicks()
        partidxs = []
        if (curtime - self.creationtime) >= 5000 and self.health > 0:
            pos = args['position']
            normal = args['normal']
            depth = args['depth']
            collided = args['otherbody']
            currenttime = Clock.GetCurrentTicks()
            self.doDeform(pos, depth, normal)
            if (currenttime - self.lastcollision) >= 1000:
                self.lastcollision = currenttime
                idx = self.getarmouratpos(pos)
                damage = depth * 250
                if self.frame[idx] > 0 and damage >= 1.0:
                    self.frame[idx] -= damage
                    if self.frame[idx] < 0:
                        self.frame[idx] = 0
                        #The average is used by the label display and drag
                    self.avgframe = sum(self.frame) / 4.0
                    self.postProcessDamage('fr', idx, self.frame[idx], collided)
                return idx
                    
    def doDeform(self, pos, depth, normal):
        if depth > 0.01:
            amount = depth * normal
            self.deform.DeformMesh(pos, amount, True)

    def pccommandinput_gearleft1(self, pc, args):
        if self.wheeled.Gear > -1:
            self.wheeled.Gear -= 1
        self.sendinput('gl1')
        
    def pccommandinput_gearleft_(self, pc, args):
        pass
    
    def pccommandinput_gearleft0(self, pc, args):
        pass
    
    def pccommandinput_gearright1(self, pc, args):
        if self.wheeled.Gear < self.wheeled.GetTopGear():
            self.wheeled.Gear += 1
        self.sendinput('gr1')
        
    def pccommandinput_gearright_(self, pc, args):
        pass
    
    def pccommandinput_gearright0(self, pc, args):
        pass

    def pccommandinput_accelerate1(self, pc, args):
        self.wheeled.Accelerate(1.0)
        self.sendinput('ac1')

    def pccommandinput_accelerate_(self, celEntitiy, args):
        pass

    def pccommandinput_accelerate0(self, pc, args):
        self.wheeled.Accelerate(0.0)
        self.sendinput('ac0')

    def pccommandinput_brake1(self, pc, args):
        self.wheeled.Brake(1.0)
        self.sendinput('br1')
        
    def pccommandinput_brake_(self, pc, args):
        pass
        
    def pccommandinput_brake0(self, pc, args):
        self.wheeled.Brake(0.0)
        self.sendinput('br0')

        
    def pccommandinput_steerleft1(self, pc, args):
        self.wheeled.SteerLeft()
        self.sendinput('sl1')

    def pccommandinput_steerleft_(self, pc, args):
        pass
        
    def pccommandinput_steerleft0(self, pc, args):
        self.wheeled.SteerStraight()
        self.sendinput('sl0')
        
    def pccommandinput_steerright1(self, pc, args):
        self.wheeled.SteerRight()
        self.sendinput('sr1')
        
    def pccommandinput_steerright_(self, celEntitiy, args):
        pass
        
    def pccommandinput_steerright0(self, pc, args):
        self.wheeled.SteerStraight()
        self.sendinput('sr0')
        
    def pccommandinput_handbrake1(self, pc, args):
        self.wheeled.Handbrake(True)
        self.sendinput('hb1')
        
    def pccommandinput_handbrake_(self, pc, args):
        pass
        
    def pccommandinput_handbrake0(self, pc, args):
        self.wheeled.Handbrake(False)
        self.sendinput('hb0')

    def pcproperties_clearproperty(self, pc, args):
        pass
    
    def pccommandinput_cammode1(self, pc, args):
        cam = celGetDefaultCamera(Entities['ioGameWorld'])
        cam.Mode = cam.GetNextMode()
        
    def pccommandinput_cammode0(self, pc, args):
        pass
    
    def pccommandinput_cammode_(self, pc, args):
        pass
    
    def pccommandinput_recover1(self, pc, args):
        mech = celMechanicsObject(self.entity)
        currenttime = Clock.GetCurrentTicks()
        if (currenttime - self.lastrecovery) > 10000:
            self.lastrecovery = currenttime
            self.unstuck(True)
            self.sendinput('rc1')
        
    def pccommandinput_recover0(self, pc, args):
        pass
    
    def pccommandinput_recover_(self, pc, args):
        pass

    #Add a weapon to the vehicle. if we can, return 0. 1 means we don't have the mount point, 2 means that weapon doesnt exist
    def addweapon(self, pc, args):
        mount = args[getid('cel.parameter.mount')]
        weapon = args[getid('cel.parameter.weapon')]
        if weapon.strip() != '':
            bodyMesh = celMesh(self.entity)
            nodeob = self.scene.QueryObject().GetChild(self.codename + '-' + mount)
            if self.weapons[mount]:
                oldweapon = self.weapons[mount]
                self.hardpoints.remove(oldweapon)
                RemoveEntity(oldweapon)
            #Make sure vehicle has this mount point
            if nodeob:
                mountNode = SCF_QUERY_INTERFACE(nodeob, iMapNode)
                template = EntityTemplates[weapon + '-tpl']
                if template:
                    name = self.entity.Name + mount
                    weaponent = CreateEntity(template, name, celEntityTemplateParams())
                    self.weapons[mount] = weaponent
                    self.hardpoints.append(weaponent)
                    mesh = celMesh(weaponent)
                    mesh.MoveMesh(self.scene, mountNode.GetPosition())
                    mesh.Mesh.GetMovable().GetSceneNode().SetParent(bodyMesh.Mesh.GetMovable().GetSceneNode())
                    mesh.Mesh.GetMovable().UpdateMove()
                    yvec = mountNode.GetYVector()
                    zvec = mountNode.GetZVector()
                    #Tell the weapon its initial orienation
                    pars = parblock({'y' : yvec, 'z' : zvec})
                    weaponent.Behaviour.SendMessage('setorientation', None, pars)
                    #Tell the weapon its codename, so it can use them for the HUD
                    pars = parblock({'codename' : weapon})
                    weaponent.Behaviour.SendMessage('setcodename', None, pars)
                    
                    index = len(self.hardpoints)
                    pars = parblock({'index' : index - 1})
                    weaponent.Behaviour.SendMessage('setindex', None, pars)
                    
                    #Tell the weapon its player so it knows how to act
                    pars = parblock({'name' : self.entity.Name, 'player' : self.player})
                    weaponent.Behaviour.SendMessage('setparent', None, pars)
                    
                    #Add it to the weapon group for this weapon.
                    if self.weapongroups.has_key(weapon):
                        if index not in self.weapongroups[weapon]:
                            self.weapongroups[weapon].append(index)
                    else:
                        self.weapongroups[weapon] = [index]
                        
                    return 0
                else:
                    return 2
            else:
                return 1
        else:
            return 1

    def pccommandinput_firehardpoint11(self, pc, args):
        self.firehardpoint(1)

    def pccommandinput_firehardpoint21(self, pc, args):
        self.firehardpoint(2)

    def pccommandinput_firehardpoint31(self, pc, args):
        self.firehardpoint(3)

    def pccommandinput_firehardpoint41(self, pc, args):
        self.firehardpoint(4)

    def pccommandinput_firehardpoint51(self, pc, args):
        self.firehardpoint(5)
        
    def pccommandinput_firehardpoint61(self, pc, args):
        self.firehardpoint(6)
        
    def pccommandinput_firehardpoint71(self, pc, args):
        self.firehardpoint(7)

    def pccommandinput_firehardpoint81(self, pc, args):
        self.firehardpoint(8)

    def pccommandinput_firehardpoint10(self, pc, args):
        self.releasehardpoint(1)

    def pccommandinput_firehardpoint20(self, pc, args):
        self.releasehardpoint(2)

    def pccommandinput_firehardpoint30(self, pc, args):
        self.releasehardpoint(3)

    def pccommandinput_firehardpoint40(self, pc, args):
        self.releasehardpoint(4)

    def pccommandinput_firehardpoint50(self, pc, args):
        self.releasehardpoint(5)
        
    def pccommandinput_firehardpoint60(self, pc, args):
        self.releasehardpoint(6)

    def pccommandinput_firehardpoint70(self, pc, args):
        self.releasehardpoint(7)

    def pccommandinput_firehardpoint80(self, pc, args):
        self.releasehardpoint(8)

    def pccommandinput_firehardpoint1_(self, pc, args):
        pass

    def pccommandinput_firehardpoint2_(self, pc, args):
        pass

    def pccommandinput_firehardpoint3_(self, pc, args):
        pass

    def pccommandinput_firehardpoint4_(self, pc, args):
        pass

    def pccommandinput_firehardpoint5_(self, pc, args):
        pass
    
    def pccommandinput_firehardpoint6_(self, pc, args):
        pass

    def pccommandinput_firehardpoint7_(self, pc, args):
        pass

    def pccommandinput_firehardpoint8_(self, pc, args):
        pass

    def pccommandinput_link_ (self, pc, args):
        pass
    
    def pccommandinput_link0 (self, pc, args):
        pass
    
    def pccommandinput_shoot1(self, pc, args):
        for i in self.currentgroup:
            self.firehardpoint(i)
    
    def pccommandinput_shoot0(self, pc, args):
        for i in self.currentgroup:
            self.releasehardpoint(i)
            
    def pccommandinput_shoot_(self, pc, args):
        pass
    
    #Choose our next weapon group
    def pccommandinput_link1 (self, pc, args):
        if len(self.weapongroups) > 0:
            #Stop shooting first so we don't mess things up
            for i in self.currentgroup:
                self.releasehardpoint(i)
            groupslist = self.weapongroups.values()
            try:
                nextgroup = groupslist.index(self.currentgroup) + 1
            except ValueError:
                nextgroup = 0
            if nextgroup is len(groupslist):
                nextgroup = 0
            self.currentgroup = groupslist[nextgroup]
        else:
            self.currentgroup = []
        
    #Remove a link from our link group
    def removeLink(self, hardpoint):
        try:
            self.currentgroup.remove(hardpoint)
            self.releasehardpoint(hardpoint)
        except ValueError:
            pass
            
    #Add a link from our link group
    def addLink(self, hardpoint):
        if hardpoint not in self.currentgroup:
            self.currentgroup.append(hardpoint)

    #Fire a weapon based on its index
    def firehardpoint(self, hardpoint):
        if hardpoint <= len(self.hardpoints):
            pars = celGenericParameterBlock(0)
            self.hardpoints[hardpoint -1].Behaviour.SendMessage('fire1', None, pars)
            self.sendinput('fh' + str(hardpoint) + '1')

    def releasehardpoint(self, hardpoint):
        if hardpoint <= len(self.hardpoints):
            pars = celGenericParameterBlock(0)
            self.hardpoints[hardpoint -1].Behaviour.SendMessage('fire0', None, pars)
            self.sendinput('fh' + str(hardpoint) + '0')

    #Determine if we crossed the 90 or 80 boundary at a side.
    #Hide the window and make the effect
    def checkWindows(self, idx):
        if self.windowsintact[idx] == True and (self.frame[idx] <= 99.5 or self.armour[idx] <= 90.0):  
            self.windowsintact[idx] = False
            window = self.windows[idx]
            if window:
                mesh = celMesh(window)
                if self.shatterfact:
                    pos = mesh.Mesh.GetWorldBoundingBox().GetCenter()
                    shatter = Engine.CreateMeshWrapper(self.shatterfact, 'shatter', self.scene, pos)
                    Engine.DelayedRemoveObject(1000, shatter)
                mesh.Mesh.GetMovable().GetSceneNode().SetParent(None)
                mesh.Hide()

    #deform our mesh when damaged
    def damageDeform(self, pos, damage):
        direction = self.mesh.Mesh.GetMovable().GetPosition() - pos
        self.deform.DeformMesh(pos, direction.Unit() * damage, True)

    #The vehicle has been sent damage, probably from a weapon
    def pcdamage_hurt(self, pc,args):
        source = args[getid('cel.parameter.source')]
        pos = args[getid('cel.parameter.position')]
        dmgtype = args[getid('cel.parameter.type')]
        damage = args[getid('cel.parameter.amount')]
        #Don't count meagre amounts of damage
        if damage > 0.5:
            #First check we are past 5 seconds of creation
            if (Clock.GetCurrentTicks() - self.creationtime) >= 5000:
                if (source != self.entity.Name):
                    self.damageDeform(pos, damage)
                    idx = self.getarmouratpos(pos)
                    oldarmour = self.armour[idx]
                    #The armour from that side is able to soak up the damage
                    if self.armour[idx] > 0:
                        self.armour[idx] -= damage
                        if self.armour[idx] < 0:
                            self.armour[idx] = 0
                        self.postProcessDamage('am', idx, self.armour[idx], source)
                    #No armour in this direction, the car recieves damage
                    else:
                        if self.health > 0:
                            oldhealth = self.health
                            self.health -= damage
                            if self.health <= 0:
                                self.die(source)
                            self.postProcessDamage('hl', 0, self.health, source)
                            #The powertrain and brakes have a random chance of taking damage
                            ptchance = random.random()
                            if ptchance >= 0.5:
                                if self.powertrain > 0:
                                    self.powertrain -= damage
                                    if self.powertrain < 0:
                                        self.powertrain = 0
                                    self.postProcessDamage('pt', 0, self.powertrain, source)
                            brchance = random.random()
                            if brchance >= 0.5:
                                self.brakes -= damage
                                if self.brakes < 0:
                                    self.brakes = 0
                                self.postProcessDamage('br', 0, self.brakes, source)

    #This is inherited by the server to send to clients. By the client to send messages to the hud
    def postProcessDamage(self, zone, idx, health, source):
        if zone is 'hl':
            #Tell the weapons about our health so they know how to act
            pars = parblock({'health' : self.health})
            for weapon in self.weapons.itervalues():
                if weapon:
                    weapon.Behaviour.SendMessage('setparenthealth', None, pars)
            #See if we make smoke
            if health < 50:
                if not self.enginesmoke:
                    self.makeSmoke()
        elif zone is 'am'or zone is 'fr':
            self.checkWindows(idx)

    #The car is killed
    def die(self, source):
        self.health = -0.01
        self.powertrain = 0
        self.brakes = 0
        self.armour = [0, 0, 0, 0]
        self.frame = [0, 0, 0, 0]
        self.dieEffects()
        for i in range(self.wheeled.WheelCount):
            joint = self.wheeled.GetWheelJoint(i)
            joint.Attach(None, None)
        pars = parblock({'armour' : 0})
        for ent in self.wheelents + self.weapons.values():
            if ent:
                ent.Behaviour.SendMessage('setarmour', None, pars)
    
    #Randomly throw a rigid body.
    def randomThrow(self, body):
        #force to apply factor
        force = 5.0
        #Angular velocity factor
        avel = 7.0
        r = lambda n: random.random() * n
        x, z = [(r(force) + force  * random.choice([1, -1])) for i in [1,2]]
        y = (r(force) + force) * 1.5
        av = csVector3(r(avel), r(avel), r(avel)) + csVector3(avel, avel, avel)
        #body.AddForce(csVector3(x, y, z))
        body.SetLinearVelocity(csVector3(x, y, z))
        body.SetAngularVelocity(av)
        #body.AddTorque(torque)

    #Create an explosion, fire, destroy all windows and weapons
    def dieEffects(self):
        for exhaust in self.exhausts:
            if exhaust:
                Engine.WantToDie(exhaust)
        self.exhausts = [None, None]
         #Give the wheels explosion physics :)
        for i, ent in enumerate(self.wheelents):
            if ent:
                self.randomThrow(self.wheeled.GetWheelBody(i))
               
        #Temporarily broken
        #Detach the weapons and give them explosion physics :)
        #for part in self.weapons.itervalues():
            #if part:
                #partmesh = celMesh(part)
                #mesh = partmesh.Mesh
                #movable = mesh.GetMovable()
                #pos = movable.GetFullPosition()
                #movable.GetSceneNode().SetParent(None)
                #movable.SetSector(self.scene)
                #movable.SetPosition(pos)
                #movable.UpdateMove()
                #partmech = celMechanicsObject(part)
                #partmech.SetMass(10.0)
                #partmech.SetFriction(0.4)
                #partmech.AddToGroup('weaponsgroup')
                #partmech.AttachColliderBoundingBox()
                #self.randomThrow(partmech.GetBody())
        dmgfname = 'gen' + self.codename + 'Body-exp'
        self.changeBodyMesh(dmgfname, False)
        explosionfact = Engine.FindMeshFactory('carExplosion')
        explosion = Engine.CreateMeshWrapper(explosionfact, 'explosion', self.scene, csVector3(0))
        explosion.QuerySceneNode().SetParent(self.mesh.Mesh.QuerySceneNode())
        Engine.DelayedRemoveObject(5000, explosion)
        firefact = Engine.FindMeshFactory('carFire')
        self.fire = Engine.CreateMeshWrapper(firefact, 'fire', self.scene, csVector3(0))
        self.fire.GetMovable().GetSceneNode().SetParent(self.mesh.Mesh.GetMovable().GetSceneNode())
        self.fire.GetMovable().UpdateMove()
        Engine.DelayedRemoveObject(65000, self.fire)

    def destruct(self, pc, args):
        if self.rmesh:
            Engine.WantToDie(self.rmesh)
        self.entity.PropertyClassList.RemoveAll()
        for weapon in self.weapons.itervalues():
            if weapon:
                RemoveEntity(weapon)
        for wheel in self.wheelents:
            if wheel:
                RemoveEntity(wheel)
        for trail in self.wheeltrails:
            Engine.WantToDie(trail[0])
        self.weapons = {}
        self.hardpoints = []
        for exhaust in self.exhausts:
            if exhaust:
                Engine.WantToDie(exhaust)
        for window in self.windows:
            if window:
                RemoveEntity(window)
                
    ##update the position of our shadow at most every 30ms
    #def pctimer_wakeupframe(self, pc, args):
        #ct = Clock.GetCurrentTicks()
        #if ct - self.lastshadow > 10:
            #self.lastshadow = ct
            #m = self.mesh.Mesh.GetMovable()
            #t = m.GetTransform()
            #p = self.wheeled.GetWheelBody(0).GetPosition()
            #result = self.scene.HitBeam(m.GetPosition() + csVector3(0, 0.5, 0), m.GetPosition() - csVector3(0, 10, 0))
            #self.shadow = self.decal_mgr.CreateDecal(self.dt, self.scene, result.isect, t.GetFront(), t.GetUp(), self.width, self.height, self.shadow)
        
    #Add a drag force proportional to frame damage. Also reset the car one off at the start
    def pctimer_wakeup(self, pc, args):
        vel = self.mech.GetLinearVelocity()
        movable = self.mesh.Mesh.GetMovable()
        trans = movable.GetTransform()
        #Add a drag force
        drag = (100 - self.avgframe) * -vel
        #Apply a downforce to keep the wheels planted
        #drag -= csVector3(0, (vel.Norm() * 0.01) * self.body.GetMass(), 0)
        #self.mech.AddForceDuration(drag * 2.5, False, movable.GetPosition(), 0.1)
        
        if self.usetrails:
            for i, traildata in enumerate(self.wheeltrails):
                if traildata:
                    partsys = traildata[1]
                    touch = traildata[2]
                    oldsize = traildata[3]
                    body = self.wheeled.GetWheelBody(i)
                    speed = body.GetAngularVelocity().Norm()
                    speed += body.GetLinearVelocity().Norm()
                    wantsize = (speed / 75.0)
                    #This should adjust with framerate ideally
                    increment = 0.05
                    if touch:
                        if wantsize > oldsize:
                            newsize = oldsize + increment
                        elif wantsize < oldsize:
                            newsize = oldsize - increment
                        else:
                            newsize = oldsize
                    else:
                        newsize = oldsize - increment
                    if newsize < 0.0:
                        newsize = 0.0
                    partsys.SetParticleSize(csVector2(newsize, newsize))
                    traildata[2] = False
                    traildata[3] = newsize 
                    
    def ai(self):
        pass

    #Return our armour of side of a certain index
    def getarmour(self, pc, args):
        idx = args[getid('cel.parameter.index')]
        return self.armour[idx]
    
    #Return our health
    def gethealth(self, pc, args):
        return self.health

    #Work out which side of armour is affected by damage at a given position
    def getarmouratpos(self, pos):
        relpos = self.mesh.Mesh.GetMovable().GetTransform().Other2This(pos)
        direction = relpos.Unit()
        if relpos.z < relpos.x:
            if relpos.z < -relpos.x:
                idx = 0
            else:
                idx = 2
        else:
            if relpos.z > -relpos.x:
                idx = 1
            else:
                idx = 3
        return idx
                
    #Now that we have our codename we can fill in windows
    def makeWindows(self):
        for i, sidename in enumerate(self.sidenames):
            wfact = Engine.FindMeshFactory('gen' + self.codename + sidename)
            if wfact:
                ent = CreateEntity(self.entity.Name + sidename, None, None)
                pcmesh = celMesh(ent)
                partmesh = Engine.CreateMeshWrapper(wfact, self.entity.Name + 'part', self.scene, csVector3(0))
                pcmesh.Mesh = partmesh
                pcmesh.Mesh.GetMovable().GetSceneNode().SetParent(self.mesh.Mesh.GetMovable().GetSceneNode())
                pcmesh.Mesh.GetMovable().UpdateMove()
                self.windows[i] = ent
    
    #Make exhaust smoke effect
    def makeExhaust(self):
        exhaustfact = Engine.FindMeshFactory('exhaustSmoke')
        mesh = celMesh(self.entity).Mesh
        for point in ['Exhaust1', 'Exhaust2']:
            nodeob = self.scene.QueryObject().GetChild('%s-%s'% (self.codename, point))
            if nodeob:
                node = SCF_QUERY_INTERFACE(nodeob, iMapNode)
                if node:
                    exhaust = Engine.CreateMeshWrapper(exhaustfact, 'exhaustsmoke', self.scene, node.GetPosition())
                    exhaust.GetMovable().GetSceneNode().SetParent(mesh.GetMovable().GetSceneNode())
                    exhaust.GetMovable().UpdateMove()
                    self.exhausts.append(exhaust)
                    
    def makeSmoke(self):
        smokefact = Engine.FindMeshFactory('engineSmoke')
        mesh = celMesh(self.entity).Mesh
        nodeob = self.scene.QueryObject().GetChild('%s-Engine' % self.codename)
        if nodeob:
            node = SCF_QUERY_INTERFACE(nodeob, iMapNode)
            if node:
                self.enginesmoke = Engine.CreateMeshWrapper(smokefact, 'enginesmoke', self.scene, node.GetPosition())
                self.enginesmoke.GetMovable().GetSceneNode().SetParent(mesh.GetMovable().GetSceneNode())
                self.enginesmoke.GetMovable().UpdateMove()

    #Change body mesh to a new mesh and update all submeshes if wanted
    def changeBodyMesh(self, dmgfname, reparent):
        dmgfact = Engine.FindMeshFactory(dmgfname)
        if dmgfact:
	    if self.rmesh:
                Engine.WantToDie(self.rmesh)
	    dmgmesh = Engine.CreateMeshWrapper(dmgfact, self.entity.Name + 'Body', self.scene, self.mesh.Mesh.GetMovable().GetPosition())
            self.body.AttachMesh(dmgmesh)
	    self.mesh.Mesh = dmgmesh
	    self.deform.Mesh = dmgmesh
	    self.deform.ResetDeform()
            self.rmesh = dmgmesh
            if reparent:
                for window in self.windows:
                    if window:
                        mesh = celMesh(window).Mesh
			mesh.GetMovable().SetPosition(csVector3(0))
                        mesh.GetMovable().GetSceneNode().SetParent(dmgmesh.GetMovable().GetSceneNode())
                        mesh.GetMovable().UpdateMove()
                for mount, weapon in self.weapons.iteritems():
                    if weapon:
			mesh = celMesh(weapon).Mesh
			mech = celGetMechanicsObject(weapon)
			if mech:
			    weapon.PropertyClassList.Remove(mech)
			#Find the mount for the weapon, and reparent it to the mount position and orientation
			nodeob = self.scene.QueryObject().GetChild(self.codename + '-' + mount)
			if nodeob:
			    mountNode = SCF_QUERY_INTERFACE(nodeob, iMapNode)
			    mesh.GetMovable().SetPosition(mountNode.GetPosition())
			    mesh.GetMovable().GetSceneNode().SetParent(dmgmesh.GetMovable().GetSceneNode())
			    zvec = mountNode.GetZVector()
			    yvec = mountNode.GetYVector()
			    mesh.GetMovable().GetTransform().LookAt(yvec, zvec)
                            mesh.GetMovable().UpdateMove()
                for exhaust in self.exhausts:
                    if exhaust:
                        exhaust.GetMovable().GetSceneNode().SetParent(dmgmesh.GetMovable().GetSceneNode())
                        exhaust.GetMovable().UpdateMove()
            return True
        else:
            return False

    #An entity was removed, if its our target we need to quickly remove our references to it
    def entremoved(self, pc, args):
        ent = args[parid('name')]
        if ent == self.targetname:
            self.clearTarget()

    #Unset our target. useful when a player leaves
    def clearTarget(self):
        self.targetname = ''
        self.targetUpdate()

    def targetUpdate(self):
        pars = {'name' : self.targetname}
        for weapon in self.weapons.itervalues():
            if weapon:
                weapon.Behaviour.SendMessage('settarget', None, parblock(pars))
        
    def pccomandinput_target1(self, pc, args):
        pass
    
    def pccomandinput_target0(self, pc, args):
        pass
    
    def pccomandinput_target_(self, pc, args):
        pass
    
    def setcodename(self, pc, args):
        #Create entities out of the wheels
        self.entiseWheels()
        self.makeDustTrails()
        self.makeWindows()
        self.makeExhaust()
    
    #A wheel has recieved damage
    def wheeldamage(self, pc, args):
        if (Clock.GetCurrentTicks() - self.creationtime >= 5000):
            amount = args[parid('amount')]
            source = args[parid('source')]
            index = int(args[parid('index')])
            wheel = self.wheelents[index]
            armour = wheel.Behaviour.SendMessage('getarmour', None, args)
            if armour > 0 and source != self.entity.Name and amount >= 0.5:
                armour -= amount
                if armour < 0:
                    armour = 0
                pars = parblock({'armour' : armour})
                wheel.Behaviour.SendMessage('setarmour', None, pars)
                self.postProcessDamage('wh', index, armour, source)
        
    #A weapon has recieved damage
    def weapondamage(self, pc, args):
        if (Clock.GetCurrentTicks() - self.creationtime >= 5000):
            amount = args[parid('amount')]
            source = args[parid('source')]
            index = int(args[parid('index')])
            weapon = self.hardpoints[index]
            armour = weapon.Behaviour.SendMessage('getarmour', None, args)
            #Don't hurt ourselves, and don't count small amounts of damage
            if armour > 0 and source != self.entity.Name and amount >= 0.5:
                armour -= amount
                if armour < 0:
                    armour = 0
                pars = parblock({'armour' : armour})
                weapon.Behaviour.SendMessage('setarmour', None, pars)
                self.postProcessDamage('we', index, armour, source)       
                
    #Respawn and reset the vehicle
    def respawn(self, pc, args):
        self.creationtime = Clock.GetCurrentTicks()
        self.wheeled.DestroyAllWheels()
        self.wheeled.RestoreAllWheels()
        if self.fire:
            Engine.WantToDie(self.fire)
            self.fire = None
        if self.enginesmoke:
            Engine.WantToDie(self.enginesmoke)
            self.enginesmoke = None
        self.changeBodyMesh('gen' + self.codename + 'Body', True)
        self.makeExhaust()
        self.armour = [100, 100, 100, 100]
        self.frame = [100, 100, 100, 100]
        self.powertrain = 50
        self.brakes = 50
        self.avgframe = 100
        self.health = 100
        self.windowsintact = [True, True, True, True]
        for weapon in self.weapons.itervalues():
            if weapon:
                mech = celMechanicsObject(weapon)
                mech.Body.DestroyColliders()
        for ent in self.wheelents + self.weapons.values():
            if ent:
                ent.Behaviour.SendMessage('reset', None, celGenericParameterBlock(0))
        #we also get stuck after recreating the wheels
        self.unstuck(True)
        
    def unstuck(self, resetorientation):
        self.mech.AddForceDuration(csVector3(0, 25.0 * self.mech.GetMass() ,0), False, csVector3(0), 0.25)
        if resetorientation:
            self.mech.Body.SetTransform(csOrthoTransform(csMatrix3(), self.mech.Body.GetPosition()))
        
    #start using ai
    def setbot(self, pc, args):
        self.bot = True
        
    def gettargetname(self, pc, args):
        return self.targetname