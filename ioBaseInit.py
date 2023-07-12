#!/usr/bin/env python
import os
import sys

def getCelstart():
    celstartPath = 'celstart'
    #First look for celstart in $CEL
    if os.environ.has_key('CEL'):
        celstartPath = checkCelstart(os.environ['CEL'])
    #Try checking the 'celstart' subfolder if we haven't found matches yet
    if celstartPath == 'celstart':
        celstartPath = checkCelstart(os.path.abspath(os.getcwd() + '/celstart'))
    return celstartPath

#Given a folder, check if celstart exists within it. If so, add it to PYTHONPATH
#And return the full path to the celstart exec
def checkCelstart(path):
    try:
        files = os.listdir(path)
    except:
        return 'celstart'
    searchlist = ['celstart', 'celstart.exe', 'celstart_static', 'celstart_static.exe']
    execs = filter((lambda n: n in files), searchlist)
    #There was at least 1 match
    if len(execs) > 0:
        os.environ['PYTHONPATH'] += os.path.pathsep + path
        #Use the first available match
        return os.path.normpath(path + '/' + execs[0])
    #Else we rely on $PATH
    else:
        print "Warning - couldn't find celstart anywhere around here, though the game may still run"
        return 'celstart'
    

def pathInit(paths):
    path, scriptname = os.path.split(sys.argv[0])
    path = os.path.abspath(path)
    os.chdir(path)
    os.environ['PYTHONPATH'] = path
    #Add crystal dir to pythonpath
    if os.environ.has_key('CRYSTAL'):
        path = os.environ['CRYSTAL']
        os.environ['PYTHONPATH'] += os.path.pathsep + path
    for path in paths:
        addPath(path)
        
#Add a folder and all it's subfolders to PYTHONPATH
def addPath(path):
    pathok = True
    try:
        root, dirs, files = os.walk(os.path.normpath(path)).next()
    except StopIteration:
        pathok = False
    if pathok:
        os.environ['PYTHONPATH'] += os.path.pathsep + root
        for dir in dirs:
            if '.' not in dir:
                os.environ['PYTHONPATH']+=os.path.pathsep+os.path.join(root,dir)
