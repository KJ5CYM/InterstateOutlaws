# a "behaviour" for an entity that continuously looks at the player.
# this goes together with a pctimer with a wakeupframe on the entity, but
# the behaviour will create it automatically if not present already.
from cspace import *
from blcelc import *

import random

class lookat:
	def __init__(self,celEntity):
		print "initializing lookat",celEntity.GetName()
		# some variables for the counter
		self.monitor		=	"camera"

		# get the mesh and movable for this entity
		self.mesh = celGetMesh(celEntity)
		if not self.mesh:
			print "lookat requires entity having a mesh!"
		self.movable = self.mesh.GetMesh().GetMovable()
		# get the movable for monitored entity
		monitor_ent=physicallayer_ptr.FindEntity(self.monitor)
		if not monitor_ent:
			print "lookat could not find",self.monitor,"entity"
		monitor_mesh  = celGetMesh(monitor_ent)
		if monitor_mesh:
			self.monitor_mov  = monitor_mesh.GetMesh().GetMovable()
		else:
			"lookat requires monitored entity having a mesh!"
		
		# set up the frame callback
		self.timer = celGetTimer(celEntity)
		if not self.timer:
			self.timer = celCreateTimer(physicallayer_ptr,celEntity)
			self.timer.WakeUpFrame (CEL_EVENT_PRE)


	def pctimer_wakeupframe(self,celEntity,args):
		monitored_pos = self.monitor_mov.GetPosition()
		self_pos = self.movable.GetPosition()
		self.movable.GetTransform().LookAt(monitored_pos-self_pos,csVector3(0,1,0))
		self.movable.UpdateMove()

