#This isn't available in the updater
try:
    from pycel import *
except ImportError:
    pass
import os
#load a map,and create a new mechanics system.
def makeGameWorld(mappath):
    print 'loading map...'
    blpython = BehaviourLayers['blpython']
    #Now make physics if its not already done.
    mechsysent = Entities['ioMechSys']
    if mechsysent is None:
        mechsysent = CreateEntity('ioMechSys', blpython, None)
        mechsys = celCreateMechanicsSystem(physicallayer_ptr, mechsysent)
        dyn = mechsys.DynamicSystem
        osys = SCF_QUERY_INTERFACE (dyn, iODEDynamicSystemState)
        #osys.SetContactMaxCorrectingVel(0.5)
        #osys.SetCFM(0.00005)
        mechsys.EnableQuickStep ()
        mechsys.SetStepTime (0.015)
        dyn.SetRollingDampener(0.998)

    #Recreate the gameworld if it already exists. Easiest way to unload a map.
    gameworld = Entities['ioGameWorld']
    if gameworld:
        zonemgr = celZoneManager(gameworld)
        gameworld.PropertyClassList.RemoveAll()
        RemoveEntity(gameworld)

    gameworld = CreateEntity('ioGameWorld', blpython, None)

    camera = celDefaultCamera(gameworld)
    camera.ModeName = 'lara_thirdperson'
    camera.SetSpringParameters (10.0, 0.1, 0.01)
    camera.ModeName = 'm64_thirdperson'
    camera.SetSpringParameters (10.0, 0.1, 0.01)
    camera.ModeName = 'firstperson'
    camera.SetSpringParameters (10.0, 0.1, 0.01)
    camera.ModeName = 'thirdperson'
    camera.SetSpringParameters(7.5, 0.1, 0.2)

    camera.SetMinMaxCameraDistance(5, 10)
    camera.SetFirstPersonOffset (csVector3 (0, 1.25, 0))
    camera.SetThirdPersonOffset (csVector3 (0, 1.25, 0))

    zonemgr = celZoneManager(gameworld)
    vfspath = '/outlaws/ioData/' + mappath
    Vfs.ChDir(vfspath)
    zonemgr.Load(vfspath, 'level.xml')
    #Now load a foliage level depending on user setting
    region = zonemgr.FindRegion('ioMapRegion')
    if region:
        foliagemap = region.CreateMapFile()
        #Now load a foliage level depending on user setting
        foliagelevel = Config.GetStr('Outlaws.Settings.Video.Foliage', 'High')
        foliagelevel = foliagelevel.lower()
        if foliagelevel in ['low', 'high']:
            foliagemap.SetPath(vfspath)
            foliagemap.SetFile('foliage-' + foliagelevel)
    #region = zonemgr.GetLastStartRegionName()
    #start = zonemgr.GetLastStartName()
    #zonemgr.PointCamera('gameworld', region, start)
    zonemgr.SetLoadingMode(CEL_ZONE_LOADALL)
    Engine.Prepare()
    Engine.PrecacheDraw()
    print 'map loaded.'
    
    return gameworld

def unloadGameWorld():
    gameworld = pl.FindEntity('ioGameWorld')
    if gameworld:
        zonemgr = celZoneManager(gameworld)
        gameworld.PropertyClassList.RemoveAll()
        RemoveEntity(gameworld)
    
#This function scans a directory and loads all subfolders with world files
def loadWorldFolder(path, entities):
    norm = os.path.normpath('ioData/'+path)
    root, folders, files = os.walk(norm).next()
    for folder in folders:
        if '.' not in folder:
            fullpath = '/outlaws/ioData/' + path + '/' + folder
            Vfs.ChDir(fullpath)
            Loader.LoadMapFile(fullpath +'/world', False)
            if entities:
                Loader.LoadMapFile(fullpath +'/entities_world', False)
    print 'folder' + ' ' + path + ' loaded.'
    
