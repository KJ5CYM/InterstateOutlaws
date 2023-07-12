from pycel import *
import ioLoader
class ioNetGameServer:
    api_version = 2
    
    def __init__(self, celEntity):
        self.entity = celEntity
        self.mapname = ''
        
        ioLoader.loadLibraryFolder('effects')
        ioLoader.loadWorldFolder('weapons', True)
        ioLoader.loadWorldFolder('vehicles', True)
        ioLoader.loadWorldFolder('entities', True)

    def clientadd(self, pc, args):
        pass

    def clientpop(self, pc, args):
        pass
    
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
        
    def setmapname(self, pc, args):
        self.mapname = args[getid('cel.parameter.name')]
        mapinfo = ioLoader.findSubfolderCfgString('maps', self.mapname)
        gameworld = ioLoader.makeGameWorld(mapinfo['Path'])
        Engine.PrecacheDraw()
        zonemgr = celZoneManager(gameworld)
        start = zonemgr.GetLastStartName()
        cam = celDefaultCamera(gameworld)
        cam.PointCamera(start)
        pars = celGenericParameterBlock(0)
        print 'server ready'