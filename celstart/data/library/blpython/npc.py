# a "behaviour" for an npc with different flavours, controlled by the "chosen"
# pcproperty, with the following values:
# - 0: will walk and stop randomly. (default)
# - 1: will stay completely still.
# . 2: will walk reandomly (doesnt stop).
# also can control simple actions on an spr3d.
# uses: linmove, actormove, timer, mesh, properties
from cspace import *
from blcelc import *

import random

class npc:
	def __init__(self,celEntity):
		print "Initializing npc..."
		pl=physicallayer_ptr
		# get or create linmove
		self.linmove = celGetLinearMovement(celEntity)
                if not self.linmove:
                        self.linmove = celCreateLinearMovement(pl,celEntity)
		# get or create actormove
		self.actormove = celGetActorMove(celEntity)
                if not self.actormove:
                        self.actormove = celCreateActorMove(pl,celEntity)
		self.actormove.SetMovementSpeed(1.0)		
		self.actormove.SetJumpingVelocity (4.1)

		# set timer if there is not one
		self.timer = celGetTimer(celEntity)
                if not self.timer:
                        self.timer = celCreateTimer(pl,celEntity)
                        self.timer.WakeUp (500,True)

		# get pcproperties
		self.prop = celGetProperties(celEntity)
		self.thechosen=False
		if self.prop:
			i=self.prop.GetPropertyIndex("chosen")
			if not i == None:
				self.thechosen=self.prop.GetPropertyLong(i)
		# check for mesh
                self.mesh = celGetMesh(celEntity)
                if self.mesh:
                	meshobj = self.mesh.GetMesh()
			self.spr3dstate = SCF_QUERY_INTERFACE(meshobj.GetMeshObject(), iSprite3DState)
			if self.spr3dstate:
				self.spr3dstate.SetAction("walk")
		else:
			self.spr3dstate = None
		# check for thechosen state
		if self.thechosen == 1:
			if self.spr3dstate:
				self.spr3dstate.SetAction("stand")
		else:
			if self.spr3dstate:
				self.spr3dstate.SetAction("walk")

	def real_init(self,celEntity,room):
		pass
	def pcmeshsel_up(self,celEntity,args):
		pl = physicallayer_ptr
		actor = pl.FindEntity("camera")
		toolt = celGetToolTip(actor)
		if toolt:
			toolt.SetText(celEntity.GetName())
		

	def pctimer_wakeup(self,celEntity,args):
		# ADVANCE
		advance = random.random()
		is_advancing = advance<0.5
		# the chosen 1 does stay still
		if self.thechosen==1:
			return
		# ROTATE
		value = random.random()
		if value<0.3 and is_advancing:
			self.actormove.RotateLeft(1)
			self.actormove.RotateRight(0)
		elif value<0.8 and is_advancing:
			self.actormove.RotateLeft(0)
			self.actormove.RotateRight(1)
		else:
			self.actormove.RotateLeft(0)
			self.actormove.RotateRight(0)
		# the chosen 2 can only run forward
		if self.thechosen==2:
			self.actormove.Forward(1)
			return
		if is_advancing:
			if not self.actormove.IsMovingForward ():
				self.actormove.Forward(1)
				self.actormove.Backward(0)
				if self.spr3dstate:
					self.spr3dstate.SetAction("walk")
		else:
			if self.actormove.IsMovingForward ():
				self.actormove.Forward(0)
				self.actormove.Backward(0)
				if self.spr3dstate:
					self.spr3dstate.SetAction("stand")


