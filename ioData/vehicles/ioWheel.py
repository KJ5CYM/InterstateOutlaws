from pycel import *
import random
#Behaviour for a wheel. It is a mix of client and server code.
class ioWheel:
    api_version = 2
    def __init__(self, celEntity):
        self.entity = celEntity
        self.armour = 100
        self.parent = None
        self.index = 0
        self.player = False
    
    def setindex(self, pc, args):
        self.index = int(args[parid('index')])
        
    def setparent(self, pc, args):
        self.parent = Entities[args[parid('name')]]
        self.player = args[parid('player')]
        self.wheeled = celWheeled(self.parent)
        self.parentbody = celMechanicsObject(self.parent).Body
        self.body = self.wheeled.GetWheelBody(self.index)
        self.joint = self.wheeled.GetWheelJoint(self.index)
        self.mesh = celMesh(self.entity)
        self.realpower = self.wheeled.GetWheelEnginePower(self.index)
        self.meshdeform = celMeshDeform(self.entity)
        self.meshdeform.DeformFactor = 0.005
        self.meshdeform.MaxDeform = 0.1
        self.meshdeform.Radius = 0.25
        self.meshdeform.Noise = 0
        
    def pcdamage_hurt(self, pc, args):
        if self.armour > 0:
            amount = args[parid('amount')]
            source = args[parid('source')]
            pars = parblock({'amount' : amount, 'source' : source, 'index' : self.index})
            self.parent.Behaviour.SendMessage('wheeldamage', None, pars)
            
    def setarmour(self, pc, args):
        oldarmour = self.armour
        self.armour = args[parid('armour')]
        dmg = oldarmour - self.armour
        if dmg > 0:
            self.meshdeform.DeformMesh(csVector3(0.1, 0.2, 0.0), csVector3(0.2, 0.2, -1.0) * dmg)

        #Power is minimum at half
        power = self.realpower * 0.5 + (self.realpower * (self.armour / 200.0))
        self.wheeled.SetWheelEnginePower(self.index, power)

    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()

    def getarmour(self, pc, args):
        return self.armour
    
    def reset(self, pc, args):
        pars = parblock({'armour' : 100})
        self.entity.Behaviour.SendMessage('setarmour', None, pars)
        self.mesh.Mesh = self.wheeled.GetWheelBody(self.index).GetAttachedMesh()
        self.meshdeform.ResetDeform()
        self.meshdeform.Mesh = self.mesh.Mesh