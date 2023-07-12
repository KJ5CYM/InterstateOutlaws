from pycel import *
import random
from ioWeapon import *


class ioFFAR (ioWeapon):
    api_version = 2
    
    def __init__(self, celEntity):
        self.reloadtime = 500
        ioWeapon.__init__(self, celEntity)
        self.ammo = 200
        self.fullammo = self.ammo
        self.movable = self.mesh.Mesh.GetMovable()
        self.timer.WakeUpFrame(0)

    def shoot(self):
        ioWeapon.shoot(self)
        pos = self.movable.GetPosition()
        self.weapontransform=self.mesh.Mesh.GetMovable().GetFullTransform()
        x = random.random() * random.choice([-0.1, 0.1])
        y = 0.2 + random.random() * random.choice([-0.1, 0.1])
        barrelpos = self.weapontransform.This2Other(csVector3(x, y, -0.8))
        self.makeRocket(barrelpos)
        
    def makeRocket(self, barrelpos):
        
        enddir = self.weapontransform.This2OtherRelative(csVector3(0, 0, -1))
        rocket = CreateEntity('rocket', self.blpython, 'ioRocket')
        mesh = celMesh(rocket)
        mesh.Mesh.GetMovable().SetPosition(barrelpos)
        pcdamage = celDamage(rocket)
        pcdamage.SetDamageSource(self.parent.Name)
        pcdamage.SetDamage(50)
        pcprojectile = celProjectile(rocket)
        pvel = self.parentmech.Body.GetLinearVelocity()
        pspeed = -self.parentmech.Body.GetTransform().Other2ThisRelative(pvel).z
        pcprojectile.Start(enddir, 30 + pspeed, 100, 1)
        