#This function scans a directory and loads all subfolders with .xml files
def loadLibraryFolder(path):
    Vfs.ChDir('ioData/'+path)
    root, folders, files = os.walk('ioData/'+path).next()
    for file in files:
        if '.xml' in file:
            Loader.LoadLibraryFile('/outlaws/ioData/' + path + '/' + file)
    print 'folder' + ' ' + path + ' loaded.'

#Load all models of a vehicle. Returns a list of dictionaries with gathered info.
def scanModels(path):
    infos = []
    foldername = os.path.normpath('ioData/' + path + '/models')
    vfsname = 'ioData/' + path + '/models'
    hasmodels = False
    try:
        root, folders, files = os.walk(foldername).next()
        hasmodels = True
    #No subfolder 'models'
    except StopIteration:
        pass
    if hasmodels:
        for modelfile in files:
            if '.cfg' in modelfile:
                cfg = Config.AddDomain('/outlaws/' + vfsname + '/' + modelfile, Vfs, 1000)
                if cfg:
                    info = {}
                    info['Name'] = cfg.GetStr('Outlaws.Info.Name')
                    info['Weapons'] = {}
                    mounts = ['Front1', 'Front2', 'Roof1', 'Roof2', 'Side1', 'Side2', 'Rear1', 'Rear2']
                    for mount in mounts:
                        info['Weapons'][mount] = cfg.GetStr('Outlaws.Info.' + mount)
                    infos.append(info)
                    Config.RemoveDomain(cfg)
    return infos

#Auto-scanned directory list. Returns a list of dictionaries with all gathered info.
def scanDir(path):
    infos = []
    foldername = os.path.normpath('ioData/' + path)
    vfsname = 'ioData/' + path
    root, folders, files = os.walk(foldername).next()
    for folder in folders:
        if '.' not in folder:
            cfg = Config.AddDomain('/outlaws/' + vfsname + '/' + folder + '/info.cfg', Vfs, 1000)
            if cfg:
                iterator = cfg.Enumerate('Outlaws.Info.')
                info = {}
                if iterator:
                    while iterator.Next():
                        info[iterator.GetKey(True)] = iterator.GetStr()
                info['Path'] = path + '/' + folder
                infos.append(info)
                Config.RemoveDomain(cfg)
    return infos

#Find the configfile which contains a given string, out of a directory. Return a dictionary of the config file.
def findCfgString(path, string):
    foldername = os.path.normpath('ioData/' + path)
    vfspath = 'ioData/' + path
    root, folders, files = os.walk(foldername).next()
    found = False
    for file in files:
        if '.cfg' in file and not '~' in file:
            vfsname = '/outlaws/' + vfspath + '/' + file
            cfg = Config.AddDomain(vfsname, Vfs, 1000)
            if cfg:
                iterator = cfg.Enumerate('Outlaws.Info.')
                if iterator:
                    info = {}
                    while iterator.Next():
                        info[iterator.GetKey(True)] = iterator.GetStr()
                        if iterator.GetStr() == string:
                            found = True
                    if found:
                        info['Path'] = path
                        info['File'] = file
                        return info
                Config.RemoveDomain(cfg)
    return {}

#Same as above, but walks one level of folders.
def findSubfolderCfgString(path, string):
    foldername = os.path.normpath('ioData/' + path)
    root, folders, files = os.walk(foldername).next()
    for folder in folders:
        if '.' not in folder:
            info = findCfgString(path + '/' + folder, string)
            if info != {}:
                return info
    return {}

#Work through an ini-style file, sorting it into a dictionary
#Used for the versions list and the patch mechanism
def parsefile(data):
    keys = {}
    currentkey = 'Blank'
    for line in data.split('\n'):
        #A new key entry
        if line.startswith('['):
            currentkey = line[1:-1]
        else:
            #Append more data to the key we are working on
            if not keys.has_key(currentkey):
                keys[currentkey] = []
            if line != '':
                keys[currentkey].append(line.strip())
    return keys