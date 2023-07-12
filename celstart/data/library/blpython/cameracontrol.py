# Python behaviour that can be used as a base to control a camera
# whose player does not move.
# Uses: defaultcamera,commandinput,actormove,linmove,meshselect,mesh,tooltip

from cspace import *
from blcelc import *

class cameracontrol:
	# INITIALIZATION
	def __init__(self,celEntity):
		print "Initializing actor..."
		# check for pcdefaultcamera
		#self.camera = celGetDefaultCamera(celEntity)
		#if not self.camera:
		#	self.camera = celCreateDefaultCamera(physicallayer_ptr,celEntity)
		# check for pcdefaultcamera
		input = celGetCommandInput(celEntity)
		if not input:
			input = celCreateCommandInput(physicallayer_ptr,celEntity)
		# check for actormove
		self.actormove = celGetActorMove(celEntity)
		if not self.actormove:
			self.actormove = celCreateActorMove(physicallayer_ptr,celEntity)
		# check for mesh
		#self.mesh = celGetMesh(celEntity)
		#if not self.mesh:
		#	self.mesh = celCreateMesh(physicallayer_ptr,celEntity)
		#	self.mesh.LoadMesh("box", "/cellib/objects/box")
		#	pos = csVector3 (0, 1, 0)
		#	self.mesh.MoveMesh(room,pos)
		#meshobj = self.mesh.GetMesh()
		#self.cal3dstate = SCF_QUERY_INTERFACE(meshobj.GetMeshObject(), iSpriteCal3DState)
		# check for meshselect
		#self.select = celGetMeshSelect(celEntity)
		#if not self.select:
		#	self.select = celCreateMeshSelect(physicallayer_ptr,celEntity)
		# check for linmove
		#self.linmove = celGetLinearMovement(celEntity)
		#if not self.linmove:
		#	self.linmove = celCreateLinearMovement(physicallayer_ptr,celEntity)
		# check for tooltip
		self.tooltip = celGetToolTip(celEntity)
		if not self.tooltip:
			self.tooltip = celCreateToolTip(physicallayer_ptr,celEntity)
		# set some default parameters
		#self.camera.SetModeName ("thirdperson")
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
		input.Bind("left", "rotateleft")
		input.Bind("right", "rotateright")
		input.Bind("a", "strafeleft")
		input.Bind("d", "straferight")
		input.Bind("pgup", "lookup")
		input.Bind("pgdn", "lookdown")
		input.Bind("m", "cammode")
	
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

	# LOOK UP AND DOWN
	def pccommandinput_lookup1(self,celEntity,args):
		self.camera.SetPitchVelocity(1.0)

	def pccommandinput_lookup0(self,celEntity,args):
		self.camera.SetPitchVelocity(0.0)

	def pccommandinput_lookdown1(self,celEntity,args):
		self.camera.SetPitchVelocity(-1.0)

	def pccommandinput_lookdown0(self,celEntity,args):
		self.camera.SetPitchVelocity(0.0)

	# CAMERA MODES
	def pccommandinput_cammode1(self,celEntity,args):
		self.camera.SetMode(self.camera.GetNextMode ())

