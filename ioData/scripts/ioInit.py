from pycel import *
import signal
import os
import socket

import ioDataBin

#Any celstart app importing ioInit will now quit on control + C
def exitapp(signal, frame):
    exitgame()
    
def exitgame():
    q = CS_QUERY_REGISTRY (oreg, iEventQueue)
    if q:
        q.GetEventOutlet().Broadcast (csevQuit (oreg))
        
signal.signal(signal.SIGINT, exitapp)
signal.signal(signal.SIGTERM, exitapp)

# This is the list of property classes the app is registering.
# Add any new ones here.
pcclasses = ['tooltip', 'mesh', 'zonemanager', 'inventory', 'defaultcamera', 'pccommandinput', 'timer', 'mechsys', 'mechobject', 'soundlistener', 'soundsource', 'billboard', 'properties', 'characteristics', 'wheeled', 'projectile', 'damage']
def registerclasses():
    # Register property classes
    #for pcclass in pcclasses:
    #    celRegisterPCFactory(oreg, 'cel.pcfactory.'+pcclass)

    #Load mounts using zone manager
    zonemgr = celZoneManager(CreateEntity('iomountsholder', None, None))
    zonemgr.SetLoadingMode(CEL_ZONE_LOADALL)
    zonemgr.Load('/this', 'mounts.xml')

# The class that implements the main application behaviour.
# if you want to make your own just copy it and set the same name for
# the file as for the class. ie: celstrap.py has class celstrap.

# To use this the player must have a camera property class and must be 
# called 'camera' :(. Have to find a better way to manage the player.

class ioInit:
    api_version = 2
    def __init__(self,celEntity):
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']
        # Initialize app entity
        self.entity = celEntity
        registerclasses()

        #Make the net client which contains our socket
        CreateEntity('ioNetClient', self.blpython, 'ioNetClient')
	
        #Stop the app from hanging too long if the network is down
        socket.setdefaulttimeout(10)

        Vfs.ChDir('/outlaws/menus')
        Loader.LoadMapFile('/outlaws/menus/world', False)
        
        #Create the splash screen, then precache after a frame is drawn
        self.splash = CreateEntity('ioSplashScreen', self.blpython, 'ioSplashScreen')
        self.timer = celTimer(self.entity)
        self.timer.WakeUpFrame(2)
        self.frames = 0
        
    #This is only started after a frame
    def maininit(self):
        Engine.PrecacheDraw()
        RemoveEntity(self.splash)
        CreateEntity('ioAutoUpdater', self.blpython, 'ioAutoUpdater')
    
    #Signalled that the updater is done
    #Make either the main menu or the garage (if first run)
    def updatecomplete(self, pc, args):
        #If we haven't visited the garage before, do it now.
        visitedgarage = Config.GetBool('Outlaws.Garage.Visited', False)
        if not visitedgarage:
            ioDataBin.Store('lastmenu', ('ioMainMenu', 'ioMainMenu'), True)
            CreateEntity('ioGarage', self.blpython, 'ioGarage')
        else:
            CreateEntity('ioMainMenu', self.blpython, 'ioMainMenu')
        
    ##Creates the splash screen while we precache. we keep it until the updater is finished
    #def precache(self):
        
        #self.frames = 0
        #self.timer = celTimer(self.entity)
        #self.timer.WakeUpFrame(2)

    # This hack makes sure the splashscreen is drawn before we start doing stuff
    def pctimer_wakeupframe(self, pc, args):
        self.frames += 1
        if self.frames > 1:
            self.frames = 0
            self.timer.Clear()
            self.maininit()

    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
