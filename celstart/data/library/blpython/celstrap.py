#! BLCEL
# A behaviour that can be run from bootstrap and receives
# the world as a parameter from the command line.

# It is intended for zipping with the world and then running
# as follows:
#
# export PYTHONPATH=_full_path_to_zipfile_.zip
# $(CEL)/bootstrap cel.behaviourlayer.python celstrap load _full_path_to_world_.zip
# 
# although it can also run if celstrap.py and all other scripts are
# in the pythonpath (for example ($PWD)/scripts/)

# Usually you won't need to touch this file, but it is as easy to add
# new functionality to it.
# The file needs to evolve
# XXX for now it looks for a player called "camera", and level file level.xml.

from cspace import *
from blcelc import *

# This is the list of property classes the app is registering.
# Add any new ones here.

pcclasses = ["region","tooltip","mesh","solid","meshselect","test","zonemanager","trigger","quest","light","inventory","defaultcamera","gravity","movable","pccommandinput","linmove","actormove","colldet","timer","mechsys","mechobject","soundlistener","soundsource","billboard","properties","hover","craft","mechjoint"]

# The class that implements the main application behaviour.
# if you want to make your own just copy it and set the same name for
# the file as for the class. ie: celstrap.py has class celstrap.

# To use this the player must have a camera property class and must be 
# called "camera" :(. Have to find a better way to manage the player.

