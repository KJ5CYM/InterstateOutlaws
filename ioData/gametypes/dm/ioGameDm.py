from pycel import *
from ioGameBase import *
import ioNetHelper

class ioGameDm (ioGameBase):
    api_version = 2
    
    def __init__(self,celEntity):
        ioGameBase.__init__(self, celEntity)
        print 'deathmatch server started'

    def addPlayer(self, name):
        self.players[name] = [0]
        
    def playerkilled(self, pc, args):
        ioGameBase.playerkilled(self, pc, args)
        killedby = args[getid('cel.parameter.killedby')]
        killed = args[getid('cel.parameter.killed')]
        if self.players.has_key(killedby):
            self.players[killedby][0] += 1
            score = self.players[killedby][0]
            data = [killedby, killed, score]
            self.net.sendToClients('ioGmTpCl', 'kl', data)
            if (score >= self.maxscore) and (self.maxscore != 0):
                self.endGame()