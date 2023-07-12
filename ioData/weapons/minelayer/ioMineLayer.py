from pycel import *
import random
from ioWeapon import *

class ioMineLayer (ioWeapon):
    api_version = 2
    
    def __init__(self, celEntity):
        self.reloadtime = 1000
        ioWeapon.__init__(self, celEntity)
        self.recoiling=False
        self.ammo = 5
        self.fullammo = self.ammo
        self.movable = self.mesh.Mesh.GetMovable()
        self.mine = None
        self.makeMine()

    def makeMine(self):
        self.mine = CreateEntity(self.entity.Name + 'mine' + str(self.ammo), self.blpython, 'ioMine')
        mesh = celMesh(self.mine)
        mesh.Mesh.GetMovable().GetSceneNode().SetParent(self.mesh.Mesh.GetMovable().GetSceneNode())
        mesh.Mesh.GetMovable().UpdateMove()
        damage = celDamage(self.mine)
        #damage.SetDamageSource(self.parent.Name)

    def releaseMine(self):
        mesh = celMesh(self.mine)
        if mesh.Mesh:
            movable = mesh.Mesh.GetMovable()
            #move mine to avoid collision with parent car
            movable.SetPosition(movable.GetPosition() - csVector3(0, 0, 0.4))
            pos = movable.GetFullPosition()
            movable.GetSceneNode().SetParent(None)
            movable.SetSector(self.scene)
            movable.SetPosition(pos)
            movable.UpdateMove()
            self.mine.Behaviour.SendMessage('activate', None, celGenericParameterBlock(0))
            mech = celMechanicsObject(self.mine)
            direction = self.mesh.Mesh.GetMovable().GetTransform().This2Other(csVector3(0, 0, 1750))
            mech.AddForceOnce(direction, False, csVector3(0))
    
    def shoot(self):
        ioWeapon.shoot(self)
        self.releaseMine()
        if self.ammo > 0:
            self.makeMine()