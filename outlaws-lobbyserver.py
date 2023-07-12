#!/usr/bin/env python
import os
import sys
import subprocess
import ioBaseInit

paths = ['ioData/menus', 'ioData/hud', 'ioData/weapons', 'ioData/entities', 'ioData/vehicles', 'ioData/gametypes', 'ioData/scripts', 'ioData/server']
ioBaseInit.pathInit(paths)
 
#Start the game!
command = os.path.normpath(ioBaseInit.getCelstart())
path = 'ioData/server/lobby/celstart.cfg'
subprocess.call([command, path] + sys.argv[1:])