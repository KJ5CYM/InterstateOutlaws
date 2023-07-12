# Python behaviour that can be used as a base to control the player.
# can also control a cal3d or particles mesh if present in the entity.
# Uses: defaultcamera,commandinput,actormove,linmove,meshselect,mesh,tooltip

from cspace import *
from blcelc import *

class actor:
	# INITIALIZATION
	def __init__(self,celEntity):
		print "Initializing actor..."
		# check for pcdefaultcamera
		self.camera = celGetDefaultCamera(celEntity)
		if not self.camera:
			self.camera = celCreateDefaultCamera(physicallayer_ptr,celEntity)
		# check for pcdefaultcamera
		input = celGetCommandInput(celEntity)
		if not input:
			input = celCreateCommandInput(physicallayer_ptr,celEntity)
		# check for actormove
		self.actormove = celGetActorMove(celEntity)
		if not self.actormove:
			self.actormove = celCreateActorMove(physicallayer_ptr,celEntity)
		# check for mesh
		self.mesh = celGetMesh(celEntity)
		if not self.mesh:
			self.mesh = celCreateMesh(physicallayer_ptr,celEntity)
			self.mesh.LoadMesh("box", "/cellib/objects/box")
			pos = csVector3 (0, 1, 0)
			self.mesh.MoveMesh(room,pos)
		meshobj = self.mesh.GetMesh()
		self.cal3dstate = SCF_QUERY_INTERFACE(meshobj.GetMeshObject(), iSpriteCal3DState)
		self.partstate = SCF_QUERY_INTERFACE(meshobj.GetMeshObject(), iParticlesObjectState)
                if self.partstate:
                        self.basepps = self.partstate.GetParticlesPerSecond()

		# check for meshselect
		self.select = celGetMeshSelect(celEntity)
		if not self.select:
			self.select = celCreateMeshSelect(physicallayer_ptr,celEntity)
		# check for linmove
		self.linmove = celGetLinearMovement(celEntity)
		if not self.linmove:
			self.linmove = celCreateLinearMovement(physicallayer_ptr,celEntity)
		# check for tooltip
		self.tooltip = celGetToolTip(celEntity)
		if not self.tooltip:
			self.tooltip = celCreateToolTip(physicallayer_ptr,celEntity)
		# set some default parameters
		self.camera.SetModeName ("thirdperson")
		self.actormove.SetMovementSpeed(1.5)
		self.actormove.SetRunningSpeed (3.2)
		self.actormove.SetRotationSpeed (2.0)
		self.actormove.SetJumpingVelocity (5.9)

		# init collider, note that this invalidates any collider
		# set to the mesh
		#self.linmove.InitCD(csVector3(.5,1.0/3.0,.5),csVector3(.5,2.0/3.0,.5),
		#	csVector3(0,0.0,0))

		# XXX this should go in template
		# bind some keys
		input.Bind("up", "forward")
		input.Bind("down", "backward")
		input.Bind("left", "rotateleft")
		input.Bind("right", "rotateright")
		input.Bind("a", "strafeleft")
		input.Bind("d", "straferight")
		input.Bind("pgup", "lookup")
		input.Bind("pgdn", "lookdown")
		input.Bind("shift", "run")
		input.Bind("m", "cammode")
		input.Bind(" ", "jump")
	
	# ENTITY CALLBACKS
	# the engine will call this functions in response
	# to certain events. 
	
	# pctimer wakeup callback
	def pctimer_wakeup (self,celentity,args):
		pass
		
	# walk callbacks. note that for each bind defined in
	# pccommandinput there are three functions calles:
	# pccommandinput_(bindcode)1     -> Key down event
	# pccommandinput_(bindcode)0     -> Key release event
	# pccommandinput_(bindcode)_     -> Key hold events
	def pccommandinput_forward1(self,celentity,args):
		self.actormove.Forward(1)
                if self.partstate:
                        self.partstate.SetParticlesPerSecond(self.basepps*10)
			self.partstate.SetSphereEmitType(1.0,0.10)
			self.partstate.SetForce(10.0)
	def pccommandinput_forward0(self,celentity,args):
		self.actormove.Forward(0)
                if self.partstate:
			self.partstate.SetPointEmitType()
                        self.partstate.SetParticlesPerSecond(self.basepps)
			self.partstate.SetForce(0.0)
	def pccommandinput_forward_(self,celentity,args):
		pass
	def pccommandinput_backward1(self,celEntity,args):
		self.actormove.Backward(1)
	def pccommandinput_backward0(self,celEntity,args):
		self.actormove.Backward(0)
	def pccommandinput_backward_(self,celentity,args):
		pass
		
	# ROTATE
	def pccommandinput_rotateleft1(self,celEntity,args):
		self.actormove.RotateLeft(1)
	def pccommandinput_rotateleft0(self,celEntity,args):
		self.actormove.RotateLeft(0)
	def pccommandinput_rotateleft_(self,celentity,args):
		pass
	def pccommandinput_rotateright1(self,celEntity,args):
		self.actormove.RotateRight(1)
	def pccommandinput_rotateright0(self,celEntity,args):
		self.actormove.RotateRight(0)
	def pccommandinput_rotateright_(self,celentity,args):
		pass

	# STRAFE
	def pccommandinput_strafeleft1(self,celEntity,args):
		self.actormove.StrafeLeft(1)
		if self.cal3dstate:
			self.cal3dstate.SetAnimCycle("Strafeleft",1)
	def pccommandinput_strafeleft0(self,celEntity,args):
		self.actormove.StrafeLeft(0)
	def pccommandinput_straferight1(self,celEntity,args):
		self.actormove.StrafeRight(1)	
		if self.cal3dstate:
			self.cal3dstate.SetAnimCycle("Straferight",1)	
	def pccommandinput_straferight0(self,celEntity,args):
		self.actormove.StrafeRight(0)

	# LOOK UP AND DOWN
	def pccommandinput_lookup1(self,celEntity,args):
		self.camera.SetPitchVelocity(1.0)

	def pccommandinput_lookup0(self,celEntity,args):
		self.camera.SetPitchVelocity(0.0)

	def pccommandinput_lookdown1(self,celEntity,args):
		self.camera.SetPitchVelocity(-1.0)

	def pccommandinput_lookdown0(self,celEntity,args):
		self.camera.SetPitchVelocity(0.0)

	# JUMP
	def pccommandinput_jump1(self,celEntity,args):
		
		if self.cal3dstate:
			self.cal3dstate.SetAnimAction("Jump",0.1,0.2)
		self.actormove.Jump()

	# RUN
	def pccommandinput_run1(self,celEntity,args):
		self.actormove.Run(True)

	def pccommandinput_run0(self,celEntity,args):
		self.actormove.Run(False)

	# CAMERA MODES
	def pccommandinput_cammode1(self,celEntity,args):
		self.camera.SetMode(self.camera.GetNextMode ())

	# TRIGGER CALLBACKS
	# you will receive this callbacks when the entity enters
	# or leaves triggers.
	def pctrigger_entertrigger(self,celEntity,args):
		pass
	def pctrigger_leavetrigger(self,celEntity,args):
		pass