class celstrap:
	def __init__(self,celEntity):
		# XXX ugly hardcoded name for the player
		self.playername="camera"
		print "Initializing game..."
		self.entity=celEntity
		# Register property classes
		for pcclass in pcclasses:
			celRegisterPCFactory(object_reg_ptr,"cel.pcfactory."+pcclass)
		# Initialize app entity
		self.entity = celEntity
		self.input = celCreateCommandInput(physicallayer_ptr,self.entity)
		self.input.Bind("r", "restart")
		self.input.Bind("i", "startrecord")
		self.input.Bind("o", "stoprecord")
		self.input.Bind("p", "pauserecord")
		
		# load the movierecorder
		self.mr = CS_QUERY_REGISTRY(object_reg_ptr,iMovieRecorder)
		if not self.mr:
			plugmgr = CS_QUERY_REGISTRY(object_reg_ptr,iPluginManager)
			self.mr = CS_LOAD_PLUGIN (plugmgr, "crystalspace.utilities.movierecorder",iMovieRecorder)
			if self.mr:
				object_reg_ptr.Register (self.mr, "iMovieRecorder")
			else:
				self.mr = None
		# check for tooltip
		self.logs=[]


		# Load dynamics plugin (in case we want to use physics)
		# otherwise this call can be commented
		self.loadDynamics()
		
		# the zone manager entity
		# XXX this should not be necessary
		self.game_entity=celCreateEntity(physicallayer_ptr,"room")

		# create the tooltip for logs
		self.createTooltip()

	def loadDynamics(self):
		# load dynamics plugin, as for now cs physics loader doesn't
		# do it for us
		plugmgr = CS_QUERY_REGISTRY(object_reg_ptr,iPluginManager)
		dynamics = CS_LOAD_PLUGIN (plugmgr, "crystalspace.dynamics.ode",
		        iDynamics)
		if dynamics:
			object_reg_ptr.Register (dynamics, "iDynamics")

	

	# TODO this way to load the map is not very nice, but
	# it is the same celtest uses, i don't know about
	# doing it better
	def createTooltip(self):
		self.tooltip = celCreateToolTip(physicallayer_ptr,self.entity)
		self.tooltip.SetBackgroundColor(-1,-1,-1)
		self.tooltip.SetTextColor(255,255,255)
		self.tooltip.Show(20,20)
		self.log_event("celstrap started")
		self.log_event("i: start record")
		self.log_event("o: stop record")
		self.log_event("p: pause record")
		self.log_event("r: restart")

	def loadMap(self,map_file):
		# create an initial environment to load the map
		zoneManager = celCreateZoneManager(physicallayer_ptr,self.game_entity)
		zoneManager.Load("/celstrap/","level.xml")
		
		# the map won't load until we put a dummy camera into
		# the region
		dummy = celCreateEntity(physicallayer_ptr,"dcamera")
		dummy_cam = celCreateDefaultCamera(physicallayer_ptr,dummy)
		self.startregion=zoneManager.GetLastStartRegionName()
		self.startname=zoneManager.GetLastStartName()
		dummy_cam.SetZoneManager(zoneManager,True,self.startregion,"")
		
		# now the map is loaded we want to find the real
		# player entity and do some setup.
		actor = physicallayer_ptr.FindEntity(self.playername)

		# get actor region and dissociate from it
		engine= CS_QUERY_REGISTRY(object_reg_ptr,iEngine)
		regions=engine.GetRegions()
		i=0
		# default region name
		# find the actor region based on mesh, and dissociate player
		# from regions (so it can move freely).
		mesh=celGetMesh(actor).GetMesh()
		while(i<regions.GetCount ()):
			# XXX it is currently not possible to directly test
			# if an entity is associated to a region.
			# (so test the mesh wrapper against cs region)
			if mesh and regions.Get(i).IsInRegion(mesh.QueryObject ()):
				self.startregion = regions.Get(i).QueryObject().GetName()
				regions.Get(i).Remove(mesh.QueryObject ())
				regions.Get(i).Remove(mesh.GetFactory().QueryObject ())
				celregion=zoneManager.FindRegion(self.startregion)
				celregion.DissociateEntity(actor)
			i=i+1
		if mesh:
			zoneManager.PointMesh(self.playername,self.startregion,self.startname)
		else:
			zoneManager.PointCamera(self.playername,self.startregion,self.startname)

		# kill the dummy camera
		# XXX removing property classes IS important before
		# removing them from the physical layer
		dummy.GetPropertyClassList().RemoveAll()
		physicallayer_ptr.RemoveEntity(dummy)
		
	def unloadMap(self):
		# reassociate the player with its region
		actor = physicallayer_ptr.FindEntity(self.playername)
		zoneManager=celGetZoneManager(self.game_entity)
		celregion=zoneManager.FindRegion(self.startregion)
		if actor:
			celregion.AssociateEntity(actor)
			# reassociate with the engine region
			mesh=celGetMesh(actor).GetMesh()
			if mesh:
				engine= CS_QUERY_REGISTRY(object_reg_ptr,iEngine)
				region=engine.GetRegions().FindByName(self.startregion)
				region.Add(mesh.QueryObject ())
				region.Add(mesh.GetFactory().QueryObject ())
		# this removes the zone manager
		self.game_entity.GetPropertyClassList().RemoveAll()

	# Restart command
	# XXX this still fails to restart correctly on some maps
	def pccommandinput_restart1(self,celEntity,args):
		self.unloadMap()
		self.loadMap(self.map)
		self.logs=[]
		self.log_event("map restarted")
	def pccommandinput_restart0(self,celEntity,args):
		pass
	def pccommandinput_restart_(self,celEntity,args):
		pass
	
	# video record commands
	def pccommandinput_startrecord1(self,celEntity,args):
		self.log_event("start recording")
		if self.mr:
			self.mr.Start()
	def pccommandinput_stoprecord1(self,celEntity,args):
		self.log_event("stop recording")
		if self.mr:
			self.mr.Stop()
	def pccommandinput_pauserecord1(self,celEntity,args):
		if self.mr:
			if self.mr.IsPaused():
				self.log_event("unpause recording")
				self.mr.UnPause()
			else:
				self.log_event("pause recording")
				self.mr.Pause()
	def log_event(self,event):
		self.logs.append(event)
		if len(self.logs) > 5:
			self.logs.pop(0)
		tooltip_text="\n".join(self.logs)
		self.tooltip.Show(20,20)
		self.tooltip.SetText(tooltip_text)

	# starting command, here we can pass map name, player name...
	def load(self,celEntity,args):
		# mount the file at some path in vfs
		self.map = args.GetParameterValue(physicallayer_ptr.FetchStringID ("cel.parameter.parameter1"))
		vfs=CS_QUERY_REGISTRY(object_reg_ptr,iVFS)
		vfs.Mount("/celstrap",self.map)
		vfs.ChDirAuto("/celstrap/");
		self.loadMap(self.map)
	
