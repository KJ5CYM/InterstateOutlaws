# an example dummy behaviour (for a billboard)
from cspace import *
from blcelc import *

class dummy:
	def __init__(self,celEntity):
		print "Initializing dummy..."
	def real_init(self,celEntity,room):
		pass
	def pcbillboard_select(self,celEntity,args):
		print "bill select"
	def pcbillboard_move(self,celEntity,args):
		print "bill select"
