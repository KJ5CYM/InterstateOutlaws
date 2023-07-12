# Python behaviour that sets a path for linmove pcclass and traverses it, then
# sets another path... and so on.from time to time the path passes through the
# monitored entity.

from cspace import *
from blcelc import *
import random
class followpath:
	# INITIALIZATION
	def __init__(self,celEntity):
		print "Initializing followpath..."
		# check for linmove
		self.linmove = celGetLinearMovement(celEntity)
		if not self.linmove:
			self.linmove = celCreateLinearMovement(physicallayer_ptr,celEntity)
		self.mesh = celGetMesh(celEntity)
		self.mypath = csPath(4)
		self.monitor = "camera"
		mypath = self.mypath
		self.mypath.SetPositionVector(0,self.mesh.GetMesh().GetMovable().GetPosition())
		mypath.SetPositionVector(1,csVector3(20,20,20))
		mypath.SetPositionVector(2,csVector3(0,0,0))
		mypath.SetPositionVector(3,csVector3(5,5,5))
		mypath.SetUpVectors(csVector3(0,1,0))
		mypath.SetForwardVectors(csVector3(1,0,0))
		mypath.SetTime(0,0)
		mypath.SetTime(1,10)
		mypath.SetTime(2,20)
		mypath.SetTime(3,25)
		self.linmove.SetPath(self.mypath)
		# get the movable for monitored entity
                monitor_ent=physicallayer_ptr.FindEntity(self.monitor)
		if monitor_ent: 
			self.dest = celGetMesh(monitor_ent).GetMesh().GetMovable()
		else:
			self.dest = None

	def SetRamdomPath(self,number):
		a = random.random()*100.0
		b = random.random()*100.0
		c = random.random()*100.0
		self.mypath.SetPositionVector(number,csVector3(a,b,c))

	def pclinearmovement_arrived(self,celEntity,args):
		self.mypath.SetPositionVector(0,self.mesh.GetMesh().GetMovable().GetPosition())
		if random.random()>0.8 and self.dest:
			self.mypath.SetPositionVector(1,self.dest.GetPosition())
		else:
			self.SetRamdomPath(1)
		if random.random()>0.2:
			self.SetRamdomPath(3)
		else:	
			self.mypath.SetPositionVector(3,csVector3(20,20,20))
		self.SetRamdomPath(2)
		self.mypath.SetTime(0,0)
		self.mypath.SetTime(1,2)
		self.mypath.SetTime(2,10)
		self.mypath.SetTime(3,15)
		self.linmove.SetPathTime(0.0)
		self.linmove.SetPath(self.mypath)

