from pycel import *
from ioGameBaseCl import *
import Menu
import ioNetHelper
import cPickle

class ioGameDmCl (ioGameBaseCl):
    api_version = 2
    
    def __init__(self,celEntity):
        ioGameBaseCl.__init__(self, celEntity)
        print 'deathmatch client started'
        self.statsent = 'ioDmStats'
        self.pdisps = {}
        self.fconst = Menu.GetFontConstant()
        self.basepos = (10000, 200000)
        self.bg = celAddBillboard(self.entity)
        self.bg.x = self.basepos[0]
        self.bg.y = self.basepos[1]
        self.bg.width = 40000
        self.bg.height = 100000
        self.bg.materialnamefast = 'half-black'
        self.bg.visible = self.visible
        
    def setvisible(self, pc, args):
        ioGameBaseCl.setvisible(self, pc, args)
        self.bg.visible = self.visible
        for bb in self.pdisps.itervalues():
            bb.visible = self.visible
  
    def addPlayerDisp(self, player, stats):
        bb = celAddBillboard(self.entity)
        self.pdisps[player] = bb
        bb.text_font_size = self.fconst
        bb.text_font = '/outlaws/fonts/lcd2.ttf'
        bb.text_fg_color = Menu.GetFontColor()
        bb.text = '%s  %s' % (player, stats[0])
        bb.visible = self.visible
        self.sortDisps()
        
    def popPlayerDisp(self, player):
        if self.pdisps.has_key(player):
            self.entity.PropertyClassList.Remove(self.pdisps[player])
            del self.pdisps[player]
        
    #Someone killed someone else
    def r_kl(self, pc, args):
        addr, data = self.net.getNetData(args)
        killedby, killed, score = data
        #If it was our player, that killed
        if killedby == self.playername:
            self.killmessage('You killed', killed)
        #Our player got killed
        elif killed == self.playername:
            self.killmessage('Killed by', killedby)
        self.players[killedby][0] = score
        self.pdisps[killedby].text = '%s  %d' % (killedby, score)
        pars = parblock({'message' : '%s was killed by %s' % (killed, killedby)})
        self.netgamecl.Behaviour.SendMessage('logevent', None, pars)
        self.sortDisps()
        
    #Sort the players by score. zips scores with player names and then sorts.
    def sortDisps(self):
        items = [(data[0], name) for name, data in self.players.iteritems()]
        sortedplayers = [item[1] for item in sorted(items, reverse = True)]
        for i, player in enumerate(sortedplayers):
            bb = self.pdisps.get(player)
            if bb:
                bb.x = self.basepos[0] + 2500
                bb.y = self.basepos[1] + (i + 1) * 10000
                
    def r_gov(self, pc, args):
        ioGameBaseCl.r_gov(self, pc, args)