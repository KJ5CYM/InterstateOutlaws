from pycel import *
class ioSplashScreen:
    #A splash screen
    api_version = 2
    def __init__(self, celEntity):
        self.entity = celEntity
        self.blpython = BehaviourLayers['blpython']
        
        bg = celAddBillboard(self.entity)
        bg.materialnamefast = 'blackbg'
        bg.width = 307200
        bg.height = 307200
        bg.x = 0
        bg.y = 0
        
        #Splash screen
        splashscreen = celAddBillboard(self.entity)
        splashscreen.materialnamefast = 'titleback'
        splashscreen.width = 307200
        splashscreen.height = 207200
        splashscreen.x = 0
        splashscreen.y = 30000
    
    #Destroy on a timer event
    def pctimer_wakeup(self, pc, args):
        RemoveEntity(self.entity)

    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
