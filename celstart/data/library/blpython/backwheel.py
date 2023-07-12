# Python behaviour that can be used as a base to control back wheel from some
# vehicle.
# Uses: commandinput,mechanicsobject,mechanicsjoint, mesh

from cspace import *
from blcelc import *

class backwheel:
	# INITIALIZATION
	def __init__(self,celEntity):
		print "Initializing wheel..."
		# check for mechanics object
		self.mech = celGetMechanicsObject(celEntity)
		if not self.mech:
			print "No mesh!"
		# check for mechanics joint
		# check for mesh
		self.mesh = celGetMesh(celEntity)
		if not self.mesh:
			print "No mesh!"
		self.mechjoint = celGetMechanicsJoint(celEntity)
		if not self.mechjoint:
			print "No joint!"
		self.joint = self.mechjoint.GetJoint()
		# check for pcdefaultcamera
                self.input = celGetCommandInput(celEntity)
                if not self.input:
                        self.input = celCreateCommandInput(physicallayer_ptr,celEntity)
		self.myjoint = SCF_QUERY_INTERFACE(self.joint,iODEJointState)
		self.myjoint.SetHinge2Axis1(csVector3(0,1,0))
		self.myjoint.SetHinge2Axis2(csVector3(1,0,0))
		self.myjoint.SetSuspensionCFM(0.0000)
		self.myjoint.SetSuspensionCFM2(0)
		self.myjoint.SetBounce(0.5)
		self.myjoint.SetBounce2(0.5)
		self.myjoint.SetSuspensionERP(0.3)
		self.myjoint.SetSuspensionERP2(0)
		self.myjoint.SetStopERP(0.3)
		self.myjoint.SetStopERP2(0)
		self.myjoint.SetFMax(100)
		self.myjoint.SetFMax2(1)
		#self.myjoint.SetCFM(0)
		#self.myjoint.SetCFM2(0.99)
		# bind some keys
		self.input.Bind("w", "forward")
		self.input.Bind("x", "backward")
		self.GearForce=[]
		self.GearVel=[]
		self.GearForce.append(1000)
		self.GearVel.append(40)
		self.center_wheel()
	
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
		self.accelerate(0)
	def pccommandinput_forward0(self,celentity,args):
		self.roll()
		pass
	def pccommandinput_forward_(self,celentity,args):
		self.accelerate(0)
		pass
	def pccommandinput_backward1(self,celEntity,args):
		self.brake()
			
	def pccommandinput_backward0(self,celEntity,args):
		self.roll()
		pass
	def pccommandinput_backward_(self,celentity,args):
		pass
	def pcdynamicbody_collision(self,celentity,args):
		pass
        def roll(self):
                self.myjoint.SetFMax2(100)
                self.myjoint.SetFMax(1)
                self.myjoint.SetVel2(1)
                self.myjoint.SetVel(1)

	# ROTATE
	def brake(self):
		#self.myjoint.SetFMax(1)
		#self.myjoint.SetFMax2(1000)
		#self.myjoint.SetVel(1)
		#self.myjoint.SetVel2(0)
		gear=0
		self.myjoint.SetFMax2(self.GearForce[gear])
		self.myjoint.SetVel2(self.GearVel[gear])
	def accelerate(self,gear):
		self.myjoint.SetFMax2(self.GearForce[gear])
		self.myjoint.SetVel2(-self.GearVel[gear])
	def center_wheel(self):
		self.myjoint.SetLoStop(0.0)
		self.myjoint.SetLoStop2(0.0)
		self.myjoint.SetHiStop(0.0)
		self.myjoint.SetHiStop2(0.0)
	def rotate_wheel(self,value,vel):
		self.myjoint.SetLoStop(-value)
		self.myjoint.SetLoStop2(0)
		self.myjoint.SetHiStop(value)
		self.myjoint.SetHiStop2(0)
		self.myjoint.SetVel(vel)
		self.myjoint.SetVel2(1)
		self.myjoint.SetFMax(1000)
		self.myjoint.SetFMax2(1)

	def pccommandinput_rotateleft1(self,celEntity,args):
		self.rotate_wheel(0.45,5)
	def pccommandinput_rotateleft0(self,celEntity,args):
		self.center_wheel()
	def pccommandinput_rotateleft_(self,celentity,args):
		pass
	def pccommandinput_rotateright1(self,celEntity,args):
		self.rotate_wheel(0.45,-5)
	def pccommandinput_rotateright0(self,celEntity,args):
		self.center_wheel()
	def pccommandinput_rotateright_(self,celentity,args):
		pass

	# TRIGGER CALLBACKS
	# you will receive this callbacks when the entity enters
	# or leaves triggers.
	def pctrigger_entertrigger(self,celEntity,args):
		pass
	def pctrigger_leavetrigger(self,celEntity,args):
		pass

