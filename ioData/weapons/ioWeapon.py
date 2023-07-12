from pycel import *
import math
#Behaviour for a vehicle-mounted weapon. A mix of server and client code
class ioWeapon:
    api_version = 2
    
    def __init__(self, celEntity):
        self.entity = celEntity
        self.mesh = celMesh(self.entity)
        self.blpython = BehaviourLayers['blpython']
        if not self.mesh:
                print "No mesh!"
        self.scene = Engine.GetSectors().Get(0)
        if not self.scene:
                print "No scene found!"
                
        self.player = False
        #If we are a forward facing weapon
        self.front = True
        self.zvec = csVector3(0, 1, 0)
        self.armour = 100
        self.ammo = 0
        self.status = 'o '
        self.parent = None
        self.parenthealth = 100
        self.firing = False
        self.target = None
        self.targetmesh = None
        self.parentmesh = None
        self.creationtime = Clock.GetCurrentTicks()

        #When the timer wakes up, the weapon is ready again.
        #It is up to the weapon to set the timer and reset it after shooting
        #It stops players from mashing the keys to shoot faster
        #self.reloadtime must be set before this
        self.ready = False
        self.timer = celTimer(self.entity)
        self.timer.WakeUp(self.reloadtime, True)
        
        #Allowed angles, in radians, to adjust to our target
        self.yallowance = math.radians(5.0)
        self.xallowance = 0
        
        #We can't get our full transform until after we have been parented
        self.movable = self.mesh.Mesh.GetMovable()
        self.localtrans = self.movable.GetTransform()
        
        self.fire = None #The fire effect for when we die
        self.ffact = Engine.FindMeshFactory('weaponFire')

    #Damage our weapon
    def pcdamage_hurt(self, pc, args):
        if self.armour > 0:
            amount = args[getid('cel.parameter.amount')]
            source = args[getid('cel.parameter.source')]
            pars = parblock({'amount' : amount, 'source' : source, 'index' : self.index})
            self.parent.Behaviour.SendMessage('weapondamage', None, pars)
        
    #Set our index
    def setindex(self, pc, args):
        self.index = int(args[getid('cel.parameter.index')])

    #Take various actions depending on our level of armour
    def checkarmour(self):
        if self.armour <= 0:
            if not self.fire:
                if self.ffact:
                    self.fire = Engine.CreateMeshWrapper(self.ffact, 'weaponfire', self.scene, csVector3(0))
                    self.fire.GetMovable().GetSceneNode().SetParent(self.movable.GetSceneNode())
            self.armour = 0
            pars = celGenericParameterBlock(0)
            self.entity.Behaviour.SendMessage('fire0', None, pars)
            self.status = 'x '
        elif self.armour <= 50:
            self.status = '! '
            if self.fire:
                Engine.WantToDie(self.fire)
                self.fire = None
        elif self.armour <= 100:
            self.status = 'o '
            if self.fire:
                Engine.WantToDie(self.fire)
                self.fire = None
        self.sendupdate()
    
    #Set our codename
    def setcodename(self, pc, args):
        self.codename = args[getid('cel.parameter.codename')]

    #Get our codename
    def getcodename(self, pc, args):
        return self.codename
    
    #Set our parent vehicle
    def setparent(self, pc, args):
        self.parent = Entities[args[getid('cel.parameter.name')]]
        self.player = int(args[getid('cel.parameter.player')])
        self.parentmesh = celMesh(self.parent)
        self.parentmech = celMechanicsObject(self.parent)
        if self.player:
            pars = parblock({'name' : self.entity.Name})
            hud = Entities['ioHUD']
            hud.Behaviour.SendMessage('addweapon', None, pars)
            self.sendupdate()

    #Tell the hud a new status
    def sendupdate(self):
        if self.player:
            pars = parblock({'codename' : self.codename, 'name' : self.entity.Name, 'status' : self.status, 'ammo' : self.ammo})
            hud = Entities['ioHUD']
            hud.Behaviour.SendMessage('setweapon', None, pars)
    
    #Take an ai action. To be subclassed
    def aiupdate(self, pc, args):
        pars = celGenericParameterBlock(0)
        self.entity.Behaviour.SendMessage('fire1', None, pars)
        
    #The parent vehicle's health changed
    def setparenthealth(self, pc, args):
        self.parenthealth = args[getid('cel.parameter.health')]
        if self.armour >= self.parenthealth:
            self.armour = self.parenthealth
            self.checkarmour()

    #Only shoot when the key is held down, the weapon is healthy and full of ammo, and has reloaded
    def canShoot(self):
        if self.armour > 0 and self.ammo > 0 and self.ready:
            return True
        else:
            return False

    #Got shoot key event, work out if we can shoot
    def fire1(self, pc, args):
        self.firing = True
        if self.canShoot():
            self.shoot()
            
    #Stop shooting
    def fire0(self, pc, args):
        self.firing = False

    #Start shooting
    def pctimer_wakeup(self,pc,args):
        self.ready = True
        if self.firing and self.canShoot():
            self.shoot()

    #The base for actually shooting. Deplete ammo and do a check
    def shoot(self):
        self.ammo -= 1
        if self.ammo == 0:
            pars = celGenericParameterBlock(0)
            self.entity.Behaviour.SendMessage('fire0', None, pars)
        if self.player:
            self.sendupdate()
        self.timer.WakeUp(self.reloadtime, True)
        self.ready = False

    def pcdynamicbody_collision(self, pc, args):
        pass

    #Set a new target
    def settarget(self, pc, args):
        name = args[getid('cel.parameter.name')]
        if name != '' and name != None:
            self.target = Entities[name]
            if self.target:
                self.targetmesh = celMesh(self.target)
            else:
                self.targetmesh = None
        else:
            self.targetmesh = None

    def getarmour(self, pc, args):
        return self.armour

    def setarmour(self, pc, args):
        self.armour = args[getid('cel.parameter.armour')]
        self.checkarmour()
        
    #When the vehicle respawns, we restore our ammo and armour.
    def reset(self, pc, args):
        self.armour = 100
        self.ammo = self.fullammo
        self.checkarmour()
        
    #Set the orientation of our mount point
    def setorientation(self, pc, args):
        yvec = args[parid('y')]
        self.zvec = args[parid('z')]
        #Work out the normal direction we face
        if yvec.z > 0:
            self.front = True
        else:
            self.front = False
        self.localtrans.LookAt(yvec, self.zvec)
        self.movable.UpdateMove()
    
    #Update the weapon's aiming, if within our allowance
    def pctimer_wakeupframe(self, pc, args):
        if self.targetmesh and self.parentmesh and self.armour > 0:
            targetpos = self.targetmesh.Mesh.GetWorldBoundingBox().GetCenter()
            tposcarspace = self.parentmesh.Mesh.GetMovable().GetTransform().Other2This(targetpos)
            trelpos = tposcarspace - self.movable.GetPosition()
            #Stuff is back to front since the model is back to front thanks to pcdefcam
            #Make sure we are facing in the right direction all the time
            if (trelpos.z < 0.0 and self.front) or (trelpos.z > 0.0 and not self.front):
                trelpos.z *= -1.0
                
            trelpos.y = -trelpos.y
            trelpos.x = -trelpos.x
            
            if self.yallowance > 0.0:
                yangle = math.atan(trelpos.y / trelpos.z)
                #Apply our allowance limit
                if math.fabs(yangle) > self.yallowance:
                    trelpos.y = math.tan(self.yallowance) * trelpos.z
                    if yangle < 0.0:
                        trelpos.y *= -1.0
            else:
                trelpos.y = 0.0
                
            if self.xallowance > 0.0:
                xangle = math.atan(trelpos.x / trelpos.z)
                #Apply the allowance limit
                if math.fabs(xangle) > self.xallowance:
                    trelpos.x = math.tan(self.xallowance) * trelpos.z
                    if xangle < 0.0:
                        trelpos.x *= -1.0
            else:
                trelpos.x = 0.0
            #Reverse it since the weapons are back to front. blame pcdefaultcamera
            self.localtrans.LookAt(trelpos, self.zvec)
            self.movable.UpdateMove()
            
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
        self.fire0(pc, args)
        if self.fire:
            Engine.WantToDie(self.fire)
            self.fire = None