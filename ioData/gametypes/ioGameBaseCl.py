from pycel import *
import random
import cPickle

import Menu
import ioNetHelper

class ioGameBaseCl:
    api_version = 2
    
    def __init__(self, celEntity):
        self.entity = celEntity
        self.client = Entities['ioCl']
        self.playername = Config.GetStr('Outlaws.Player.Name')
        #The entity to create to show stats when the game is over
        self.statsent = 'ioStatsBase'
        self.players = {}

        #We don't want to show until asked
        self.visible = False
        
        self.net = ioNetHelper.ioNetHelper()
        
        self.net.sendData('ioGmTp', 'getplayers', [])
        
        #Used to log messages
        self.netgamecl = Entities['ioNetMgrCl']
        
        self.kmessage = celAddBillboard(self.entity)
        self.kmessage.text_font_size = Menu.GetFontConstant() * 2.5
        self.kmessage.text_font = '/outlaws/fonts/lcd2.ttf'

    #We got the full list of players from the server
    def r_players(self, pc, args):
        addr, data = self.net.getNetData(args)
        for player in data:
            name = player[0]
            stats = player[1]
            self.players[name] = stats
            self.addPlayerDisp(name, stats)

    #A player has joined the game.
    def r_addplayer(self, pc, args):
        addr, data = self.net.getNetData(args)
        player, stats = data
        pars = parblock({'message' : '%s joined the game' % player})
        self.netgamecl.Behaviour.SendMessage('logevent', None, pars)
        if not self.players.has_key(player):
            self.players[player] = stats
            self.addPlayerDisp(player, stats)
            self.sortDisps()
  
    #Remove a player
    def r_popplayer(self, pc, args):
        addr, data = self.net.getNetData(args)
        player = data[0]
        pars = parblock({'message' : '%s left the game' % player})
        self.netgamecl.Behaviour.SendMessage('logevent', None, pars)
        if self.players.has_key(player):
            del self.players[player]
            self.popPlayerDisp(player)
            self.sortDisps()
        
    def destruct(self, pc, args):
        self.entity.PropertyClassList.RemoveAll()

    def authok(self, pc, args):
        pass
    
    def setvisible(self, pc, args):
        self.visible = args[parid('visible')]
                
    #Player kills another player
    def r_kl(self, pc, args):
        pass
                
    def addPlayerDisp(self, player, stats):
        pass
    
    def popPlayerDisp(self, player):
        pass
    
    def sortDisps(self):
        pass
    
    #Pick a start point for the player, and move them there
    def positionplayer(self, pc, args):
        entity = args[getid('cel.parameter.entity')]
        lastplayer = len(self.players)
        startnum = lastplayer % Engine.GetCameraPositions().GetCount()
        startpos = Engine.GetCameraPositions ().Get (startnum).GetPosition()
        celMechanicsObject(entity).GetBody().SetPosition(startpos)
    
    #Game is over due to conditions met in gametype
    def r_gov(self, pc, args):
        #Hide the hud
        pars = parblock({'visible' : False})
        hud = Entities['ioHUD']
        if hud:
            hud.Behaviour.SendMessage('setvisible', None, pars)
        #Hide us
        self.entity.Behaviour.SendMessage('setvisible', None, pars)
        stats = CreateEntity(self.statsent, BehaviourLayers['blpython'], self.statsent)
        pars = parblock({'stats' : cPickle.dumps(self.players)})
        stats.Behaviour.SendMessage('fillstats', None, pars)
        
    #Show the message, you killed someone
    def killmessage(self, premessage, killed):
        self.kmessage.x = -200000
        self.kmessage.y = 80000
            
        self.kmessage.Billboard.MoveToPosition(1000, 20000, 80000) 
        self.kmessage.text = '%s %s' % (premessage, killed)
        timer = celTimer(self.entity)
        timer.WakeUp(4000, False)
        
    #Destroy the killed message
    def pctimer_wakeup(self, pc, args):
        self.kmessage.Billboard.MoveToPosition(1000, -200000, 80000) 