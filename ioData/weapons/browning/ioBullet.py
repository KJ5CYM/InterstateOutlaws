from pycel import *

class ioBullet:
    api_version = 2
    def __init__(self, celEntity):
        self.entity = celEntity
        self.damage = celDamage(self.entity)
        self.damage.DamageType = 'weapondamage'
        self.damage.FallOff = 'constant'
        self.expfact = Engine.FindMeshFactory('bulletExplosion')
        self.dirtfact = Engine.FindMeshFactory('bulletDirtFly')
        self.scene = Engine.GetSectors().Get(0)
        bulletFact = Engine.FindMeshFactory('genBullet')
        bulletmesh = Engine.CreateMeshWrapper(bulletFact, 'bullet', self.scene, csVector3(0))
        bulletmesh.GetMeshObject().SetColor(csColor(1, 1, 1))
        self.mesh = celMesh(self.entity)
        self.mesh.Mesh = bulletmesh
    
    def pcprojectile_hit(self, pc, args):
        entity = args[getid('cel.parameter.entity')]
	if entity:
            self.damage.SingleDamage(entity.Name)
        if self.dirtfact:
            mypos = self.mesh.Mesh.GetMovable().GetPosition()
            dirtmesh = Engine.CreateMeshWrapper(self.dirtfact, 'dirtexplosion', self.scene, mypos)
            Engine.DelayedRemoveObject(1500, dirtmesh)
            
    def pcprojectile_stopped(self, pc, args):
        mypos = self.mesh.Mesh.GetMovable().GetPosition()
        if self.expfact:
            expmesh = Engine.CreateMeshWrapper(self.expfact, 'bulletexplosion', self.scene, mypos)
            Engine.DelayedRemoveObject(1000, expmesh)
        Engine.WantToDie(self.mesh.Mesh)
        RemoveEntity(self.entity)

    def pcdamage_hurt(self, pc, args):
        pass

    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
