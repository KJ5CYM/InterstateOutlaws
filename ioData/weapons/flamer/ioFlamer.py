from pycel import *
import random
from ioWeapon import *

class ioFlamer (ioWeapon):
    api_version = 2
    
    def __init__(self, celEntity):
        self.reloadtime = 100
        ioWeapon.__init__(self, celEntity)
        self.ammo = 500
        self.fullammo = self.ammo
        self.effectfact = Engine.FindMeshFactory('flamerFire')
        self.effect = None
        
        self.damage = celDamage(self.entity)
        self.damage.SetDamage(6)
        self.damage.DamageType = 'weapondamage'
        self.damage.FallOff = 'constant'
        self.scenename = self.scene.QueryObject().GetName()
        
        self.timer.WakeUpFrame(0)

    def setparent(self, pc, args):
        ioWeapon.setparent(self, pc, args)
        self.damage.SetDamageSource(self.parent.Name)
	
    def shoot(self):
        ioWeapon.shoot(self)
        if self.effectfact and not self.effect:
            self.effect = Engine.CreateMeshWrapper(self.effectfact,'fire',self.scene, csVector3(0))
            self.effect.QuerySceneNode().SetParent(self.mesh.Mesh.QuerySceneNode())
            self.effect.GetMovable().UpdateMove()
        if self.effect:
            #dmgbox = self.effect.GetWorldBoundingBox()
            #dmgents = pl.FindNearbyEntities(self.scene, dmgbox, False)
            #for ent in dmgents:
            #    self.damage.SingleDamage(ent.Name)
            
            #flamedir = self.movable.GetFullTransform().This2OtherRelative(csVector3(0, 0, -1))
            #flamecentre = self.movable.GetFullPosition()
            flamecentre = self.movable.GetFullTransform().This2Other(csVector3(0, 0, -0.75))
            self.damage.SetDamageLocation(self.scenename, flamecentre)
            self.damage.AreaDamage(0.75)
            #Not sure how well this is working
            #self.damage.BeamDamage(flamedir, 3)
                    
    def fire0(self, pc, args):
        self.firing = False
        if self.effect:
            Engine.WantToDie(self.effect)
            self.effect = None
 
