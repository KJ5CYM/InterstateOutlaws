# a behaviour for an actor ball that can be controlled by applying force
# it is a good start for playing with physics
# uses: mechanicsobject, defaultcamera, tooltip, commandinput

# it also prints a time out in the tooltip as an example.

from cspace import *
from blcelc import *

class actorball:
	def __init__(self,celEntity):
		print "Initializing actor..."
		# the timeout counter
		self.counter = 60
		# movement variables
		self.forward = 0
		self.side = 0
		# make sure we have a tooltip
		self.tooltip = celGetToolTip(celEntity)
		if not self.tooltip:
			self.tooltip = celCreateToolTip(physicallayer_ptr,celEntity)
		# make sure we have a pcdefaultcamera
		self.camera = celGetDefaultCamera(celEntity)
		if not self.camera:
			self.camera = celCreateDefaultCamera(physicallayer_ptr,celEntity)
		# get a virtualclock interface to count time
		self.myClock = CS_QUERY_REGISTRY (object_reg_ptr, iVirtualClock)
		self.time = self.myClock.GetCurrentTicks()

		# get a mechanics object
		self.meshobject = celGetMechanicsObject(celEntity)

		# make sure we have a pccommandinput
		input = celGetCommandInput(celEntity)
		if not input:
			input = celCreateCommandInput(physicallayer_ptr,celEntity)
		# set default camera mode
		self.camera.SetModeName ("lara_thirdperson")
		# bind inputs
		input.Bind("up", "forward")
		input.Bind("down", "backward")
		input.Bind("a", "lookup")
		input.Bind("z", "lookdown")
		input.Bind("m", "cammode")
		input.Bind(" ", "jump")
		input.Bind("left", "forteleft")
		input.Bind("right", "forteright")
	
	# TRIGGER CALLBACKS
	def pctrigger_leavetrigger(self,celEntity,args):
		pass
	def pctrigger_entertrigger(self,celEntity,args):
		pass
	# INVENTORY CALLBACK
	def pcinventory_addchild(self,celEntity,args):
		pass
	# TIMER CALLBACKS
	def pctimer_wakeupframe(self,celEntity,args):
		g2d=CS_QUERY_REGISTRY(object_reg_ptr,iGraphics2D)
		if self.counter > 0:
			self.tooltip.SetText("remaining time:"+str(self.counter))
		else:
			self.tooltip.SetText("GAME OVER")
		newtime = self.myClock.GetCurrentTicks()
		if self.forward:
			self.meshobject.AddForceFrame(csVector3(0,0,self.forward*20),False,csVector3(0,0,0))
		if self.side:
			self.meshobject.AddForceFrame(csVector3(self.side*20,0,0), False,csVector3(0,0,0))
	
	# LOOK UP/DOWN
	def pccommandinput_lookup1(self,celEntity,args):
		self.camera.SetPitchVelocity(1.0)

	def pccommandinput_lookup0(self,celEntity,args):
		self.camera.SetPitchVelocity(0.0)
	def pccommandinput_lookup_(self,celEntity,args):
		pass

	def pccommandinput_lookdown1(self,celEntity,args):
		self.camera.SetPitchVelocity(-1.0)
	def pccommandinput_lookdown0(self,celEntity,args):
		self.camera.SetPitchVelocity(0.0)
	def pccommandinput_lookdown_(self,celEntity,args):
		pass

	#JUMP
	def pccommandinput_jump1(self,celEntity,args):
		newtime = self.myClock.GetCurrentTicks()
		# this try to apply the force only if the object is not
		# touching the ground
		if newtime - self.time > -100:
			self.meshobject.AddForceOnce(csVector3(0,3000,0),False,csVector3(0,0,0))
		self.time = newtime
	def pccommandinput_jump0(self,celEntity,args):
		pass
	def pccommandinput_jump_(self,celEntity,args):
		pass
	# MOVEMENT
	def pccommandinput_forteleft1(self,celEntity,args):
		self.side = 1
	def pccommandinput_forteleft0(self,celEntity,args):
		self.side = 0
	def pccommandinput_forteleft_(self,celEntity,args):
		pass
	def pccommandinput_forteright1(self,celEntity,args):
		self.side = -1
	def pccommandinput_forteright0(self,celEntity,args):
		self.side = 0
	
	def pccommandinput_forteright_(self,celEntity,args):
		pass
	def pccommandinput_forward1(self,celEntity,args):
		self.forward = -1
	def pccommandinput_forward0(self,celEntity,args):
		self.forward = 0
	def pccommandinput_forward_(self,celEntity,args):
		pass
	def pccommandinput_backward1(self,celEntity,args):
		self.forward = 1.4
	def pccommandinput_backward0(self,celEntity,args):
		self.forward = 0
	def pccommandinput_backward_(self,celEntity,args):
		pass
	# CAMERA MODES
	def pccommandinput_cammode1(self,celEntity,args):
		self.camera.SetMode(self.camera.GetNextMode ())

	# COLLISION CALLBACK
	# all pcmechanicobjects have this
	def pcdynamicbody_collision(self,celEntity,args):
		newtime = self.myClock.GetCurrentTicks()
		self.time = newtime

