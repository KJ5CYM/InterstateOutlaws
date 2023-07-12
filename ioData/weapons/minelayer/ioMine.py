from pycel import *

class ioMine:
    api_version = 2
    def __init__(self, celEntity):
        self.entity = celEntity
        self.damage = celDamage(self.entity)
        self.damage.SetDamage(500)
        self.damage.DamageType = 'weapondamage'
        self.expfact = Engine.FindMeshFactory('mineExplosion')
        if not self.expfact:
            print 'missing mineExplosion factory'
        self.scene = Engine.GetSectors().Get(0)
        mineFact = Engine.FindMeshFactory('genmine')
        if not mineFact:
            print 'missing genmine factory'
        minemesh = Engine.CreateMeshWrapper(mineFact,'mine', self.scene, csVector3(0,0, -0.2))
        self.mesh = celMesh(self.entity)
        self.mesh.Mesh = minemesh
        self.active = False
        self.timer = celTimer(self.entity)
        #Explode after 10s anyway
        self.activetime = 0

    #Check if anything passes over the mine
    def pctimer_wakeup(self, pc, args):
        self.timer.WakeUp(50, False)
        if self.active:
            self.activetime += 50
            pos = self.mesh.Mesh.GetMovable().GetPosition() + csVector3(0, 0.2, 0)
            endpos = pos + csVector3(0, 0.8, 0)
            overents = pl.FindNearbyEntities(self.scene, pos, endpos)
            if overents.GetCount() > 0 or self.activetime >= 10000:
                self.explode()

    def explode(self):
        self.damage.AreaDamage(0.5)
        pos = self.mesh.Mesh.GetMovable().GetPosition()
        expmesh = Engine.CreateMeshWrapper(self.expfact, 'mineexplosion', self.scene, pos)
        Engine.DelayedRemoveObject(2000, expmesh)
        Engine.WantToDie(self.mesh.Mesh)
        self.active = False
        self.timer.Clear()
        #The remove entity is crashing because of mechobject. need to investigate
        RemoveEntity(self.entity)

    def activate(self, pc, args):
        self.mech = celMechanicsObject(self.entity)
        self.mech.Mass = 20
        self.mech.Friction = 0.5
        self.mech.AttachColliderBoundingBox()
        self.active = True
        #Take some time to actually activate. That way we won't blow up the car that launched us. o_O
        self.timer.WakeUp(1000, False)
        
    def pcdamage_hurt(self, pc, args):
        pass

    def pcdynamicbody_collision(self, pc, args):
        pass

    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()