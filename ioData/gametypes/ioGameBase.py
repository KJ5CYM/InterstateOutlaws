from pycel import *
import cPickle
import ioNetHelper

class ioGameBase:
    api_version = 2
    
    def __init__(self, celEntity):
        self.entity = celEntity
        self.players = {}
        self.gsrv = Entities['ioGSrv']
        self.maxscore = 0
        self.gameover = False
        
        timer = celTimer(self.entity)
        timer.WakeUp(250, True)
        #When a player dies, we add it to the spawnlist. Once the respawn time has passed,
        #we tell it to respaen
        self.respawntime = 10000
        self.ticks = Clock.GetCurrentTicks()
        self.spawnwatches = {}
        
        self.net = ioNetHelper.ioNetHelper()
    
    #Run through all watched dead players, and see if they are able to respawn
    def pctimer_wakeup(self, pc, args):
        for player, deathtime in self.spawnwatches.copy().iteritems():
            if (Clock.GetCurrentTicks() - deathtime) >= self.respawntime:
                entity = Entities[player]
                if entity:
                    entity.Behaviour.SendMessage('respawn', None, args)
                del self.spawnwatches[player]
    
    #A player is added to the game. Tell all clients, and make a new slot
    def addentity(self, pc, args):
        name = args[getid('cel.parameter.name')]
        self.addPlayer(name)
        data = [name, self.players[name]]
        self.net.sendToClients('ioGmTpCl', 'addplayer', data)
    
    #Make a new slot for a player. This is overridden by the specific gametype
    def addPlayer(self, name):
        self.players[name] = []

    #A gametype client needs to know existing players when it joins the game
    def r_getplayers(self, pc, args):
        addr = self.net.getNetData(args)[0]
        self.net.sendData('ioGmTpCl', 'players', self.players.items(), addr)

    #Remove a player from the game, if they got that far
    def clientpop(self, pc, args):
        name = args[getid('cel.parameter.name')]
        if self.players.has_key(name):
            self.net.sendToClients('ioGmTpCl', 'popplayer', [name])
            del self.players[name]
    
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()
    
    #A player is killed. Add a spawnwatch
    def playerkilled(self, pc, args):
        killedby = args[getid('cel.parameter.killedby')]
        killed = args[getid('cel.parameter.killed')]
        self.spawnwatches[killed] = Clock.GetCurrentTicks()
    
    #Work out a suitable position for a new player
    def positionplayer(self, pc, args):
        entity = args[getid('cel.parameter.entity')]
        lastplayer = len(self.players)
        startnum = lastplayer % Engine.GetCameraPositions().GetCount()
        startpos = Engine.GetCameraPositions ().Get (startnum).GetPosition()
        celMechanicsObject(entity).GetBody().SetPosition(startpos)
    
    #Server sends us the max score
    def setmaxscore(self, pc, args):
        self.maxscore = args[getid('cel.parameter.score')]
    
    #Tell all clients the game is over
    def endGame(self):
        if not self.gameover:
            self.gameover = True
            self.net.sendToClients('ioGmTpCl', 'gov', [])