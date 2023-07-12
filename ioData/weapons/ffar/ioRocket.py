from pycel import *

class ioRocket:
    api_version = 2
    def __init__(self, celEntity):
        self.entity = celEntity
        self.damage = celDamage(self.entity)
        self.damage.DamageType = 'weapondamage'
        self.expfact = Engine.FindMeshFactory('rocketExplosion')
        self.scene = Engine.GetSectors().Get(0)
        bulletFact = Engine.FindMeshFactory('genBigRocket')
        bulletmesh = Engine.CreateMeshWrapper(bulletFact, 'bullet', self.scene, csVector3(0))
        self.mesh = celMesh(self.entity)
        self.mesh.Mesh = bulletmesh
        self.dirtfact = Engine.FindMeshFactory('rocketDirtFly')
	trailfact = Engine.FindMeshFactory('rocketTrail')
        if trailfact:
            self.trailmesh = Engine.CreateMeshWrapper(trailfact, 'rockettrail', self.scene, csVector3(0,0,-1.2))
            self.trailmesh.QuerySceneNode().SetParent(self.mesh.Mesh.QuerySceneNode())
        firefact = Engine.FindMeshFactory('rocketFire')
        if firefact:
            self.firemesh = Engine.CreateMeshWrapper(firefact, 'rocketfire', self.scene, csVector3(0,0,-0.2))
            self.firemesh.QuerySceneNode().SetParent(self.mesh.Mesh.QuerySceneNode())
    
    def pcprojectile_hit(self, pc, args):
        self.damage.AreaDamage(0.1)
            
    #Explode the rocket. create a dirt flying effect, explosion effect, and unparent the trail effects.
    #finally remove ourselves.
    def pcprojectile_stopped(self, pc, args):
        mypos = self.mesh.Mesh.GetMovable().GetPosition()
        if self.expfact:
            expmesh = Engine.CreateMeshWrapper(self.expfact, 'rocketexplosion', self.scene, mypos)
            Engine.DelayedRemoveObject(1500, expmesh)
        if self.dirtfact:
            dirtmesh = Engine.CreateMeshWrapper(self.dirtfact, 'dirtexplosion', self.scene, mypos)
            Engine.DelayedRemoveObject(1500, dirtmesh)
        pos = self.trailmesh.GetMovable().GetFullPosition()
        self.trailmesh.GetMovable().GetSceneNode().SetParent(None)
        self.trailmesh.GetMovable().SetPosition(self.scene, pos)
        self.trailmesh.GetMovable().UpdateMove()
        Engine.DelayedRemoveObject(1500, self.trailmesh)
        self.firemesh.GetMovable().GetSceneNode().SetParent(None)
        self.firemesh.GetMovable().SetPosition(self.scene, pos)
        self.firemesh.GetMovable().UpdateMove()
        Engine.DelayedRemoveObject(500, self.firemesh)
        Engine.WantToDie(self.mesh.Mesh)
        RemoveEntity(self.entity)

    def pcdamage_hurt(self, pc, args):
        pass

    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
