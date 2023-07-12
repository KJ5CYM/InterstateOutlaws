# a behaviour for a trigger that changes camera mode
# on approaching. actorname is the name for entity that
# carries the camera
from cspace import *
from blcelc import *

actorname = "camera"

class camerachange:
	def __init__(self,celEntity):
		pass
	
	def pctrigger_entityenters(self,celEntity,args):
		actor = physicallayer_ptr.FindEntity(actorname)
		camera = celGetDefaultCamera(actor)
		self.prevcamera = camera.GetModeName()
		camera.SetModeName ("firstperson")
	def pctrigger_entityleaves(self,celEntity,args):
		actor = physicallayer_ptr.FindEntity(actorname)
		camera = celGetDefaultCamera(actor)
		camera.SetModeName (self.prevcamera)
