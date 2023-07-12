from pycel import *
import random
from ioWeapon import *

class ioBrowning (ioWeapon):
    api_version = 2
    
    def __init__(self, celEntity):
        self.reloadtime = 100
        ioWeapon.__init__(self, celEntity)
        self.recoiling=False
        self.ammo = 1000
        self.fullammo = self.ammo
        self.movable = self.mesh.Mesh.GetMovable()
        self.sparkfact = Engine.FindMeshFactory('barrelSpark')
        self.sparkmesh = None
        self.opos = None
        self.timer.WakeUpFrame(0)
        
    def shoot(self):
        ioWeapon.shoot(self)
        if not self.sparkmesh and self.sparkfact:
            mypos = csVector3(0.02, 0.05, -0.7)
            self.sparkmesh = Engine.CreateMeshWrapper(self.sparkfact, 'barrelsparks', self.scene, mypos)
            self.sparkmesh.GetMovable().GetSceneNode().SetParent(self.movable.GetSceneNode())
        pos = self.movable.GetPosition()
        if self.recoiling:
            self.movable.SetPosition(self.opos)
            self.recoiling = False
        else:
            self.movable.SetPosition(self.opos +  self.localtrans.This2OtherRelative(csVector3(0,0,0.1)))
            self.recoiling = True
        self.movable.UpdateMove()
        self.fulltrans = self.mesh.Mesh.GetMovable().GetFullTransform()
        barrelpos = self.fulltrans.This2Other(csVector3(0.05, 0.05, -1.75))
        self.makeBullet(barrelpos)
                    
    def fire0(self, pc, args):
        self.firing = False
        if self.sparkmesh:
            Engine.WantToDie(self.sparkmesh)
            self.sparkmesh = None
        #Make sure its back to its original position
        if self.recoiling:
            self.movable.SetPosition(self.opos)
            self.movable.UpdateMove()
            self.recoiling = False
            
    def makeBullet(self, barrelpos):
        endx = random.random() * random.choice([-1, 1])
        endy = random.random() * random.choice([-1 ,1])
        accuracy = 125
        enddir = self.fulltrans.This2OtherRelative(csVector3(endx, endy, -accuracy))
        bullet = CreateEntity('bullet', self.blpython, 'ioBullet')
        mesh = celMesh(bullet)
        mesh.Mesh.GetMovable().SetPosition(barrelpos)
        pcdamage = celDamage(bullet)
        pcdamage.SetDamageSource(self.parent.Name)
        pcdamage.SetDamage(5)
        pcprojectile = celProjectile(bullet)
        pvel = self.parentmech.Body.GetLinearVelocity()
        pspeed = -self.parentmech.Body.GetTransform().Other2ThisRelative(pvel).z
        pcprojectile.Start(enddir, 120.0 + pspeed, 100, 1)

    def setparent(self, pc, args):
        ioWeapon.setparent(self, pc, args)
        #Store original relative position for use in recoil
        self.opos = csVector3(self.movable.GetPosition())

